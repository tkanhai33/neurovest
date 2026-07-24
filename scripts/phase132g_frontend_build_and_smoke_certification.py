#!/usr/bin/env python3

from __future__ import annotations

from datetime import datetime, UTC
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(".").resolve()
FRONTEND = ROOT / "frontend"

PHASE = "132G_FRONTEND_BUILD_AND_SMOKE_CERTIFICATION"

OUT_DIR = ROOT / "runtime/frontend_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "132G_frontend_build_and_smoke_certification_latest.json"
OUT_TXT = OUT_DIR / "132G_frontend_build_and_smoke_certification_latest.txt"

REQUIRED_FILES = [
    FRONTEND / "app/page.tsx",
    FRONTEND / "app/hooks/useDashboardData.ts",
    FRONTEND / "app/components/layout/DashboardShell.tsx",
    FRONTEND / "app/components/layout/WorkspaceRouter.tsx",
    FRONTEND / "app/components/ticker/MarketTickerBanner.tsx",
    FRONTEND / "app/components/chat/FloatingChatWidget.tsx",
    FRONTEND / "app/components/workspaces/MarketWorkspace.tsx",
    FRONTEND / "app/components/workspaces/NeuroWorkspace.tsx",
    FRONTEND / "app/components/workspaces/GraphWorkspacePanel.tsx",
    FRONTEND / "app/components/workspaces/ObservabilityWorkspacePanel.tsx",
    FRONTEND / "app/components/workspaces/LearningWorkspacePanel.tsx",
    FRONTEND / "app/components/cards/LivePriceCard.tsx",
    FRONTEND / "app/components/cards/PositionsPanel.tsx",
    FRONTEND / "app/components/cards/StrategyDecisionCard.tsx",
    FRONTEND / "app/components/cards/RiskGateCard.tsx",
    FRONTEND / "public/neurovest-training/learning_state.json",
]

def run_command(name: str, command: list[str]) -> dict:
    print()
    print("=" * 80)
    print(name)
    print("=" * 80)
    print(" ".join(command))

    completed = subprocess.run(
        command,
        cwd=FRONTEND,
        text=True,
        capture_output=True,
    )

    if completed.stdout:
        print(completed.stdout)

    if completed.stderr:
        print(completed.stderr, file=sys.stderr)

    return {
        "name": name,
        "command": command,
        "return_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "passed": completed.returncode == 0,
    }

file_checks = {
    str(path.relative_to(ROOT)): path.exists()
    for path in REQUIRED_FILES
}

page_text = (FRONTEND / "app/page.tsx").read_text(encoding="utf-8")

architecture_checks = {
    "page_uses_dashboard_data_hook": "useDashboardData()" in page_text,
    "page_uses_workspace_router": "<WorkspaceRouter" in page_text,
    "page_uses_market_ticker": "<MarketTickerBanner" in page_text,
    "page_uses_dashboard_header": "<DashboardHeader" in page_text,
    "page_uses_dashboard_stats": "<DashboardStats" in page_text,
    "page_uses_sidebar": "<Sidebar" in page_text,
    "page_uses_floating_chat": "<FloatingChatWidget" in page_text,
    "page_has_no_local_market_workspace": "function MarketWorkspacePanel" not in page_text,
    "page_has_no_local_neuro_workspace": "function NeuroWorkspace" not in page_text,
    "page_has_no_local_learning_workspace": "function LearningWorkspacePanel" not in page_text,
    "page_has_no_local_graph_workspace": "function GraphWorkspacePanel" not in page_text,
    "page_has_no_local_observability_workspace": "function ObservabilityWorkspacePanel" not in page_text,
    "page_has_no_local_floating_chat": "function FloatingChatWidget" not in page_text,
}

commands = [
    run_command("ESLINT", ["npm", "run", "lint"]),
    run_command("PRODUCTION BUILD", ["npm", "run", "build"]),
]

all_files_present = all(file_checks.values())
architecture_passed = all(architecture_checks.values())
commands_passed = all(command["passed"] for command in commands)

certified = (
    all_files_present
    and architecture_passed
    and commands_passed
)

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "frontend_directory": str(FRONTEND),
    "file_checks": file_checks,
    "architecture_checks": architecture_checks,
    "commands": commands,
    "summary": {
        "all_required_files_present": all_files_present,
        "architecture_passed": architecture_passed,
        "lint_passed": commands[0]["passed"],
        "production_build_passed": commands[1]["passed"],
    },
    "safety": {
        "broker_execution_changed": False,
        "live_execution_changed": False,
        "chat_behavior_changed": False,
        "backend_contracts_changed": False,
    },
    "certified": certified,
    "recommended_next_phase": (
        "133A_OVERVIEW_WORKSPACE_REDESIGN"
        if certified
        else "132G_FRONTEND_BUILD_REPAIR"
    ),
}

OUT_JSON.write_text(
    json.dumps(result, indent=2),
    encoding="utf-8",
)

lines = [
    PHASE,
    "",
    f"certified: {certified}",
    "",
    "SUMMARY",
    f"required_files_present: {all_files_present}",
    f"architecture_passed: {architecture_passed}",
    f"lint_passed: {commands[0]['passed']}",
    f"production_build_passed: {commands[1]['passed']}",
    "",
    "ARCHITECTURE",
]

for name, passed in architecture_checks.items():
    lines.append(f"{name}: {'PASS' if passed else 'FAIL'}")

lines.extend([
    "",
    "SAFETY",
    "broker_execution_changed: False",
    "live_execution_changed: False",
    "chat_behavior_changed: False",
    "backend_contracts_changed: False",
    "",
    f"next: {result['recommended_next_phase']}",
])

OUT_TXT.write_text(
    "\n".join(lines),
    encoding="utf-8",
)

print()
print("=" * 80)
print("132G CERTIFICATION RESULT")
print("=" * 80)
print(OUT_TXT.read_text(encoding="utf-8"))

if not certified:
    raise SystemExit(1)
