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
            # Truncating to the 56-char MCP name limit can cut mid-word and
            # leave a trailing "_"; strip it so it matches the name FastMCP
            # actually registers (and TOOLS.md / the wizard stay accurate).
            base = path_name(method, path)[:56].rstrip("_")
            candidate = base
            n = 2
            while candidate in seen:
                suffix = f"_{n}"
                candidate = base[: 56 - len(suffix)].rstrip("_") + suffix
                n += 1
            seen.add(candidate)
            names[oid] = candidate
    return names


_ISO_DT = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z?$")


def normalize(node):
    """Canonicalize the spec in place so it diffs only on real API changes.

    Two fixes:
    - `format: uuid4` (non-standard) -> `uuid`, silencing validator warnings.
    - Drop `default` values that are ISO-8601 datetimes: Mealie stamps the
      server's *current time* into a couple of schema defaults
      (RecipeTimelineEventIn/Out.timestamp), which would otherwise churn the
      vendored spec on every fetch.
    """
    if isinstance(node, dict):
        if node.get("format") == "uuid4":
            node["format"] = "uuid"
        dv = node.get("default")
        if isinstance(dv, str) and _ISO_DT.match(dv):
            node.pop("default", None)
        for v in node.values():
            normalize(v)
    elif isinstance(node, list):
        for v in node:
            normalize(v)
    return node


# Backwards-compatible alias.
sanitize = normalize
