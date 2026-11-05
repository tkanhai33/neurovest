#!/usr/bin/env python3

from pathlib import Path
import re

ROOT = Path(".").resolve()

MASTER = ROOT / "docs/system_inventory/MASTER_NEUROVEST_LAUNCH_QUALIFICATION.md"
REPORT = ROOT / "docs/system_inventory/MASTER_NEUROVEST_LAUNCH_REPORT.md"

master = MASTER.read_text(encoding="utf-8", errors="ignore")
report = REPORT.read_text(encoding="utf-8", errors="ignore")

parts = re.split(
    r'(?=FUNCTION PATH\s+\d+\s+—)',
    master,
    flags=re.IGNORECASE,
)

blockers = []

for part in parts:

    header = re.search(
        r'FUNCTION PATH\s+(\d+)\s+—\s+(.+)',
        part,
        re.IGNORECASE,
    )

    if not header:
        continue

    fp = int(header.group(1))
    title = header.group(2).strip()

    gap = re.search(
        r'Current Gaps(.*?)(?:FUNCTION FLOW GRAPH|Repository Files|Launch Dependency|FINAL VERDICT|\Z)',
        part,
        re.DOTALL | re.IGNORECASE,
    )

    if not gap:
        continue

    lines = []

    for line in gap.group(1).splitlines():

        line = line.strip()

        if not line:
            continue

        line = re.sub(r'^[\-\*\u2022]+\s*', '', line)

        if line.lower() == "current gaps":
            continue

        lines.append(line)

    blockers.append((fp, title, lines))

marker = "## Launch Blockers / Verification Required"

if marker not in report:
    raise SystemExit(
        f"Couldn't locate section:\n{marker}"
    )

before = report.split(marker)[0]

new = before
new += marker + "\n\n"

for fp, title, lines in blockers:

    new += f"### FP{fp:02d} — {title}\n\n"

    if lines:
        for item in lines:
            new += f"- {item}\n"
    else:
        new += "- No explicit gaps listed.\n"

    new += "\n"

new += (
    "\n---\n\n"
    "Report updated automatically from the Function Path inventories.\n"
)

REPORT.write_text(new, encoding="utf-8")

print("=" * 70)
print("LAUNCH BLOCKERS SECTION REBUILT")
print("=" * 70)
print(f"Functions Processed : {len(blockers)}")
print(REPORT)
