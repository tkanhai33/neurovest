#!/usr/bin/env python3
import json
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/repo_memory/strategy_service_chain_graph_v1.json"

nodes = [
    {"id": "strategy.engine", "layer": "L2_domain", "file": "backend/app/stacks/strategy/engine.py", "role": "decision engine"},
    {"id": "strategy.service", "layer": "L3_service_facade", "file": "backend/app/stacks/strategy/strategy_service.py", "role": "backend service facade"},
    {"id": "fastapi.strategy_route", "layer": "L5_api_presentation", "file": "backend/app/main.py", "role": "API route"},
    {"id": "frontend.strategyService", "layer": "L6_frontend_service", "file": "frontend/services/strategyService.ts", "role": "frontend service facade"},
    {"id": "frontend.StrategyDecisionCard", "layer": "L6_frontend_component", "file": "frontend/app/page.tsx", "role": "strategy decision display"},
]

edges = [
    {"from": "strategy.engine", "to": "strategy.service", "type": "backend_call"},
    {"from": "strategy.service", "to": "fastapi.strategy_route", "type": "api_binding"},
    {"from": "fastapi.strategy_route", "to": "frontend.strategyService", "type": "http_proxy"},
    {"from": "frontend.strategyService", "to": "frontend.StrategyDecisionCard", "type": "component_data"},
]

report = {
    "phase": "14E_STRATEGY_SERVICE_CHAIN_GRAPH_EXPORT",
    "generated_at": datetime.now(UTC).isoformat(),
    "node_count": len(nodes),
    "edge_count": len(edges),
    "nodes": nodes,
    "edges": edges,
}

OUT.write_text(json.dumps(report, indent=2))
print(json.dumps({"phase": report["phase"], "node_count": report["node_count"], "edge_count": report["edge_count"], "output": str(OUT)}, indent=2))
