#!/usr/bin/env python3
import json
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/repo_memory/service_chain_graph_v1.json"

nodes = [
    {
        "id": "market_data.feed",
        "layer": "L2_domain",
        "file": "backend/app/stacks/market_data/feed.py",
        "role": "provider-facing quote helper",
    },
    {
        "id": "market_data.service",
        "layer": "L3_service_facade",
        "file": "backend/app/stacks/market_data/market_data_service.py",
        "role": "backend service facade",
    },
    {
        "id": "fastapi.market_route",
        "layer": "L5_api_presentation",
        "file": "backend/app/main.py",
        "role": "API route",
    },
    {
        "id": "frontend.marketService",
        "layer": "L6_frontend_service",
        "file": "frontend/services/marketService.ts",
        "role": "frontend service facade",
    },
    {
        "id": "frontend.LivePriceCard",
        "layer": "L6_frontend_component",
        "file": "frontend/app/page.tsx",
        "role": "single symbol display",
    },
    {
        "id": "frontend.LiveMarketWatchlist",
        "layer": "L6_frontend_component",
        "file": "frontend/app/page.tsx",
        "role": "watchlist display",
    },
]

edges = [
    {"from": "market_data.feed", "to": "market_data.service", "type": "backend_call"},
    {"from": "market_data.service", "to": "fastapi.market_route", "type": "api_binding"},
    {"from": "fastapi.market_route", "to": "frontend.marketService", "type": "http_proxy"},
    {"from": "frontend.marketService", "to": "frontend.LivePriceCard", "type": "component_data"},
    {"from": "frontend.marketService", "to": "frontend.LiveMarketWatchlist", "type": "component_data"},
]

report = {
    "phase": "12E_SERVICE_CHAIN_GRAPH_EXPORT",
    "generated_at": datetime.now(UTC).isoformat(),
    "node_count": len(nodes),
    "edge_count": len(edges),
    "nodes": nodes,
    "edges": edges,
}

OUT.write_text(json.dumps(report, indent=2))

print(json.dumps({
    "phase": report["phase"],
    "node_count": report["node_count"],
    "edge_count": report["edge_count"],
    "output": str(OUT),
}, indent=2))
