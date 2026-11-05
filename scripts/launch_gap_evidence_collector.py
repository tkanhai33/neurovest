#!/usr/bin/env python3

from pathlib import Path
import json
import re

ROOT = Path(".").resolve()

GAPS = ROOT / "docs/system_inventory/NEUROVEST_GAP_QUALIFICATION.md"
OUT = ROOT / "docs/system_inventory/NEUROVEST_GAP_EVIDENCE.md"

SEARCH_ROOTS = [
    ROOT / "frontend",
    ROOT / "backend" / "app",
]

IGNORE = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    ".next",
    "runtime",
    "archive",
    "build",
    "dist",
    "coverage",
}

rows = []

for line in GAPS.read_text(encoding="utf-8", errors="ignore").splitlines():
    if not line.startswith("|"):
        continue

    cols = [c.strip() for c in line.strip().split("|")[1:-1]]

    if len(cols) != 5:
        continue

    if cols[0] == "---:":
        continue

    rows.append((cols[0], cols[1]))

def keywords(text):
    words = re.findall(r"[A-Za-z0-9_/.-]+", text)
    stop = {
        "no","not","was","were","detected","direct","frontend","backend",
        "dedicated","exact","explicit","current","appears","currently",
        "required","review","against","must","route","page","functions",
        "behavior","markers","the","and","for","with","from","this"
    }
    out=[]
    for w in words:
        if len(w) < 4:
            continue
        if w.lower() in stop:
            continue
        out.append(w)
    return out[:6]

with OUT.open("w", encoding="utf-8") as report:

    report.write("# NEUROVEST GAP EVIDENCE\n\n")

    for fp,gap in rows:

        report.write(f"## FP{fp}\n")
        report.write(f"{gap}\n\n")

        pats = keywords(gap)

        found = []

        for root in SEARCH_ROOTS:

            for file in root.rglob("*"):

                if any(part in IGNORE for part in file.parts):
                    continue

                if not file.is_file():
                    continue

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

                score=0

                for n,line in enumerate(lines,1):

                    lower=line.lower()

                    if all(k.lower() in lower for k in pats[:1]):
                        found.append(
                            (
                                file.relative_to(ROOT),
                                n,
                                line.strip()
                            )
                        )

                        if len(found)>=15:
                            break

                if len(found)>=15:
                    break

            if len(found)>=15:
                break

        if found:

            report.write("STATUS: POSSIBLY IMPLEMENTED\n\n")

            for f,n,t in found:
                report.write(f"- {f}:{n}\n")
                report.write(f"    {t}\n")

        else:

            report.write("STATUS: POSSIBLY MISSING\n")

        report.write("\n---\n\n")

print("="*70)
print("GAP EVIDENCE REPORT GENERATED")
print("="*70)
print(OUT)
