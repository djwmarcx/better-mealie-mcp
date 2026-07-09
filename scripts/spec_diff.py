#!/usr/bin/env python3
"""Emit markdown release notes describing what changed between two specs.

Usage:  python scripts/spec_diff.py OLD.json NEW.json > notes.md

Compares the derived MCP tool set (name -> METHOD path) so the notes read in
terms of the tools people actually call, not raw operationIds.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from naming import build_names  # noqa: E402


def tool_map(spec: dict) -> dict[str, str]:
    """tool name -> 'METHOD /path'."""
    meta = {}
    for path, item in spec.get("paths", {}).items():
        for m, op in item.items():
            if m in ("get", "post", "put", "patch", "delete") and op.get("operationId"):
                meta[op["operationId"]] = f"{m.upper()} {path}"
    names = build_names(spec)
    return {name: meta[oid] for oid, name in names.items()}


def main(old_path: str, new_path: str) -> int:
    old = tool_map(json.loads(Path(old_path).read_text()))
    new_spec = json.loads(Path(new_path).read_text())
    new = tool_map(new_spec)
    ver = new_spec.get("info", {}).get("version", "unknown")

    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))

    out = [
        "Automated update of the vendored Mealie OpenAPI spec "
        "(`openapi.json`) from `demo.mealie.io`.",
        "",
        f"- **Mealie spec version:** `{ver}`",
        f"- **Tools:** {len(old)} → {len(new)}"
        + (f"  (**+{len(added)}**, **−{len(removed)}**)" if (added or removed) else ""),
        "",
    ]
    if added:
        out.append(f"### Added tools ({len(added)})\n")
        out += [f"- `{n}` — {new[n]}" for n in added]
        out.append("")
    if removed:
        out.append(f"### Removed tools ({len(removed)})\n")
        out += [f"- `{n}` — {old[n]}" for n in removed]
        out.append("")
    if not added and not removed:
        out.append(
            "### Schema-only changes\n\n"
            "No tools added or removed — parameters, response shapes, or "
            "descriptions changed. See the commit diff for details."
        )
    out.append("")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: spec_diff.py OLD.json NEW.json")
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
