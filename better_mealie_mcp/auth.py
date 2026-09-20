"""Authentication for the MCP HTTP endpoint.

Turns FastMCP's ``auth=`` hook into a small resource server so that, when the
server runs over HTTP, every request to /mcp must authenticate. The
mechanisms are:

- ``key``       — a single pre-shared API key sent as ``Authorization: Bearer <key>``
- ``oauth``     — a built-in OAuth 2.1 authorization server (DCR + PKCE) so
  clients like ChatGPT and Claude can run their usual "sign in" connector
  flow; auto-approves every request, so only use on non-public URLs
- ``authentik`` — validate tokens issued by an external Authentik (OIDC)
  authorization server, so /mcp accepts only tokens Authentik actually issued
  to your users. Full RFC 9728 protected-resource metadata routes, no
  auto-approval.
- ``both``      — accept an Authentik OIDC token *or* the pre-shared API key
  (per-user logins for interactive clients, the key for scripts/services)

STDIO transport is unaffected (it inherits security from the local environment).
"""

from __future__ import annotations

import asyncio
import os
import secrets
import time
from typing import Any

import httpx
from fastmcp.server.auth import (
    AccessToken,
    AuthProvider,
    MultiAuth,
    RemoteAuthProvider,
    TokenVerifier,
)


class BearerTokenAuth(AuthProvider):
    """Require a single pre-shared bearer token (API key) on every request.

    The token is compared in constant time to avoid leaking it via timing.

    Setting ``base_url`` / ``resource_base_url`` is optional; omitted here so
    the provider only enforces the token and exposes no metadata routes.
    """

    def __init__(self, token: str) -> None:
        super().__init__()
        self.token = token

    async def verify_token(self, token: str) -> AccessToken | None:
        if not secrets.compare_digest(token, self.token):
            return None
        return AccessToken(
            token=token,
            client_id="mcp-client",
            subject="mcp-client",
            scopes=[],
        )


def _oauth_provider(public_url: str) -> AuthProvider:
    """Build a self-contained OAuth 2.1 authorization server.

    Uses FastMCP's in-memory provider: clients register dynamically (DCR) and
    the authorization step auto-approves, so no external identity provider is
    needed. Clients, tokens and refresh tokens live in process memory only —
    they are dropped on restart and clients simply re-authorize.

    .. warning::
        Auto-approval means anyone who can reach ``/authorize`` obtains a
        token. Only use this on a URL that is not publicly reachable, or front
        it with an identity provider. See the README.
    """
    from fastmcp.server.auth.auth import ClientRegistrationOptions
    from fastmcp.server.auth.providers.in_memory import InMemoryOAuthProvider

    return InMemoryOAuthProvider(
        base_url=public_url.rstrip("/"),
        client_registration_options=ClientRegistrationOptions(enabled=True),
    )


class AuthentikTokenVerifier(TokenVerifier):
    """Validate access tokens issued by an Authentik (OIDC) server.

    Fetches Authentik's OIDC discovery document to locate its JWKS, then
    validates the signature (RS256) plus ``exp`` / ``iss`` / ``aud`` / scopes
    of every access token — the server accepts **only** tokens Authentik
    actually issued, so access is tied to your Authentik users, not anyone who
    can reach the endpoint.

    Keys are cached with a short TTL and refreshed automatically on an unknown
    ``kid`` (key rotation). No network I/O happens until the first request is
    verified, so the server starts even while Authentik is briefly unreachable
    — requests just get 401 until the issuer can be contacted.
    """

    CACHE_TTL = 300.0  # seconds between OIDC discovery / JWKS refreshes

    def __init__(
        self,
        issuer: str,
        discovery_url: str | None = None,
        audience: str | None = None,
        required_scopes: list[str] | None = None,
    ) -> None:
        super().__init__(required_scopes=required_scopes)
        self.issuer = issuer.rstrip("/")
        self.discovery_url = discovery_url or (
            f"{self.issuer}/.well-known/openid-configuration"
        )
        self.audience = audience
        self.required_scopes = required_scopes or []
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(10.0))
        self._keyset: Any = None
        self._fetched_at: float = 0
        self._lock = asyncio.Lock()

    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            return await self._verify(token)
        except Exception:
            # A dangling Authentik failure must never crash the request handler.
            return None

    async def _verify(self, token: str) -> AccessToken | None:
        from joserfc import jwt

        await self._load_keys()
        try:
            decoded = jwt.decode(token, self._keyset, algorithms=["RS256"])
        except Exception:
            if self._keyset is None:
                return None
            # Unknown `kid` — likely key rotation behind the TTL. Refresh once
            # and give the token a single retry.
            await self._load_keys(force=True)
            if self._keyset is None:
                return None
            try:
                decoded = jwt.decode(token, self._keyset, algorithms=["RS256"])
            except Exception:
                return None

        now = time.time()
        payload = dict(decoded.claims)
        exp = payload.get("exp")
        if isinstance(exp, (int, float)) and exp < now - 15:
            return None
        iat = payload.get("iat")
        if isinstance(iat, (int, float)) and iat > now + 15:
            return None
        if str(payload.get("iss", "")).rstrip("/") != self.issuer:
            return None
        aud = payload.get("aud")
        if self.audience:
            actual = {aud} if isinstance(aud, str) else set(aud or [])
            if self.audience not in actual:
                return None
        scopes = str(payload.get("scope", "")).split()
        if self.required_scopes and not all(s in scopes for s in self.required_scopes):
            return None

        return AccessToken(
            token=token,
            client_id=str(aud) if isinstance(aud, str) else "",
            subject=str(payload.get("sub", "")),
            scopes=scopes,
            claims=payload,
        )

    async def _load_keys(self, force: bool = False) -> None:
        async with self._lock:
            if force or self._keyset is None or time.monotonic() - self._fetched_at > self.CACHE_TTL:
                await self._fetch_jwks()

    async def _fetch_jwks(self) -> None:
        from joserfc.jwk import KeySet, RSAKey

        doc = (await self._client.get(self.discovery_url)).raise_for_status().json()
        jwks_uri = doc.get("jwks_uri")
        keys: list[RSAKey] = []
        if jwks_uri:
            jwks = (await self._client.get(jwks_uri)).raise_for_status().json()
            for jwk in jwks.get("keys", []):
                try:
                    keys.append(RSAKey.import_key(jwk))
                except Exception:
                    continue  # skip unusable entries; keep what we can import
        self._keyset = KeySet(keys) if keys else None
        self._fetched_at = time.monotonic()


