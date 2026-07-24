#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
FRONTEND = ROOT / "frontend"
OUT = ROOT / "runtime/certifications/phase23a_frontend_request_normalizer_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

SERVICE_FILES = [
    ROOT / "frontend/services/marketService.ts",
    ROOT / "frontend/services/portfolioService.ts",
    ROOT / "frontend/services/strategyService.ts",
    ROOT / "frontend/services/riskService.ts",
]

def run(cmd, cwd=ROOT):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {
        "cmd": " ".join(cmd),
        "returncode": r.returncode,
        "stdout": r.stdout[-5000:],
        "stderr": r.stderr[-5000:],
    }

steps = {
    "phase22b_cert": run(["python3", "scripts/phase22b_live_graph_visualization_certification.py"]),
    "phase20f_cert": run(["python3", "scripts/phase20f_floating_chat_widget_certification.py"]),
    "patch": run(["python3", "scripts/phase23a_frontend_request_normalizer.py"]),
    "lint": run(["npm", "run", "lint"], cwd=FRONTEND),
    "build": run(["npm", "run", "build"], cwd=FRONTEND),
    "graph_reset": run(["./neuro", "graph_reset"]),
    "simulate_trade": run(["./neuro", "simulate_trade", "AAPL"]),
    "graph_validate": run(["./neuro", "graph_validate"]),
}

normalizer = ROOT / "frontend/services/requestNormalizer.ts"
normalizer_text = normalizer.read_text() if normalizer.exists() else ""
service_texts = {str(path): path.read_text() if path.exists() else "" for path in SERVICE_FILES}

checks = {
    "patch_ok": steps["patch"]["returncode"] == 0,
    "normalizer_exists": normalizer.exists(),
    "normalizer_has_cache": "responseCache" in normalizer_text,
    "normalizer_has_inflight_dedupe": "inflight" in normalizer_text,
    "normalizer_has_ttl": "ttlMs" in normalizer_text,
    "all_services_import_normalizer": all('from "./requestNormalizer"' in text for text in service_texts.values()),
    "all_services_use_normalized_request": all("normalizedJsonRequest" in text for text in service_texts.values()),
    "phase22b_certified": '"certified": true' in steps["phase22b_cert"]["stdout"],
    "phase20f_certified": '"certified": true' in steps["phase20f_cert"]["stdout"],
    "lint_ok": steps["lint"]["returncode"] == 0,
    "build_ok": steps["build"]["returncode"] == 0,
    "simulate_trade_ok": '"trade_simulated"' in steps["simulate_trade"]["stdout"],
    "graph_validate_ok": '"valid": true' in steps["graph_validate"]["stdout"],
}

certified = all(checks.values())

report = {
    "phase": "23A_FRONTEND_REQUEST_NORMALIZER_CERTIFICATION",
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
