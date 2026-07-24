#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase11b_frontend_live_price_card_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

candidates = [
    ROOT / "frontend/app/page.tsx",
    ROOT / "frontend/src/app/page.tsx",
    ROOT / "app/page.tsx",
    ROOT / "src/app/page.tsx",
]

target = next((p for p in candidates if p.exists()), None)

def run(cmd):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return {
        "cmd": " ".join(cmd),
        "returncode": r.returncode,
        "stdout": r.stdout[-4000:],
        "stderr": r.stderr[-4000:],
    }

steps = {
    "patch": run(["python3", "scripts/phase11b_frontend_live_price_card.py"]),
    "api_bridge_cert": run(["python3", "scripts/phase11_live_market_price_api_bridge_certification.py"]),
    "graph_reset": run(["./neuro", "graph_reset"]),
    "simulate_trade": run(["./neuro", "simulate_trade", "AAPL"]),
    "graph_validate": run(["./neuro", "graph_validate"]),
}

text = target.read_text() if target else ""

checks = {
    "target_found": target is not None,
    "patch_ok": steps["patch"]["returncode"] == 0,
    "component_exists": "function LivePriceCard()" in text,
    "component_rendered": "<LivePriceCard />" in text,
    "endpoint_used": "/api/v1/market/live-price/" in text,
    "api_bridge_certified": '"certified": true' in steps["api_bridge_cert"]["stdout"],
    "simulate_trade_ok": '"trade_simulated"' in steps["simulate_trade"]["stdout"],
    "graph_validate_ok": '"valid": true' in steps["graph_validate"]["stdout"],
}

certified = all(checks.values())

report = {
    "phase": "11B_FRONTEND_LIVE_PRICE_CARD_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "target": str(target.relative_to(ROOT)) if target else None,
    "steps": steps,
}

OUT.write_text(json.dumps(report, indent=2))

print(json.dumps({
    "phase": report["phase"],
    "certified": certified,
    "target": report["target"],
    "checks": checks,
    "output": str(OUT),
}, indent=2))

if not certified:
    sys.exit(1)
