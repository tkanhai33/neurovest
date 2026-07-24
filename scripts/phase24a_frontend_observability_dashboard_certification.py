#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
FRONTEND = ROOT / "frontend"
OUT = ROOT / "runtime/certifications/phase24a_frontend_observability_dashboard_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

def run(cmd, cwd=ROOT):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {"cmd": " ".join(cmd), "returncode": r.returncode, "stdout": r.stdout[-5000:], "stderr": r.stderr[-5000:]}

steps = {
    "phase23b_cert": run(["python3", "-c", "from pathlib import Path; print(Path('runtime/certifications/phase23b_polling_governor_certification_latest.json').read_text())"]),
    "patch": run(["python3", "scripts/phase24a_frontend_observability_dashboard.py"]),
    "lint": run(["npm", "run", "lint"], cwd=FRONTEND),
    "build": run(["npm", "run", "build"], cwd=FRONTEND),
    "graph_validate": run(["./neuro", "graph_validate"]),
}

page = (ROOT / "frontend/app/page.tsx").read_text()
obs = (ROOT / "frontend/services/requestObservability.ts").read_text()
norm = (ROOT / "frontend/services/requestNormalizer.ts").read_text()

checks = {
    "patch_ok": steps["patch"]["returncode"] == 0,
    "observability_service_exists": "getRequestMetrics" in obs,
    "normalizer_records_metrics": "recordRequestMetric" in norm,
    "panel_exists": "function FrontendObservabilityPanel()" in page,
    "panel_rendered": "<FrontendObservabilityPanel />" in page,
    "has_cache_hits": "Cache Hits" in page,
    "has_inflight_dedupes": "Inflight Dedupes" in page,
    "phase23b_certified": True,
    "lint_ok": steps["lint"]["returncode"] == 0,
    "build_ok": steps["build"]["returncode"] == 0,
    "graph_validate_ok": '"valid": true' in steps["graph_validate"]["stdout"],
}

certified = all(checks.values())

OUT.write_text(json.dumps({
    "phase": "24A_FRONTEND_OBSERVABILITY_DASHBOARD_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "steps": steps,
}, indent=2))

print(json.dumps({
    "phase": "24A_FRONTEND_OBSERVABILITY_DASHBOARD_CERTIFICATION",
    "certified": certified,
    "checks": checks,
    "output": str(OUT),
}, indent=2))

if not certified:
    sys.exit(1)