def _authentik_provider(public_url: str) -> AuthProvider:
    """Build an Authentik-backed resource server (RFC 9728).

    The server validates tokens issued by an external Authentik OIDC provider
    and advertises protected-resource metadata pointing at it, so spec-aware
    MCP clients discover Authentik from ``/.well-known/oauth-protected-resource``
    and run the real login there — no auto-approval.

    Env: ``MCP_AUTH_ISSUER`` (required), ``MCP_AUTH_AUDIENCE`` and
    ``MCP_AUTH_SCOPES`` (optional), ``MCP_AUTH_DISCOVERY_URL`` (optional).
    """
    issuer = os.environ.get("MCP_AUTH_ISSUER")
    if not issuer:
        raise SystemExit("MCP_AUTH_MODE='authentik' requires MCP_AUTH_ISSUER.")
    scopes = [
        s.strip()
        for s in os.environ.get("MCP_AUTH_SCOPES", "").split(",")
        if s.strip()
    ]
    return RemoteAuthProvider(
        token_verifier=AuthentikTokenVerifier(
            issuer=issuer,
            discovery_url=os.environ.get("MCP_AUTH_DISCOVERY_URL") or None,
            audience=os.environ.get("MCP_AUTH_AUDIENCE") or None,
            required_scopes=scopes or None,
        ),
        authorization_servers=[issuer],
        base_url=public_url.rstrip("/"),
    )


def build_auth() -> AuthProvider | None:
    """Build the HTTP auth provider from the environment.

    ``MCP_AUTH_MODE`` selects the mechanism (default ``none``):

    - ``none``      — no auth; open endpoint for trusted/local setups
    - ``key``       — require ``MCP_AUTH_TOKEN`` as ``Authorization: Bearer <token>``
    - ``oauth``     — run the built-in OAuth 2.1 authorization server (open,
      auto-approving; for clients that only speak OAuth)
    - ``authentik`` — validate OIDC access tokens issued by an external
      Authentik server (per-user access; no auto-approval)
    - ``both``      — accept an Authentik OIDC token *or* ``MCP_AUTH_TOKEN``

    ``oauth`` / ``authentik`` / ``both`` need ``MCP_PUBLIC_BASE_URL`` so
    discovery metadata and redirect URIs resolve correctly. ``authentik`` and
    ``both`` need ``MCP_AUTH_ISSUER``; ``key`` and ``both`` need
    ``MCP_AUTH_TOKEN``.
    """
    mode = os.environ.get("MCP_AUTH_MODE", "none").strip().lower()
    token = os.environ.get("MCP_AUTH_TOKEN")
    public_url = os.environ.get("MCP_PUBLIC_BASE_URL")

    if mode in ("none", "off", ""):
        return None
    if mode == "key":
        return BearerTokenAuth(token) if token else None
    if mode in ("authentik", "both"):
        if not public_url:
            raise SystemExit(f"MCP_AUTH_MODE={mode!r} requires MCP_PUBLIC_BASE_URL.")
        server = _authentik_provider(public_url)
        if mode == "authentik":
            return server
        if not token:
            raise SystemExit("MCP_AUTH_MODE='both' requires MCP_AUTH_TOKEN.")
        # The Authentik verifier still enforces scopes on real tokens; the API
        # key is exempt from the scope gate, so the outer middleware gets none.
        return MultiAuth(
            server=server,
            verifiers=[BearerTokenAuth(token)],
            required_scopes=[],
        )
    if mode != "oauth":
        raise SystemExit(
            f"Invalid MCP_AUTH_MODE={mode!r}. "
            "Use 'none', 'key', 'oauth', 'both' or 'authentik'."
        )
    if not public_url:
        raise SystemExit(f"MCP_AUTH_MODE={mode!r} requires MCP_PUBLIC_BASE_URL.")
    return _oauth_provider(public_url)
