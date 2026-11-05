#!/usr/bin/env python3

import json
import re
from pathlib import Path
from datetime import datetime

ROOT = Path(".").resolve()

WORKSHEET = ROOT / "docs/system_inventory/NEUROVEST_GAP_QUALIFICATION.md"
REPORT = ROOT / "docs/system_inventory/NEUROVEST_GAP_CLASSIFICATION.md"

SEARCH_ROOTS = [
    ROOT / "frontend",
    ROOT / "backend/app",
]

rows = []

for line in WORKSHEET.read_text(encoding="utf-8").splitlines():

    if not line.startswith("|"):
        continue

    cols = [c.strip() for c in line.strip().split("|")[1:-1]]

    if len(cols) != 5:
        continue

    if cols[0] == "---:":
        continue

    rows.append({
        "fp": cols[0],
        "gap": cols[1],
        "status": cols[2],
    })


def build_patterns(gap: str):

    words = re.findall(r"[A-Za-z0-9_/.-]+", gap)

    ignore = {
        "no","not","was","were","detected","direct","frontend","backend",
        "dedicated","exact","explicit","current","appears","currently",
        "required","review","against","must","and","or","the","to","be",
        "route","page","functions","behavior","markers"
    }

    pats=[]

    for w in words:

        if len(w) < 4:
            continue

        if w.lower() in ignore:
            continue

        pats.append(re.escape(w))

    return pats[:6]


def search(patterns):

    evidence=[]

    for root in SEARCH_ROOTS:

        for file in root.rglob("*"):

            if file.suffix not in (
                ".py",".ts",".tsx",".js",".jsx"
            ):
                continue

            try:
                lines=file.read_text(
                    encoding="utf-8",
                    errors="ignore"
                ).splitlines()
            except Exception:
                continue

            for n,line in enumerate(lines,1):

                score=0

                lower=line.lower()

                for p in patterns:
                    if re.search(p.lower(), lower):
                        score+=1

                if score:
                    evidence.append(
                        (
                            score,
                            file.relative_to(ROOT),
                            n,
                            line.strip()
                        )
                    )

    evidence.sort(reverse=True)

    return evidence[:10]


with REPORT.open("w",encoding="utf-8") as out:

    out.write("# NEUROVEST GAP CLASSIFICATION\n\n")
    out.write(f"Generated: {datetime.now().isoformat()}\n\n")

    for row in rows:

        pats=build_patterns(row["gap"])

        hits=search(pats)

        out.write("="*80+"\n")
        out.write(f"FP{row['fp']}\n")
        out.write(row["gap"]+"\n\n")

        if hits:

            out.write("LIKELY STATUS: IMPLEMENTED OR PARTIALLY IMPLEMENTED\n\n")

            for score,file,line,text in hits:

                out.write(
                    f"{file}:{line}\n"
                )
                out.write(
                    f"    {text}\n\n"
                )

        else:

            out.write("LIKELY STATUS: POSSIBLY MISSING\n\n")

print("="*70)
print("GAP CLASSIFICATION COMPLETE")
print("="*70)
print(REPORT)
