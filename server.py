"""Back-compat shim: the server lives in the better_mealie_mcp package.

Kept so `uv run server.py`, `fastmcp run fastmcp.json`, and existing MCP client
registrations pointing at server.py keep working. Prefer the console script:
`uvx better-mealie-mcp` (or `uv run better-mealie-mcp` in this repo).
"""

from better_mealie_mcp.server import main, mcp  # noqa: F401  (mcp re-exported for fastmcp.json)

if __name__ == "__main__":
    main()
