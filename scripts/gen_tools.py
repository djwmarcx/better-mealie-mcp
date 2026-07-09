#!/usr/bin/env python3
"""Regenerate TOOLS.md from openapi.json and sync the tool count everywhere.

Pure/offline: reads the vendored spec, derives tool names via naming.py, and
rewrites TOOLS.md. If the operation count changed, updates the count in
README.md and setup-wizard.html too. Run by the nightly spec-update workflow
and usable locally:  uv run python scripts/gen_tools.py
"""

from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from naming import build_names, normalize  # noqa: E402

SPEC = ROOT / "openapi.json"
TOOLS = ROOT / "TOOLS.md"
README = ROOT / "README.md"
WIZARD = ROOT / "setup-wizard.html"


def method_and_path(spec: dict) -> dict[str, tuple[str, str]]:
    meta: dict[str, tuple[str, str]] = {}
    for path, item in spec["paths"].items():
        for m, op in item.items():
            if m in ("get", "post", "put", "patch", "delete") and op.get("operationId"):
                meta[op["operationId"]] = (m.upper(), path)
    return meta


def render_tools(spec: dict, names: dict[str, str]) -> tuple[str, int]:
    meta = method_and_path(spec)
    groups: dict[str, list[tuple[str, str, str]]] = collections.defaultdict(list)
    for oid, name in names.items():
        m, p = meta[oid]
        seg = [s for s in p.split("/") if s and s != "api"]
        groups[seg[0] if seg else "misc"].append((name, m, p))
    total = sum(len(v) for v in groups.values())
    lines = [
        "# Better Mealie MCP — Tool Reference",
        "",
        f"**{total} tools**, auto-generated from Mealie's OpenAPI spec. "
        "Every endpoint included, none excluded.",
        "",
    ]
    for g in sorted(groups):
        lines += [f"## `{g}` ({len(groups[g])})", "", "| tool | method | path |", "|------|--------|------|"]
        for name, m, p in sorted(groups[g]):
            lines.append(f"| `{name}` | {m} | `{p}` |")
        lines.append("")
    return "\n".join(lines), total


def old_count() -> int | None:
    if not TOOLS.exists():
        return None
    m = re.search(r"\*\*(\d+) tools\*\*", TOOLS.read_text())
    return int(m.group(1)) if m else None


def main() -> int:
    # Canonicalize the vendored spec first: normalize non-standard formats and
    # drop volatile (server-clock) defaults, then rewrite it pretty-printed so
    # the file diffs only on real API changes.
    spec = normalize(json.loads(SPEC.read_text()))
    with SPEC.open("w") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
        f.write("\n")

    names = build_names(spec)
    prev = old_count()
    text, total = render_tools(spec, names)
    TOOLS.write_text(text)
    print(f"TOOLS.md: {total} tools (was {prev})")

    if prev is not None and prev != total:
        for f in (README, WIZARD):
            if f.exists():
                f.write_text(re.sub(rf"\b{prev}\b", str(total), f.read_text()))
        print(f"Updated tool count {prev} -> {total} in README.md, setup-wizard.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
