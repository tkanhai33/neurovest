#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime

ROOT = Path(".").resolve()
SOURCE = ROOT / "runtime/system_inventory"
OUT = ROOT / "docs/system_inventory/NEUROVEST_GAP_QUALIFICATION.md"

inventories = sorted(SOURCE.rglob("*_inventory.json"))

rows = []

for inv in inventories:
    try:
        data = json.loads(inv.read_text(encoding="utf-8"))
    except Exception:
        continue

    fp = inv.name.split("_")[2]

    for gap in data.get("potential_gaps", []):
        rows.append((fp, gap))

with OUT.open("w", encoding="utf-8") as out:
    out.write("# NEUROVEST GAP QUALIFICATION WORKSHEET\n\n")
    out.write(f"Generated: {datetime.now().isoformat()}\n\n")
    out.write("| FP | Gap | Status | Evidence | Action |\n")
    out.write("|---:|---|---|---|---|\n")

    for fp, gap in sorted(rows):
        out.write(
            f"| {fp} | {gap} | TODO |  |  |\n"
        )

print("=" * 70)
print("GAP QUALIFICATION WORKSHEET GENERATED")
print("=" * 70)
print(f"Gap entries: {len(rows)}")
print(OUT)
