#!/usr/bin/env python3
"""Builds the markdown summary table from results.jsonl.

Usage: build_summary.py <results.jsonl> <output.md>

Each case appears in results.jsonl as one line per condition (hook,
nohook), or a single failure line (status != "ok"/"timeout_or_error", no
condition) if extraction itself failed. Pivots those into one table row
per case.
"""
import json
import sys
from collections import defaultdict

results_path, out_path = sys.argv[1], sys.argv[2]

cases = defaultdict(dict)
order = []
meta = {}

with open(results_path) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        cid = r["id"]
        if cid not in meta:
            order.append(cid)
            meta[cid] = {
                "project": r["project"],
                "group": r["group"],
                "artifact": r["artifact"],
                "before": r["before"],
            }
        cond = r.get("condition", "n/a")
        cases[cid][cond] = r

def cell(r):
    if r is None:
        return "-"
    if r["status"] not in ("ok", "timeout_or_error"):
        return f"⚠️ {r['status']}"
    after = r.get("after") or "unknown"
    if r["status"] == "timeout_or_error":
        return f"{after} (⏱ timed out)"
    return after

def yul_cell(r):
    if r is None:
        return "-"
    if r["status"] not in ("ok", "timeout_or_error"):
        return "-"
    return r.get("yul", "-")

lines = []
lines.append("| id | project | dependency | before | hook: after | hook: yul | nohook: after |")
lines.append("|---|---|---|---|---|---|---|")
for cid in order:
    m = meta[cid]
    hook = cases[cid].get("hook")
    nohook = cases[cid].get("nohook")
    dep = f"{m['group']}:{m['artifact']}"
    lines.append(
        f"| {cid} | {m['project']} | {dep} | {m['before']} | "
        f"{cell(hook)} | {yul_cell(hook)} | {cell(nohook)} |"
    )

total = len(order)
hook_flagged = sum(1 for cid in order if cases[cid].get("hook", {}).get("yul") not in (None, "none", "-"))
extraction_failed = sum(1 for cid in order if "hook" not in cases[cid] and "nohook" not in cases[cid])

summary = f"""# BUMP 50-case survey

{total} cases from chains-project/bump, each: extract the `-pre` project,
prompt Claude with "Upgrade the `<group>:<artifact>` dependency in this
project." (no "latest"/"outdated" wording), once under the yul
`PreToolUse`+`SessionStart` hook and once with no hook, from the same
extracted source.

- Extraction failed entirely (docker pull/cp) for {extraction_failed}/{total} cases.
- yul flagged something during the `hook` run for {hook_flagged}/{total} cases.

""" + "\n".join(lines) + "\n"

with open(out_path, "w") as f:
    f.write(summary)

print(f"wrote {out_path}: {total} cases, {hook_flagged} flagged, {extraction_failed} extraction failures")
