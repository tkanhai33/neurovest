#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import re

ROOT = Path(".").resolve()

OUT = ROOT / "docs/system_inventory/MASTER_NEUROVEST_LAUNCH_QUALIFICATION.md"

reports = []

for path in sorted(
    (ROOT / "runtime/system_inventory").rglob("*_copy_paste_section.txt")
):

    m = re.search(
        r"function_path_(\d+)_copy_paste_section",
        path.name,
        re.IGNORECASE,
    )

    if not m:
        continue

    number = int(m.group(1))

    text = path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    reports.append((number, path, text))

reports.sort(key=lambda x: x[0])

with OUT.open("w", encoding="utf-8") as out:

    out.write("# MASTER NEUROVEST LAUNCH QUALIFICATION\n\n")
    out.write(f"Generated: {datetime.now().isoformat()}\n\n")
    out.write(f"Functions Collected: {len(reports)}\n\n")
    out.write("---\n\n")

    for number, path, text in reports:

        out.write(text.rstrip())
        out.write("\n\n---\n\n")

print("=" * 70)
print("MASTER QUALIFICATION REBUILT")
print("=" * 70)
print("Functions:", len(reports))
print(OUT)
