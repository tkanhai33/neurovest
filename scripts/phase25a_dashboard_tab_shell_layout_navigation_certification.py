#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
FRONTEND = ROOT / "frontend"
OUT = ROOT / "runtime/certifications/phase25a_dashboard_tab_shell_layout_navigation_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

def run(cmd, cwd=ROOT):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {
        "cmd": " ".join(cmd),
        "returncode": r.returncode,
        "stdout": r.stdout[-5000:],
        "stderr": r.stderr[-5000:],
    }

steps = {
    "phase24d_cert": run(
        ["python3", "scripts/phase24d_observability_lock_handoff_snapshot.py"]
    ),
    "patch": run(
        ["python3", "scripts/phase25a_dashboard_tab_shell_layout_navigation.py"]
    ),
    "lint": run(["npm", "run", "lint"], cwd=FRONTEND),
    "build": run(["npm", "run", "build"], cwd=FRONTEND),
    "graph_validate": run(["./neuro", "graph_validate"]),
}

page = (ROOT / "frontend/app/page.tsx").read_text()

checks = {
    "phase24d_certified": '"certified": true'
    in steps["phase24d_cert"]["stdout"],
    "patch_ok": steps["patch"]["returncode"] == 0,
    "dashboard_tab_type_exists": "type DashboardTab" in page,
    "navigation_component_exists": "function DashboardTabNavigation" in page,
    "active_tab_state_exists": "const [activeTab, setActiveTab]" in page,
    "overview_tab_exists": '"overview"' in page,
    "market_tab_exists": '"market"' in page,
    "graph_tab_exists": '"graph"' in page,
    "observability_tab_exists": '"observability"' in page,
    "chat_tab_exists": '"chat"' in page,
    "navigation_rendered": "<DashboardTabNavigation" in page,
    "lint_ok": steps["lint"]["returncode"] == 0,
    "build_ok": steps["build"]["returncode"] == 0,
    "graph_validate_ok": '"valid": true'
    in steps["graph_validate"]["stdout"],
}

certified = all(checks.values())

report = {
    "phase": "25A_DASHBOARD_TAB_SHELL_LAYOUT_NAVIGATION_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "steps": steps,
}

OUT.write_text(json.dumps(report, indent=2))

print(
    json.dumps(
        {
            "phase": report["phase"],
            "certified": certified,
            "checks": checks,
            "output": str(OUT),
        },
        indent=2,
    )
)

if not certified:
    sys.exit(1)
