"""Better Mealie MCP — every Mealie API endpoint as an MCP tool.

The actual server lives in better_mealie_mcp.server and is re-exported lazily:
building it needs Mealie credentials and network, but offline tooling (CI's
gen_tools/spec_diff) imports better_mealie_mcp.naming and must not trigger it.
"""

from __future__ import annotations

_LAZY = {"mcp", "main", "build_server", "MEALIE_VERSION"}


def __getattr__(name: str):
    if name in _LAZY:
        from . import server

        return getattr(server, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
