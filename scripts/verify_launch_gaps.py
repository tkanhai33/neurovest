#!/usr/bin/env python3

import json
import re
from pathlib import Path
from datetime import datetime

ROOT = Path(".").resolve()

WORKSHEET = ROOT / "docs/system_inventory/NEUROVEST_GAP_QUALIFICATION.md"
REPORT = ROOT / "docs/system_inventory/NEUROVEST_GAP_VERIFICATION_REPORT.md"

SEARCH_ROOTS = [
    ROOT / "frontend",
    ROOT / "backend" / "app",
]

VERIFY_TYPES = {
    "VERIFY DETECTION",
    "VERIFY ROUTE",
    "VERIFY FRONTEND",
}

KEYWORDS = {
    "Registration rate limiting": [r"rate.?limit", r"register"],
    "Login rate limiting": [r"rate.?limit", r"login"],
    "login-to-dashboard redirect": [r"redirect", r"dashboard", r"login"],
    "/api/v1/chat": [r"/api/v1/chat", r"chat"],
    "notification": [r"notification", r"alert"],
    "broker": [r"snaptrade", r"broker"],
    "operating-mode": [r"mode", r"emergency", r"safe", r"locked"],
}

rows = []

for line in WORKSHEET.read_text(encoding="utf-8").splitlines():
    if not line.startswith("|"):
        continue

    cols = [c.strip() for c in line.strip().split("|")[1:-1]]

    if len(cols) != 5:
        continue

    fp, gap, status, evidence, action = cols

    if status not in VERIFY_TYPES:
        continue

    rows.append({
        "fp": fp,
        "gap": gap,
        "status": status,
    })

results = []

for row in rows:

    patterns = []

    for key, pats in KEYWORDS.items():
        if key.lower() in row["gap"].lower():
            patterns = pats
            break

    hits = []

    if patterns:
        regexes = [re.compile(p, re.IGNORECASE) for p in patterns]

        for root in SEARCH_ROOTS:

            for file in root.rglob("*"):

                if file.suffix not in (".py", ".ts", ".tsx", ".js", ".jsx"):
                    continue

                try:
                    lines = file.read_text(
                        encoding="utf-8",
                        errors="ignore"
                    ).splitlines()
                except Exception:
                    continue

                for lineno, line in enumerate(lines, 1):

                    if any(r.search(line) for r in regexes):
                        hits.append(
                            f"{file.relative_to(ROOT)}:{lineno}"
                        )

                        if len(hits) >= 10:
                            break

                if len(hits) >= 10:
                    break

            if len(hits) >= 10:
                break

    results.append((row, hits))

with REPORT.open("w", encoding="utf-8") as out:

    out.write("# NEUROVEST GAP VERIFICATION REPORT\n\n")
    out.write(f"Generated: {datetime.now().isoformat()}\n\n")

    for row, hits in results:

        out.write(f"## FP{row['fp']}\n\n")
        out.write(f"Gap: {row['gap']}\n\n")
        out.write(f"Classification: {row['status']}\n\n")

        if hits:
            out.write("Evidence Found:\n\n")
            for h in hits:
                out.write(f"- {h}\n")
        else:
            out.write("Evidence Found:\n\n")
            out.write("- NONE\n")

        out.write("\n---\n\n")

print("=" * 70)
print("GAP VERIFICATION COMPLETE")
print("=" * 70)
print(REPORT)
