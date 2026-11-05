#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime

ROOT = Path(".").resolve()

KB = ROOT / "runtime/system_inventory/launch_knowledge_base.json"
OUT = ROOT / "docs/system_inventory/NEUROVEST_EXECUTIVE_LAUNCH_DASHBOARD.md"

data = json.loads(KB.read_text(encoding="utf-8"))

functions = sorted(
    data["functions"],
    key=lambda x: x["function_path"]
)

summary = data["summary"]

with OUT.open("w", encoding="utf-8") as out:

    out.write("# NEUROVEST EXECUTIVE LAUNCH DASHBOARD\n\n")
    out.write(f"Generated: {datetime.now().isoformat()}\n\n")

    out.write("## Repository Summary\n\n")

    out.write(f"- Function Paths: {data['function_count']}\n")
    out.write(f"- Browser Routes: {summary['browser_routes']}\n")
    out.write(f"- Backend Routes: {summary['backend_routes']}\n")
    out.write(f"- Frontend Requests: {summary['frontend_requests']}\n")
    out.write(f"- Tests: {summary['tests']}\n")
    out.write(f"- Potential Gaps: {summary['potential_gaps']}\n\n")

    out.write("---\n\n")

    out.write("## Function Inventory\n\n")

    out.write("| FP | Browser Route | Backend Routes | Requests | Tests | Gaps |\n")
    out.write("|---:|---|---:|---:|---:|---:|\n")

    total_tests = 0
    total_routes = 0
    total_requests = 0
    total_gaps = 0

    for f in functions:

        routes = len(f.get("backend_routes", []))
        reqs = len(f.get("frontend_requests", []))
        tests = len(f.get("tests", []))
        gaps = len(f.get("potential_gaps", []))

        total_routes += routes
        total_requests += reqs
        total_tests += tests
        total_gaps += gaps

        route = f.get("browser_route") or "-"

        out.write(
            f"| {f['function_path']:02d} "
            f"| {route} "
            f"| {routes} "
            f"| {reqs} "
            f"| {tests} "
            f"| {gaps} |\n"
        )

    out.write("\n---\n\n")

    out.write("## Overall Totals\n\n")

    out.write(f"- Backend Routes: {total_routes}\n")
    out.write(f"- Frontend Requests: {total_requests}\n")
    out.write(f"- Tests: {total_tests}\n")
    out.write(f"- Potential Gaps: {total_gaps}\n\n")

    out.write("---\n\n")

    out.write("## Launch Recommendation\n\n")

    if total_gaps == 0:
        verdict = "READY FOR CONTROLLED EARLY USER VALIDATION"
    else:
        verdict = "QUALIFICATION REQUIRED BEFORE CONTROLLED EARLY USER RELEASE"

    out.write(f"**{verdict}**\n\n")

    out.write("## Largest Gap Counts\n\n")

    ranked = sorted(
        functions,
        key=lambda f: len(f.get("potential_gaps", [])),
        reverse=True,
    )

    for f in ranked:
        gaps = len(f.get("potential_gaps", []))
        if gaps:
            out.write(
                f"- FP{f['function_path']:02d}: {gaps} gap(s)\n"
            )

print("=" * 70)
print("EXECUTIVE DASHBOARD GENERATED")
print("=" * 70)
print(OUT)
