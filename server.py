"""Better Mealie MCP server — exposes EVERY Mealie API endpoint as an MCP tool.

Auto-generated from Mealie's OpenAPI spec via FastMCP. No endpoint excluded.

Auth (env):
  MEALIE_BASE_URL   base URL of Mealie instance (default http://localhost:9925)
  MEALIE_API_TOKEN  long-lived API token (preferred)  -- OR --
  MEALIE_USERNAME + MEALIE_PASSWORD  credentials to fetch a token at startup

Optional knobs:
  MEALIE_TIMEOUT      per-request timeout, seconds (default 60)
  MEALIE_VERIFY_SSL   verify TLS cert; "false" to accept self-signed (default true)
  MCP_SERVER_NAME     MCP server name advertised to clients (default "Mealie")

Run:
  uv run server.py                 # stdio (for Claude Desktop / MCP clients)
  uv run server.py --http 8000     # streamable-http on port 8000
  fastmcp run fastmcp.json         # via FastMCP project config (stdio)
  fastmcp run fastmcp-http.json    # via FastMCP project config (http)
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.providers.openapi import MCPType, RouteMap

from naming import build_names, normalize

load_dotenv()  # pick up a local .env if present

BASE_URL = os.environ.get("MEALIE_BASE_URL", "http://localhost:9925").rstrip("/")
API_TOKEN = os.environ.get("MEALIE_API_TOKEN")
USERNAME = os.environ.get("MEALIE_USERNAME")
PASSWORD = os.environ.get("MEALIE_PASSWORD")
TIMEOUT = float(os.environ.get("MEALIE_TIMEOUT", "60"))
VERIFY_SSL = os.environ.get("MEALIE_VERIFY_SSL", "true").lower() not in ("false", "0", "no")
SERVER_NAME = os.environ.get("MCP_SERVER_NAME", "Better Mealie MCP")

SPEC_PATH = Path(__file__).parent / "openapi.json"


def _get_token() -> str:
    """Return a bearer token: use API token if given, else login."""
    if API_TOKEN:
        return API_TOKEN
    if USERNAME and PASSWORD:
        resp = httpx.post(
            f"{BASE_URL}/api/auth/token",
            data={"username": USERNAME, "password": PASSWORD},
            timeout=TIMEOUT,
            verify=VERIFY_SSL,
        )
        resp.raise_for_status()
        return resp.json()["access_token"]
    sys.exit(
        "No credentials. Set MEALIE_API_TOKEN, or MEALIE_USERNAME + MEALIE_PASSWORD."
    )


def build_server() -> FastMCP:
    spec = normalize(json.loads(SPEC_PATH.read_text()))
    token = _get_token()

    client = httpx.AsyncClient(
        base_url=BASE_URL,
        headers={"Authorization": f"Bearer {token}"},
        timeout=TIMEOUT,
        verify=VERIFY_SSL,
    )

    return FastMCP.from_openapi(
        openapi_spec=spec,
        client=client,
        name=SERVER_NAME,
        # EVERY route becomes a callable Tool. No exclusions.
        route_maps=[RouteMap(pattern=r".*", mcp_type=MCPType.TOOL)],
        mcp_names=build_names(spec),
    )


mcp = build_server()


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--http":
        mcp.run(transport="http", host="127.0.0.1", port=int(sys.argv[2]))
    else:
        mcp.run()
