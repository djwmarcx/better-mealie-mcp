"""Better Mealie MCP server — exposes EVERY Mealie API endpoint as an MCP tool.

Auto-generated from Mealie's OpenAPI spec via FastMCP. No endpoint excluded.

Auth (env):
  MEALIE_BASE_URL   base URL of Mealie instance (default http://localhost:9925)
  MEALIE_API_TOKEN  long-lived API token (preferred)  -- OR --
  MEALIE_USERNAME + MEALIE_PASSWORD  credentials to fetch a token at startup

Optional knobs:
  MEALIE_TIMEOUT      per-request timeout, seconds (default 60)
  MEALIE_VERIFY_SSL   verify TLS cert; "false" to accept self-signed (default true)
  MCP_SERVER_NAME     MCP server name advertised to clients (default "Better Mealie MCP")
  MCP_HOST            bind address in --http mode (default 127.0.0.1; the Docker
                      image sets 0.0.0.0)

Run:
  uv run better-mealie-mcp              # stdio, from a source checkout
  uv run better-mealie-mcp --http 8000  # streamable-http on port 8000
  docker run -i --rm ghcr.io/djwmarcx/better-mealie-mcp   # stdio, from GHCR
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.providers.openapi import MCPType, RouteMap

from .naming import build_names, normalize

load_dotenv()  # pick up a local .env if present

BASE_URL = os.environ.get("MEALIE_BASE_URL", "http://localhost:9925").rstrip("/")
API_TOKEN = os.environ.get("MEALIE_API_TOKEN")
USERNAME = os.environ.get("MEALIE_USERNAME")
PASSWORD = os.environ.get("MEALIE_PASSWORD")
TIMEOUT = float(os.environ.get("MEALIE_TIMEOUT", "60"))
VERIFY_SSL = os.environ.get("MEALIE_VERIFY_SSL", "true").lower() not in ("false", "0", "no")
SERVER_NAME = os.environ.get("MCP_SERVER_NAME", "Better Mealie MCP")
# Optional tool filtering by Mealie API group (the first path segment, e.g.
# "recipes", "households", "admin"). Fewer tools = leaner context / fits clients
# that cap tool counts. INCLUDE wins if both are set; unset = every endpoint.
INCLUDE_TAGS = [t.strip() for t in os.environ.get("MEALIE_INCLUDE_TAGS", "").split(",") if t.strip()]
EXCLUDE_TAGS = [t.strip() for t in os.environ.get("MEALIE_EXCLUDE_TAGS", "").split(",") if t.strip()]


def _route_maps() -> list[RouteMap]:
    """Map Mealie groups to include/exclude per the env config.

    Route maps are evaluated in order (first match wins), so listed groups get
    their rule and a catch-all closes it out.
    """
    grp = lambda g: rf"^/api/{re.escape(g)}(/|$)"  # noqa: E731
    if INCLUDE_TAGS:
        return [RouteMap(pattern=grp(g), mcp_type=MCPType.TOOL) for g in INCLUDE_TAGS] + [
            RouteMap(pattern=r".*", mcp_type=MCPType.EXCLUDE)
        ]
    if EXCLUDE_TAGS:
        return [RouteMap(pattern=grp(g), mcp_type=MCPType.EXCLUDE) for g in EXCLUDE_TAGS] + [
            RouteMap(pattern=r".*", mcp_type=MCPType.TOOL)
        ]
    # Default: EVERY route becomes a callable Tool. No exclusions.
    return [RouteMap(pattern=r".*", mcp_type=MCPType.TOOL)]


def _data_path(name: str) -> Path:
    """Locate a data file both installed and in a source checkout.

    In a built wheel the spec files are packaged next to this module
    (force-included by hatch); in the repo they live at the project root,
    one level up.
    """
    here = Path(__file__).parent
    candidate = here / name
    return candidate if candidate.exists() else here.parent / name


SPEC_PATH = _data_path("openapi.json")
VERSION_PATH = _data_path("MEALIE_VERSION")

# The Mealie release this vendored spec was generated from (e.g. "v3.20.1").
# The MCP server advertises the same version, so `MCP version == Mealie version`.
MEALIE_VERSION = (
    VERSION_PATH.read_text().strip() if VERSION_PATH.exists() else "unknown"
)


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
        # Advertise the targeted Mealie version so clients see the mapping
        # (MCP version == Mealie version).
        version=MEALIE_VERSION.lstrip("v"),
        instructions=f"Exposes every endpoint of the Mealie API ({MEALIE_VERSION}) as a tool.",
        route_maps=_route_maps(),
        mcp_names=build_names(spec),
    )


mcp = build_server()


def main() -> None:
    """Console entry point: stdio by default, `--http [port]` for HTTP."""
    argv = sys.argv[1:]
    if argv and argv[0] == "--http":
        port = int(argv[1]) if len(argv) > 1 else 8000
        host = os.environ.get("MCP_HOST", "127.0.0.1")
        mcp.run(transport="http", host=host, port=port)
    else:
        mcp.run()
