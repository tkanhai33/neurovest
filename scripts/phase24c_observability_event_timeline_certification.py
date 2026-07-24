#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
FRONTEND = ROOT / "frontend"
OUT = ROOT / "runtime/certifications/phase24c_observability_event_timeline_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

def run(cmd, cwd=ROOT):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {"cmd": " ".join(cmd), "returncode": r.returncode, "stdout": r.stdout[-5000:], "stderr": r.stderr[-5000:]}

steps = {
    "phase24b_cert": run(["python3", "scripts/phase24b_persist_observability_backend_health_certification.py"]),
    "patch": run(["python3", "scripts/phase24c_observability_event_timeline.py"]),
    "lint": run(["npm", "run", "lint"], cwd=FRONTEND),
    "build": run(["npm", "run", "build"], cwd=FRONTEND),
    "graph_validate": run(["./neuro", "graph_validate"]),
}

page = (ROOT / "frontend/app/page.tsx").read_text()
timeline = (ROOT / "frontend/services/observabilityTimelineService.ts").read_text()

checks = {
    "phase24b_certified": '"certified": true' in steps["phase24b_cert"]["stdout"],
    "patch_ok": steps["patch"]["returncode"] == 0,
    "timeline_service_exists": "getObservabilityTimeline" in timeline,
    "timeline_reads_request_metrics": "getRequestMetrics" in timeline,
    "timeline_reads_live_graph": "getLiveGraph" in timeline,
    "timeline_component_exists": "function ObservabilityEventTimeline()" in page,
    "timeline_rendered": "<ObservabilityEventTimeline />" in page,
    "timeline_title_exists": "Recent Frontend + Runtime Events" in page,
    "lint_ok": steps["lint"]["returncode"] == 0,
    "build_ok": steps["build"]["returncode"] == 0,
    "graph_validate_ok": '"valid": true' in steps["graph_validate"]["stdout"],
}

certified = all(checks.values())

report = {
    "phase": "24C_OBSERVABILITY_EVENT_TIMELINE_CERTIFICATION",
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
