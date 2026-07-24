#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
FRONTEND = ROOT / "frontend"
OUT = ROOT / "runtime/certifications/phase25c_split_dashboard_panels_into_tab_workspaces_certification_latest.json"
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
    "phase25b_cert": run(["python3", "scripts/phase25b_tab_layout_polish_chat_panel_certification.py"]),
    "patch": run(["python3", "scripts/phase25c_split_dashboard_panels_into_tab_workspaces.py"]),
    "lint": run(["npm", "run", "lint"], cwd=FRONTEND),
    "build": run(["npm", "run", "build"], cwd=FRONTEND),
    "graph_validate": run(["./neuro", "graph_validate"]),
}

page = (ROOT / "frontend/app/page.tsx").read_text()

checks = {
    "phase25b_certified": '"certified": true' in steps["phase25b_cert"]["stdout"],
    "patch_ok": steps["patch"]["returncode"] == 0,
    "market_workspace_exists": "function MarketWorkspacePanel" in page,
    "graph_workspace_exists": "function GraphWorkspacePanel" in page,
    "observability_workspace_exists": "function ObservabilityWorkspacePanel" in page,
    "market_workspace_rendered": "<MarketWorkspacePanel positions={positions} />" in page,
    "graph_workspace_rendered": "<GraphWorkspacePanel />" in page,
    "observability_workspace_rendered": "<ObservabilityWorkspacePanel />" in page,
    "chat_panel_rendered": "<ChatTabPanel />" in page,
    "floating_chat_still_rendered": "<FloatingChatWidget />" in page,
    "navigation_not_duplicated": page.count("function DashboardTabNavigation(") == 1,
    "lint_ok": steps["lint"]["returncode"] == 0,
    "build_ok": steps["build"]["returncode"] == 0,
    "graph_validate_ok": '"valid": true' in steps["graph_validate"]["stdout"],
}

certified = all(checks.values())

report = {
    "phase": "25C_SPLIT_DASHBOARD_PANELS_INTO_TAB_WORKSPACES_CERTIFICATION",
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
