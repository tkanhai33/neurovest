#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
FRONTEND = ROOT / "frontend"
OUT = ROOT / "runtime/certifications/phase13f_portfolio_positions_service_chain_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

GRAPH = ROOT / "runtime/repo_memory/portfolio_service_chain_graph_v1.json"

def run(cmd, cwd=ROOT):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {"cmd": " ".join(cmd), "returncode": r.returncode, "stdout": r.stdout[-5000:], "stderr": r.stderr[-5000:]}

steps = {
    "patch": run(["python3", "scripts/phase13_portfolio_positions_service_chain.py"]),
    "compile_paper": run(["python3", "-m", "py_compile", "backend/app/stacks/execution/paper_broker.py"]),
    "compile_service": run(["python3", "-m", "py_compile", "backend/app/stacks/portfolio/portfolio_service.py"]),
    "compile_main": run(["python3", "-m", "py_compile", "backend/app/main.py"]),
    "graph_export": run(["python3", "scripts/phase13e_portfolio_service_chain_graph_export.py"]),
    "lint": run(["npm", "run", "lint"], cwd=FRONTEND),
    "build": run(["npm", "run", "build"], cwd=FRONTEND),
    "graph_reset": run(["./neuro", "graph_reset"]),
    "simulate_trade": run(["./neuro", "simulate_trade", "AAPL"]),
    "graph_validate": run(["./neuro", "graph_validate"]),
}

files = {
    "paper": ROOT / "backend/app/stacks/execution/paper_broker.py",
    "service": ROOT / "backend/app/stacks/portfolio/portfolio_service.py",
    "main": ROOT / "backend/app/main.py",
    "frontend_service": ROOT / "frontend/services/portfolioService.ts",
    "next_route": ROOT / "frontend/app/api/v1/portfolio/positions/route.ts",
    "page": ROOT / "frontend/app/page.tsx",
}

texts = {k: v.read_text() if v.exists() else "" for k, v in files.items()}
graph = json.loads(GRAPH.read_text()) if GRAPH.exists() else {}

checks = {
    "patch_ok": steps["patch"]["returncode"] == 0,
    "paper_helper_exists": "get_positions_snapshot" in texts["paper"],
    "backend_service_exists": files["service"].exists(),
    "backend_service_compiles": steps["compile_service"]["returncode"] == 0,
    "main_route_exists": '"/api/v1/portfolio/positions"' in texts["main"],
    "frontend_service_exists": files["frontend_service"].exists(),
    "frontend_service_has_getPortfolioPositions": "getPortfolioPositions" in texts["frontend_service"],
    "next_proxy_exists": files["next_route"].exists(),
    "page_imports_portfolio_service": "getPortfolioPositions" in texts["page"],
    "service_graph_exists": GRAPH.exists(),
    "service_graph_node_count_ok": graph.get("node_count") == 5,
    "service_graph_edge_count_ok": graph.get("edge_count") == 4,
    "lint_ok": steps["lint"]["returncode"] == 0,
    "build_ok": steps["build"]["returncode"] == 0,
    "simulate_trade_ok": '"trade_simulated"' in steps["simulate_trade"]["stdout"],
    "graph_validate_ok": '"valid": true' in steps["graph_validate"]["stdout"],
}

certified = all(checks.values())

report = {
    "phase": "13F_PORTFOLIO_POSITIONS_SERVICE_CHAIN_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "service_graph": str(GRAPH.relative_to(ROOT)) if GRAPH.exists() else None,
    "steps": steps,
}

OUT.write_text(json.dumps(report, indent=2))
print(json.dumps({"phase": report["phase"], "certified": certified, "checks": checks, "service_graph": report["service_graph"], "output": str(OUT)}, indent=2))

if not certified:
    sys.exit(1)
