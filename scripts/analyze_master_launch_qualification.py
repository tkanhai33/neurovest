#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import re

ROOT = Path(".").resolve()

MASTER = ROOT / "docs/system_inventory/MASTER_NEUROVEST_LAUNCH_QUALIFICATION.md"
REPORT = ROOT / "docs/system_inventory/MASTER_NEUROVEST_LAUNCH_REPORT.md"

if not MASTER.exists():
    raise SystemExit(f"Missing master document:\n{MASTER}")

text = MASTER.read_text(encoding="utf-8", errors="ignore")

parts = re.split(
    r'(?=FUNCTION PATH\s+\d+\s+—)',
    text,
    flags=re.IGNORECASE,
)

functions = []

def field(body, name):
    m = re.search(
        rf'^{re.escape(name)}\s*:\s*(.+)$',
        body,
        re.MULTILINE | re.IGNORECASE,
    )
    if m:
        return m.group(1).strip()
    return "UNKNOWN"

for part in parts:

    m = re.search(
        r'FUNCTION PATH\s+(\d+)\s+—\s+(.+)',
        part,
        re.IGNORECASE,
    )

    if not m:
        continue

    functions.append({
        "number": int(m.group(1)),
        "title": m.group(2).strip(),
        "inventory": field(part, "Inventory status"),
        "implementation": field(part, "Implementation status"),
        "qualification": field(part, "Qualification status"),
        "importance": field(part, "Launch importance"),
        "verified": field(part, "Last verified"),
        "body": part,
    })

functions.sort(key=lambda x: x["number"])

critical = [
    f for f in functions
    if "CRITICAL" in f["importance"].upper()
]

verification = [
    f for f in functions
    if (
        "UNVERIFIED" in f["qualification"].upper()
        or "PARTIAL" in f["qualification"].upper()
        or "UNKNOWN" in f["qualification"].upper()
    )
]

with REPORT.open("w", encoding="utf-8") as out:

    out.write("# NEUROVEST MASTER LAUNCH REPORT\n\n")
    out.write(f"Generated: {datetime.now().isoformat()}\n\n")

    out.write("## Executive Summary\n\n")
    out.write(f"Function Paths: {len(functions)}\n")
    out.write(f"Critical Functions: {len(critical)}\n")
    out.write(f"Require Verification: {len(verification)}\n\n")

    out.write("---\n\n")

    out.write("## Function Status Matrix\n\n")
    out.write("| FP | Function | Implementation | Qualification | Importance |\n")
    out.write("|---:|---|---|---|---|\n")

    for f in functions:
        out.write(
            f"| {f['number']:02d} | "
            f"{f['title']} | "
            f"{f['implementation']} | "
            f"{f['qualification']} | "
            f"{f['importance']} |\n"
        )

    out.write("\n---\n\n")

    out.write("## Critical Function Paths\n\n")

    if critical:
        for f in critical:
            out.write(
                f"- FP{f['number']:02d} — {f['title']}\n"
            )
    else:
        out.write("None detected.\n")

    out.write("\n---\n\n")

    out.write("## Functions Requiring Qualification\n\n")

    if verification:
        for f in verification:
            out.write(
                f"- FP{f['number']:02d} — "
                f"{f['title']} "
                f"({f['qualification']})\n"
            )
    else:
        out.write("None.\n")

    out.write("\n---\n\n")
    out.write("# APPENDIX\n\n")

    for f in functions:
        out.write(f["body"])
        out.write("\n\n---\n\n")

print("="*70)
print("MASTER LAUNCH REPORT GENERATED")
print("="*70)
print("Functions Parsed :", len(functions))
print("Critical Paths   :", len(critical))
print("Need Verification:", len(verification))
print()
print(REPORT)
