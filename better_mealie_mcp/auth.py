"""Static bearer-token (API key) authentication for the MCP HTTP endpoint.

Turns FastMCP's ``auth=`` hook into a simple resource server: when the server
runs over HTTP, every request to /mcp must carry ``Authorization: Bearer <key>``.
STDIO transport is unaffected (it inherits security from the local environment).
"""

from __future__ import annotations

import secrets

from fastmcp.server.auth import AccessToken, AuthProvider


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