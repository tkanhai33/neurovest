#!/usr/bin/env python3
import json
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/repo_memory/risk_service_chain_graph_v1.json"

nodes = [
    {"id": "risk.drawdown_guard", "layer": "L1_security_auth_safety", "file": "backend/app/stacks/risk/drawdown_guard.py", "role": "risk gate source"},
    {"id": "risk.service", "layer": "L3_service_facade", "file": "backend/app/stacks/risk/risk_service.py", "role": "backend service facade"},
    {"id": "fastapi.risk_route", "layer": "L5_api_presentation", "file": "backend/app/main.py", "role": "API route"},
    {"id": "frontend.riskService", "layer": "L6_frontend_service", "file": "frontend/services/riskService.ts", "role": "frontend service facade"},
    {"id": "frontend.RiskGateCard", "layer": "L6_frontend_component", "file": "frontend/app/page.tsx", "role": "risk gate display"},
]

edges = [
    {"from": "risk.drawdown_guard", "to": "risk.service", "type": "backend_call"},
    {"from": "risk.service", "to": "fastapi.risk_route", "type": "api_binding"},
    {"from": "fastapi.risk_route", "to": "frontend.riskService", "type": "http_proxy"},
    {"from": "frontend.riskService", "to": "frontend.RiskGateCard", "type": "component_data"},
]

report = {
    "phase": "15E_RISK_SERVICE_CHAIN_GRAPH_EXPORT",
    "generated_at": datetime.now(UTC).isoformat(),
    "node_count": len(nodes),
    "edge_count": len(edges),
    "nodes": nodes,
    "edges": edges,
}

OUT.write_text(json.dumps(report, indent=2))
print(json.dumps({"phase": report["phase"], "node_count": report["node_count"], "edge_count": report["edge_count"], "output": str(OUT)}, indent=2))
