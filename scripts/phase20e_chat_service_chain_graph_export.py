#!/usr/bin/env python3
import json
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/repo_memory/chat_service_chain_graph_v1.json"

nodes = [
    {"id": "chat_public.runtime", "layer": "L4_runtime_orchestration", "file": "backend/app/stacks/chat_public/chat_runtime.py", "role": "chat runtime"},
    {"id": "fastapi.chat_route", "layer": "L5_api_presentation", "file": "backend/app/stacks/chat_public/chat_api.py", "role": "backend chat API route"},
    {"id": "frontend.chatService", "layer": "L6_frontend_service", "file": "frontend/services/chatService.ts", "role": "frontend chat service"},
    {"id": "frontend.FloatingChatWidget", "layer": "L6_frontend_component", "file": "frontend/app/page.tsx", "role": "floating chat UI"},
]

edges = [
    {"from": "chat_public.runtime", "to": "fastapi.chat_route", "type": "backend_call"},
    {"from": "fastapi.chat_route", "to": "frontend.chatService", "type": "http_proxy"},
    {"from": "frontend.chatService", "to": "frontend.FloatingChatWidget", "type": "component_data"},
]

report = {
    "phase": "20E_CHAT_SERVICE_CHAIN_GRAPH_EXPORT",
    "generated_at": datetime.now(UTC).isoformat(),
    "node_count": len(nodes),
    "edge_count": len(edges),
    "nodes": nodes,
    "edges": edges,
}

OUT.write_text(json.dumps(report, indent=2))
print(json.dumps({"phase": report["phase"], "node_count": report["node_count"], "edge_count": report["edge_count"], "output": str(OUT)}, indent=2))
