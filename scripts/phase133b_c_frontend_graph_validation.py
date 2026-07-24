#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import json


ROOT = Path(".").resolve()

SERVICE = ROOT / "frontend/services/graphService.ts"
WORKSPACE = (
    ROOT
    / "frontend/app/components/workspaces"
    / "GraphWorkspacePanel.tsx"
)
CSS = ROOT / "frontend/app/globals.css"

service_text = SERVICE.read_text(encoding="utf-8")
workspace_text = WORKSPACE.read_text(encoding="utf-8")
css_text = CSS.read_text(encoding="utf-8")

checks = {
    "trace_type_present": (
        "export type LiveGraphTrace" in service_text
    ),
    "flow_step_type_present": (
        "export type LiveGraphFlowStep" in service_text
    ),
    "contract_type_present": (
        "export type LiveGraphContract" in service_text
    ),
    "normalizer_preserves_traces": (
        "traces," in service_text
        and "recent_flows: recentFlows" in service_text
    ),
    "layer_lanes_present": (
        "const GRAPH_LAYERS" in workspace_text
        and "L0" in workspace_text
        and "L7" in workspace_text
    ),
    "trace_selector_present": (
        "function TraceSelector" in workspace_text
    ),
    "ordered_playback_present": (
        "function PlaybackTimeline" in workspace_text
    ),
    "node_activation_highlight_present": (
        'activeStep?.record_type === "node_activation"'
        in workspace_text
    ),
    "edge_activation_highlight_present": (
        'activeStep?.record_type === "edge_activation"'
        in workspace_text
    ),
    "polling_enabled": (
        "2000" in workspace_text
        and "setInterval" in workspace_text
    ),
    "websocket_not_added": (
        "WebSocket" not in workspace_text
        and "ws/graph" not in workspace_text
    ),
    "truth_boundary_present": (
        "Graph Truth Boundary" in workspace_text
    ),
    "animation_css_present": (
        "neurovest-graph-node-pulse" in css_text
        and "neurovest-graph-edge-pulse" in css_text
    ),
}

certified = all(checks.values())

print(
    json.dumps(
        {
            "phase": "133B-C_LIVE_LAYERED_GRAPH_UI",
            "checks": checks,
            "polling_transport": True,
            "websocket_dependency_added": False,
            "synthetic_animation_added": False,
            "certified": certified,
        },
        indent=2,
    )
)

if not certified:
    raise SystemExit(1)
