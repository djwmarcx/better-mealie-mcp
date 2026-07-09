#!/usr/bin/env python3
"""Sync the MCP version to a Mealie version and log it in VERSIONS.md.

Usage:  python scripts/set_version.py <mealie_version> <date> <tools>
        e.g. python scripts/set_version.py v3.21.0 2026-08-01 261

Writes MEALIE_VERSION, sets the pyproject version to the same value (minus a
leading "v"), and prepends a row to the VERSIONS.md table. Idempotent: a row
for the same (Mealie version, date) is not duplicated.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main(mealie_version: str, date: str, tools: str) -> int:
    mcp_version = mealie_version.lstrip("v")

    (ROOT / "MEALIE_VERSION").write_text(mealie_version + "\n")

    pyproject = ROOT / "pyproject.toml"
    text = pyproject.read_text()
    text = re.sub(
        r'(?m)^version = "[^"]*"(.*)$',
        f'version = "{mcp_version}"   # mirrors the targeted Mealie version (see MEALIE_VERSION)',
        text,
        count=1,
    )
    pyproject.write_text(text)

    versions = ROOT / "VERSIONS.md"
    lines = versions.read_text().splitlines()
    row = f"| {mcp_version} | {mealie_version} | {date} | {tools} |"
    if any(f"| {mealie_version} | {date} |" in ln for ln in lines):
        print("VERSIONS.md already has this row; not duplicating.")
    else:
        for i, ln in enumerate(lines):
            if re.match(r"\|[-\s|]+\|\s*$", ln):  # the table's |---|---| separator
                lines.insert(i + 1, row)
                break
        versions.write_text("\n".join(lines) + "\n")
        print(f"VERSIONS.md: added row -> {row}")

    print(f"MCP version set to {mcp_version} (Mealie {mealie_version})")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("usage: set_version.py <mealie_version> <date> <tools>")
    raise SystemExit(main(*sys.argv[1:]))
