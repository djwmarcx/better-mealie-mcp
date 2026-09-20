"""Authentication for the MCP HTTP endpoint.

Turns FastMCP's ``auth=`` hook into a small resource server so that, when the
server runs over HTTP, every request to /mcp must authenticate. Three
mechanisms are available and the latter two can be combined:

- ``key``   — a single pre-shared API key sent as ``Authorization: Bearer <key>``
- ``oauth`` — a built-in OAuth 2.1 authorization server (DCR + PKCE) so clients
  like ChatGPT and Claude can run their usual "sign in" connector flow
- ``both``  — accept an OAuth access token *or* the pre-shared API key

STDIO transport is unaffected (it inherits security from the local environment).
"""

from __future__ import annotations

import os
import secrets

from fastmcp.server.auth import AccessToken, AuthProvider, MultiAuth


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


def build_auth() -> AuthProvider | None:
    """Build the HTTP auth provider from the environment.

    ``MCP_AUTH_MODE`` selects the mechanism (default ``none``):

    - ``none``  — no auth; open endpoint for trusted/local setups
    - ``key``   — require ``MCP_AUTH_TOKEN`` as ``Authorization: Bearer <token>``
    - ``oauth`` — run the built-in OAuth 2.1 authorization server
    - ``both``  — accept an OAuth access token or the pre-shared API key

    ``oauth`` / ``both`` need ``MCP_PUBLIC_BASE_URL`` (the public HTTPS URL) so
    discovery metadata and redirect URIs resolve correctly. ``both`` also needs
    ``MCP_AUTH_TOKEN``.
    """
    mode = os.environ.get("MCP_AUTH_MODE", "none").strip().lower()
    token = os.environ.get("MCP_AUTH_TOKEN")
    public_url = os.environ.get("MCP_PUBLIC_BASE_URL")

    if mode in ("none", "off", ""):
        return None
    if mode == "key":
        return BearerTokenAuth(token) if token else None
    if mode not in ("oauth", "both"):
        raise SystemExit(
            f"Invalid MCP_AUTH_MODE={mode!r}. Use 'none', 'key', 'oauth' or 'both'."
        )
    if not public_url:
        raise SystemExit(f"MCP_AUTH_MODE={mode!r} requires MCP_PUBLIC_BASE_URL.")

    oauth = _oauth_provider(public_url)
    if mode == "oauth":
        return oauth
    if not token:
        raise SystemExit("MCP_AUTH_MODE='both' requires MCP_AUTH_TOKEN.")
    return MultiAuth(server=oauth, verifiers=[BearerTokenAuth(token)])
