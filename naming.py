"""Pure helpers for turning Mealie's OpenAPI spec into MCP tool names.

Kept side-effect free (no network, no server build) so it can be imported by
CI tooling — e.g. the nightly spec-update workflow that regenerates TOOLS.md.
"""

from __future__ import annotations

import re

_VERB = {"post": "create", "put": "update", "patch": "patch", "delete": "delete"}
_METHODS = ("get", "post", "put", "patch", "delete")


def path_name(method: str, path: str) -> str:
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
            if method not in _METHODS:
                continue
            oid = op.get("operationId")
            if not oid:
                continue
            base = path_name(method, path)[:56]
            candidate = base
            n = 2
            while candidate in seen:
                suffix = f"_{n}"
                candidate = base[: 56 - len(suffix)] + suffix
                n += 1
            seen.add(candidate)
            names[oid] = candidate
    return names


def sanitize(node):
    """Normalize Mealie's non-standard `format: uuid4` -> standard `uuid`."""
    if isinstance(node, dict):
        if node.get("format") == "uuid4":
            node["format"] = "uuid"
        for v in node.values():
            sanitize(v)
    elif isinstance(node, list):
        for v in node:
            sanitize(v)
    return node
