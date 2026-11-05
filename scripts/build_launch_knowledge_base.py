#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime
import re

ROOT = Path(".").resolve()

SOURCE = ROOT / "runtime/system_inventory"
OUT = SOURCE / "launch_knowledge_base.json"

inventories = []

for path in sorted(SOURCE.rglob("*_inventory.json")):

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"SKIPPED {path}: {exc}")
        continue

    m = re.search(r'function_path_(\d+)', path.name, re.IGNORECASE)

    if m:
        fp = int(m.group(1))
    else:
        fp = 999

    record = {
        "function_path": fp,
        "file": str(path.relative_to(ROOT)),
        "inventory": data.get("inventory"),
        "browser_route": data.get("browser_route"),
        "page_file": data.get("page_file"),
        "page_component": data.get("page_component"),
        "layout_file": data.get("layout_file"),
        "route_type": data.get("route_type"),
        "middleware": data.get("middleware", {}),
        "backend_routes": data.get("backend_routes", []),
        "frontend_requests": data.get("frontend_requests", []),
        "handlers": data.get("handlers", []),
        "controls": data.get("controls", {}),
        "security_controls": data.get("security_controls", {}),
        "tests": data.get("tests", []),
        "potential_gaps": data.get("potential_gaps", []),
        "raw": data
    }

    inventories.append(record)

inventories.sort(key=lambda x: x["function_path"])

knowledge = {
    "generated": datetime.now().isoformat(),
    "function_count": len(inventories),
    "functions": inventories,
    "summary": {
        "browser_routes": sum(
            1 for f in inventories if f["browser_route"]
        ),
        "backend_routes": sum(
            len(f["backend_routes"])
            for f in inventories
        ),
        "frontend_requests": sum(
            len(f["frontend_requests"])
            for f in inventories
        ),
        "tests": sum(
            len(f["tests"])
            for f in inventories
        ),
        "potential_gaps": sum(
            len(f["potential_gaps"])
            for f in inventories
        ),
    }
}

OUT.write_text(
    json.dumps(
        knowledge,
        indent=2,
        ensure_ascii=False,
    ),
    encoding="utf-8",
)

print("=" * 70)
print("LAUNCH KNOWLEDGE BASE BUILT")
print("=" * 70)
print(f"Functions           : {knowledge['function_count']}")
print(f"Browser Routes      : {knowledge['summary']['browser_routes']}")
print(f"Backend Routes      : {knowledge['summary']['backend_routes']}")
print(f"Frontend Requests   : {knowledge['summary']['frontend_requests']}")
print(f"Tests               : {knowledge['summary']['tests']}")
print(f"Potential Gaps      : {knowledge['summary']['potential_gaps']}")
print()
print(OUT)
