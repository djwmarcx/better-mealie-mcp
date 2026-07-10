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

from better_mealie_mcp.naming import build_names, normalize  # noqa: E402

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


def group_counts(spec: dict, names: dict[str, str]) -> list[dict]:
    """[{tag, count, subs}] per Mealie group (first path segment), biggest first.

    `subs` are the distinct non-parameter path segments under the group — a
    human-readable hint of the services it covers (e.g. recipes → images,
    comments, exports, timeline…).
    """
    meta = method_and_path(spec)
    counts: dict[str, int] = collections.Counter()
    subs: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    tools: dict[str, list[str]] = collections.defaultdict(list)
    for oid, name in names.items():
        _, p = meta[oid]
        seg = [s for s in p.split("/") if s and s != "api"]
        grp = seg[0] if seg else "misc"
        counts[grp] += 1
        tools[grp].append(name)
        for s in seg[1:]:
            if not (s.startswith("{") and s.endswith("}")):
                subs[grp][s] += 1
    # subs ordered by how many endpoints use them (most representative first)
    return [
        {
            "tag": t,
            "count": c,
            "subs": [s for s, _ in subs[t].most_common()],
            "tools": sorted(tools[t]),
        }
        for t, c in sorted(counts.items(), key=lambda kv: -kv[1])
    ]


def context_costs(spec: dict, names: dict[str, str]) -> dict[str, dict[str, int]]:
    """Per-group wire-char cost in each context mode: {tag: {leanest,lean,full}}.

    Builds the FastMCP server offline (dummy client, no network) in each mode and
    sums each tool's serialized MCP wire size, grouped by tag. The wizard adds
    these up for the chosen groups + mode to show a live token estimate. Kept
    here so it regenerates whenever the spec changes.
    """
    import asyncio

    import httpx
    from fastmcp import FastMCP
    from fastmcp.server.providers.openapi import MCPType, RouteMap

    from better_mealie_mcp.naming import normalize, slim

    meta = method_and_path(spec)
    group_of = {}
    for oid, name in names.items():
        _, p = meta[oid]
        seg = [s for s in p.split("/") if s and s != "api"]
        group_of[name] = seg[0] if seg else "misc"

    costs: dict[str, dict[str, int]] = collections.defaultdict(dict)
    for mode in ("leanest", "lean", "full"):
        s = normalize(json.loads(json.dumps(spec)))  # deep copy
        if mode != "full":
            slim(s.get("components", {}), aggressive=(mode == "leanest"))
            slim(s.get("paths", {}), aggressive=(mode == "leanest"))
        m = FastMCP.from_openapi(
            openapi_spec=s, client=httpx.AsyncClient(base_url="http://x"), name="m",
            route_maps=[RouteMap(pattern=r".*", mcp_type=MCPType.TOOL)],
            mcp_names=build_names(s), validate_output=(mode == "full"),
        )
        per = collections.Counter()
        for t in asyncio.run(m.list_tools()):
            w = t.to_mcp_tool().model_dump(exclude_none=True)
            per[group_of.get(w["name"], "misc")] += len(json.dumps(w, separators=(",", ":")))
        for g, c in per.items():
            costs[g][mode] = c
    return costs


def inject_costs(costs: dict) -> None:
    """Write the per-group context-cost table into the wizard between markers."""
    if not WIZARD.exists():
        return
    payload = json.dumps(costs, separators=(",", ":"))
    text = re.sub(
        r"/\*COSTS_START\*/.*?/\*COSTS_END\*/",
        f"/*COSTS_START*/{payload}/*COSTS_END*/",
        WIZARD.read_text(),
        flags=re.DOTALL,
    )
    WIZARD.write_text(text)


def inject_groups(groups: list[dict]) -> None:
    """Write the generated group list into the wizard between markers."""
    if not WIZARD.exists():
        return
    payload = json.dumps(groups, separators=(",", ":"))
    text = re.sub(
        r"/\*GROUPS_START\*/.*?/\*GROUPS_END\*/",
        f"/*GROUPS_START*/{payload}/*GROUPS_END*/",
        WIZARD.read_text(),
        flags=re.DOTALL,
    )
    WIZARD.write_text(text)


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
    inject_groups(group_counts(spec, names))
    inject_costs(context_costs(spec, names))
    print(f"TOOLS.md + badges + wizard groups synced to {total} tools")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
