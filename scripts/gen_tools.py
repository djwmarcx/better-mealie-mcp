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


def sync_counts(total: int) -> None:
    """Point every tool-count badge at `total`.

    Count-agnostic: matches the badge/label shape, not a specific number, so it
    stays correct forever and never needs to know the previous count. The number
    lives only in these generated/badge spots — prose says "every endpoint".
    """
    n = str(total)
    edits = [
        (README, [
            (r"(badge/tools-)\d+(-)", rf"\g<1>{n}\g<2>"),       # shields badge
            (r'(alt=")\d+( tools")', rf"\g<1>{n}\g<2>"),        # badge alt text
        ]),
        (WIZARD, [
            (r"(<b>)\d+(</b>&nbsp;tools)", rf"\g<1>{n}\g<2>"),  # header chip
        ]),
    ]
    for path, subs in edits:
        if not path.exists():
            continue
        text = path.read_text()
        for pattern, repl in subs:
            text = re.sub(pattern, repl, text)
        path.write_text(text)


def main() -> int:
    # Canonicalize the vendored spec first: normalize non-standard formats and
    # drop volatile (server-clock) defaults, then rewrite it pretty-printed so
    # the file diffs only on real API changes.
    spec = normalize(json.loads(SPEC.read_text()))
    with SPEC.open("w") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
        f.write("\n")

    names = build_names(spec)
    text, total = render_tools(spec, names)
    TOOLS.write_text(text)
    sync_counts(total)
    print(f"TOOLS.md + badges synced to {total} tools")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
