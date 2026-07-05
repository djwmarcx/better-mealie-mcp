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
import re
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.providers.openapi import MCPType, RouteMap

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


_VERB = {"post": "create", "put": "update", "patch": "patch", "delete": "delete"}


def _path_name(method: str, path: str) -> str:
    """Build a descriptive tool name from HTTP method + path.

    Mealie's operationIds bury the semantics in a `_api_<path>` echo
    (e.g. `create_one_api_recipes_post`), so the leading verb alone is
    generic and collides across resources. Derive the name from the path
    instead:  POST /api/recipes -> create_recipes,
              GET  /api/recipes/{slug} -> get_recipes_by_slug.
    """
    segs = [s for s in path.split("/") if s and s != "api"]
    words: list[str] = []
    ends_with_param = bool(segs) and segs[-1].startswith("{")
    for s in segs:
        if s.startswith("{") and s.endswith("}"):
            words.append("by_" + s[1:-1].replace("_id", "").strip("_") or "by_id")
        else:
            words.append(re.sub(r"[^a-zA-Z0-9]+", "_", s))
    if method == "get":
        verb = "get" if ends_with_param else "list"
    else:
        verb = _VERB[method]
    name = verb + "_" + "_".join(w for w in words if w)
    return re.sub(r"_+", "_", name).strip("_")


def build_names(spec: dict) -> dict[str, str]:
    """operationId -> descriptive, unique tool name (<=56 chars)."""
    names: dict[str, str] = {}
    seen: set[str] = set()
    for path, item in spec.get("paths", {}).items():
        for method, op in item.items():
            if method not in ("get", "post", "put", "patch", "delete"):
                continue
            oid = op.get("operationId")
            if not oid:
                continue
            base = _path_name(method, path)[:56]
            candidate = base
            n = 2
            while candidate in seen:
                suffix = f"_{n}"
                candidate = base[: 56 - len(suffix)] + suffix
                n += 1
            seen.add(candidate)
            names[oid] = candidate
    return names


def _sanitize(node):
    """Normalize Mealie's non-standard schema formats in place.

    Mealie emits `format: uuid4`, which JSON Schema validators don't know
    and warn about on every tool. Rewrite it to the standard `uuid`.
    """
    if isinstance(node, dict):
        if node.get("format") == "uuid4":
            node["format"] = "uuid"
        for v in node.values():
            _sanitize(v)
    elif isinstance(node, list):
        for v in node:
            _sanitize(v)
    return node


def build_server() -> FastMCP:
    spec = _sanitize(json.loads(SPEC_PATH.read_text()))
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
