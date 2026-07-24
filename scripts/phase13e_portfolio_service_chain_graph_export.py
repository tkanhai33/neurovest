#!/usr/bin/env python3
import json
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/repo_memory/portfolio_service_chain_graph_v1.json"

nodes = [
    {"id": "execution.paper_broker", "layer": "L4_runtime_orchestration", "file": "backend/app/stacks/execution/paper_broker.py", "role": "paper positions source"},
    {"id": "portfolio.service", "layer": "L3_service_facade", "file": "backend/app/stacks/portfolio/portfolio_service.py", "role": "backend service facade"},
    {"id": "fastapi.portfolio_route", "layer": "L5_api_presentation", "file": "backend/app/main.py", "role": "API route"},
    {"id": "frontend.portfolioService", "layer": "L6_frontend_service", "file": "frontend/services/portfolioService.ts", "role": "frontend service facade"},
    {"id": "frontend.PositionsPanel", "layer": "L6_frontend_component", "file": "frontend/app/page.tsx", "role": "positions display"},
]

edges = [
    {"from": "execution.paper_broker", "to": "portfolio.service", "type": "backend_call"},
    {"from": "portfolio.service", "to": "fastapi.portfolio_route", "type": "api_binding"},
    {"from": "fastapi.portfolio_route", "to": "frontend.portfolioService", "type": "http_proxy"},
    {"from": "frontend.portfolioService", "to": "frontend.PositionsPanel", "type": "component_data"},
]

report = {
    "phase": "13E_PORTFOLIO_SERVICE_CHAIN_GRAPH_EXPORT",
    "generated_at": datetime.now(UTC).isoformat(),
    "node_count": len(nodes),
    "edge_count": len(edges),
    "nodes": nodes,
    "edges": edges,
}

OUT.write_text(json.dumps(report, indent=2))
print(json.dumps({"phase": report["phase"], "node_count": report["node_count"], "edge_count": report["edge_count"], "output": str(OUT)}, indent=2))
