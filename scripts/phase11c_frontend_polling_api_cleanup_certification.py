#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase11c_frontend_polling_api_cleanup_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

PAGE = ROOT / "frontend/app/page.tsx"

def run(cmd):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return {
        "cmd": " ".join(cmd),
        "returncode": r.returncode,
        "stdout": r.stdout[-4000:],
        "stderr": r.stderr[-4000:],
    }

steps = {
    "patch": run(["python3", "scripts/phase11c_frontend_polling_api_cleanup.py"]),
    "api_bridge_cert": run(["python3", "scripts/phase11_live_market_price_api_bridge_certification.py"]),
    "frontend_card_cert": run(["python3", "scripts/phase11b_frontend_live_price_card_certification.py"]),
    "graph_reset": run(["./neuro", "graph_reset"]),
    "simulate_trade": run(["./neuro", "simulate_trade", "AAPL"]),
    "graph_validate": run(["./neuro", "graph_validate"]),
}

text = PAGE.read_text() if PAGE.exists() else ""

checks = {
    "patch_ok": steps["patch"]["returncode"] == 0,
    "page_exists": PAGE.exists(),
    "relative_api_used": "/api/v1/market/live-price/${cleanSymbol}" in text,
    "hardcoded_backend_removed": "http://127.0.0.1:8000/api/v1/market/live-price" not in text,
    "polling_dependency_symbol": "}, [symbol]);" in text,
    "api_bridge_certified": '"certified": true' in steps["api_bridge_cert"]["stdout"],
    "frontend_card_certified": '"certified": true' in steps["frontend_card_cert"]["stdout"],
    "simulate_trade_ok": '"trade_simulated"' in steps["simulate_trade"]["stdout"],
    "graph_validate_ok": '"valid": true' in steps["graph_validate"]["stdout"],
}

certified = all(checks.values())

report = {
    "phase": "11C_FRONTEND_POLLING_API_CLEANUP_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "steps": steps,
}

OUT.write_text(json.dumps(report, indent=2))

print(json.dumps({
    "phase": report["phase"],
    "certified": certified,
    "checks": checks,
    "output": str(OUT),
}, indent=2))

if not certified:
    sys.exit(1)
