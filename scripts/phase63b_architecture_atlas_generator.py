#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import ast
import json
import re
from collections import defaultdict

ROOT = Path(".").resolve()
HANDOFF = ROOT / "handoff"
BIBLE = HANDOFF / "project_bible"
OUT = BIBLE / "architecture_atlas"

PHASE = "63B_ARCHITECTURE_ATLAS_GENERATOR"

OUT.mkdir(parents=True, exist_ok=True)

IGNORE_DIRS = {
    ".git", ".venv", "__pycache__", ".pytest_cache",
    "node_modules", ".next", "dist", "build", "coverage",
    "quarantine_artifacts",
}

def ignored(path: Path) -> bool:
    return bool(set(path.parts) & IGNORE_DIRS)

def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))

def read(path: Path, fallback: str = "") -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return fallback

def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")

def section(title: str, body: str) -> str:
    return f"\n\n# {title}\n\n{body.strip()}\n"

def detect_stack(path: str) -> str:
    m = re.search(r"backend/app/stacks/([^/]+)", path)
    if m:
        return m.group(1)
    if path.startswith("frontend/"):
        return "frontend"
    if path.startswith("runtime/strategy_candidate_sandbox"):
        return "strategy_candidate_sandbox_artifacts"
    if path.startswith("runtime/certifications"):
        return "runtime_certifications"
    if path.startswith("scripts/"):
        return "phase_scripts"
    if path.startswith("audit/"):
        return "audit"
    return "root_or_misc"

def py_imports(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:
        return []

    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                found.append(n.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                found.append(node.module)
    return sorted(set(found))

def collect_import_edges() -> dict:
    edges = defaultdict(set)
    file_edges = {}

    for path in ROOT.rglob("*.py"):
        if ignored(path):
            continue
        r = rel(path)
        source_stack = detect_stack(r)
        imports = py_imports(path)
        file_edges[r] = imports

        for imp in imports:
            if imp.startswith("backend.app.stacks."):
                parts = imp.split(".")
                if len(parts) >= 4:
                    edges[source_stack].add(parts[3])
            elif imp.startswith("app.stacks."):
                parts = imp.split(".")
                if len(parts) >= 3:
                    edges[source_stack].add(parts[2])
            elif "snaptrade" in imp.lower():
                edges[source_stack].add("snaptrade")
            elif "yfinance" in imp.lower():
                edges[source_stack].add("market_data")

    return {
        "stack_edges": {k: sorted(v) for k, v in sorted(edges.items())},
        "file_imports": file_edges,
    }

def collect_phase_artifacts() -> list[dict]:
    rows = []
    for folder in [ROOT / "runtime/strategy_candidate_sandbox", ROOT / "runtime/certifications", ROOT / "audit"]:
        if not folder.exists():
            continue
        for path in sorted(folder.rglob("*.json")):
            if ignored(path):
                continue
            data = read_json(path)
            rows.append({
                "file": rel(path),
                "phase": data.get("phase", path.stem),
                "created_at": data.get("created_at"),
                "certified": data.get("certified"),
                "stage": data.get("stage"),
                "source_phase": data.get("source_phase"),
                "latest_confirmed_phase": data.get("latest_confirmed_phase"),
                "next": (
                    data.get("next_recommended_phase")
                    or data.get("pipeline_summary", {}).get("next_recommended_phase")
                    or data.get("handoff_snapshot", {}).get("next_recommended_phase")
                ),
            })
    return rows

def phase_num(phase: str) -> int:
    m = re.search(r"(\d+)", str(phase))
    return int(m.group(1)) if m else 999999

def group_phase(phase: str) -> str:
    n = phase_num(phase)
    if n <= 30:
        return "Foundation / Provider / Candidate Prep"
    if 31 <= n <= 32:
        return "Historical Replay + Metrics"
    if 33 <= n <= 35:
        return "Trade Simulation Contracts + Entry/Exit Disabled"
    if 36 <= n <= 40:
        return "Sandbox Gates + Dependency Trace"
    if 41 <= n <= 48:
        return "Qwen Read-Only Context + Response Validation"
    if 49 <= n <= 55:
        return "Qwen Session / Bridge / Loop / State Machine"
    if 56 <= n <= 58:
        return "Qwen Policy Matrix + Context Package"
    if 59 <= n <= 61:
        return "Terminal Freeze + Archive"
    if n == 62:
        return "Master Handoff Snapshot"
    if n == 63:
        return "Documentation Compiler"
    return "Other"

def build_condensed_timeline(rows: list[dict]) -> str:
    groups = defaultdict(list)
    for r in sorted(rows, key=lambda x: (phase_num(x.get("phase")), str(x.get("phase")))):
        groups[group_phase(r.get("phase"))].append(r)

    lines = []
    for group, items in groups.items():
        lines.append(f"## {group}")
        lines.append("")
        for r in items:
            mark = "✅" if r.get("certified") is True else "⚠️" if r.get("certified") is False else "•"
            stage = r.get("stage") or r.get("latest_confirmed_phase") or ""
            lines.append(f"{mark} **{r.get('phase')}**")
            if stage:
                lines.append(f"   - {stage}")
            if r.get("next"):
                lines.append(f"   - next: `{r.get('next')}`")
            lines.append(f"   - evidence: `{r.get('file')}`")
            lines.append("")
    return "\n".join(lines)

def stack_ownership(stack_topology: dict) -> str:
    lines = []
    for stack, info in sorted(stack_topology.items()):
        files = info.get("sample_files", [])
        lines.append(f"## {stack}")
        lines.append("")
        lines.append(f"Files detected: {info.get('file_count')}")
        lines.append("")
        lines.append("Owns:")
        if stack in {"market_data"}:
            lines.append("- provider routing, bars, price, sessions, market data service")
        elif stack in {"strategy"}:
            lines.append("- strategy contracts, decisions, indicators, signal rules")
        elif stack in {"risk"}:
            lines.append("- drawdown, exposure, loss streak, kill switch, risk service")
        elif stack in {"execution"}:
            lines.append("- paper broker, ledger, fills, commissions, sandbox runtime")
        elif stack in {"portfolio"}:
            lines.append("- allocation, accounting, positions, dashboard data")
        elif stack in {"chat"}:
            lines.append("- chat runtime, memory, prompts, Qwen/Ollama-facing chat layer")
        elif stack in {"learning"}:
            lines.append("- replay research, Monte Carlo, probability, evaluator logic")
        else:
            lines.append("- stack-specific files detected by topology scan")
        lines.append("")
        lines.append("Must not own:")
        lines.append("- unrelated stack mutation")
        lines.append("- broker/live execution unless explicitly certified")
        lines.append("- cross-layer shortcuts")
        lines.append("")
        lines.append("Sample files:")
        for f in files[:12]:
            lines.append(f"- `{f}`")
        lines.append("")
    return "\n".join(lines)

def layer_ownership(layer_map: dict) -> str:
    rules = {
        "L0_external_adapter": "External providers and adapters only.",
        "L1_security_auth_safety": "Auth, gates, guards, firewalls, locked safety contracts.",
        "L2_domain": "Pure business/domain logic and contracts.",
        "L3_service_facade": "Stable services coordinating domain/adapters.",
        "L4_runtime_orchestration": "Controllers, schedulers, runtime orchestration.",
        "L5_api_presentation": "API routes and presentation only.",
        "L6_frontend": "Next.js UI and client services.",
        "L7_tests": "Tests, fixtures, probes, validation.",
        "UNCLASSIFIED": "Needs future classification; do not assume ownership.",
    }
    lines = []
    for layer, info in sorted(layer_map.items()):
        lines.append(f"## {layer}")
        lines.append("")
        lines.append(rules.get(layer, "Layer detected by scan."))
        lines.append(f"Files detected: {info.get('file_count')}")
        lines.append("")
        for f in info.get("sample_files", [])[:15]:
            lines.append(f"- `{f}`")
        lines.append("")
    return "\n".join(lines)

stack_topology = read_json(HANDOFF / "topology_summary.json").get("stacks", {})
stack_topology_full = read_json(HANDOFF / "stack_topology.txt")
layer_topology_full = read_json(HANDOFF / "canonical_layer_map.txt")

rows = collect_phase_artifacts()
imports = collect_import_edges()

condensed_timeline = build_condensed_timeline(rows)
stack_guide = stack_ownership(stack_topology_full)
layer_guide = layer_ownership(layer_topology_full)

node_map = read(HANDOFF / "runtime_node_graph.txt")
dependency_graph = read(HANDOFF / "dependency_graph.txt")
state_machine = read(HANDOFF / "runtime_state_machine.txt")

architecture_atlas = ""
architecture_atlas += section("Architecture Atlas Overview", f"""
Generated: {datetime.now(UTC).isoformat()}
Controller: {PHASE}
Mode: READ ONLY ATLAS COMPILER

This atlas explains NeuroVest topology, ownership, flow, and certification history using existing repository and handoff evidence only.
""")
architecture_atlas += section("Expanded Node Map", f"```text\n{node_map}\n```")
architecture_atlas += section("Dependency Graph", f"```text\n{dependency_graph}\n```")
architecture_atlas += section("Runtime State Machine", f"```text\n{state_machine}\n```")
architecture_atlas += section("Stack Ownership", stack_guide)
architecture_atlas += section("Layer Ownership", layer_guide)
architecture_atlas += section("Condensed Certification Timeline", condensed_timeline)
architecture_atlas += section("Import Dependency Atlas", f"```json\n{json.dumps(imports['stack_edges'], indent=2)}\n```")
architecture_atlas += section("Future Workstream Order", """
1. LLM orchestration architecture.
2. Permission request model.
3. Sandbox runtime activation plan.
4. Candidate lifecycle hardening.
5. Learning and promotion approval chain.
6. Broker/live execution safety model.

Do not continue the Qwen read-only certification chain. It is terminal-frozen.
""")

write(OUT / "ARCHITECTURE_ATLAS.md", architecture_atlas)
write(OUT / "PHASE_TIMELINE.md", condensed_timeline)
write(OUT / "STACK_OWNERSHIP.md", stack_guide)
write(OUT / "LAYER_OWNERSHIP.md", layer_guide)
write(OUT / "IMPORT_DEPENDENCY_ATLAS.json", json.dumps(imports, indent=2))

flows_dir = OUT / "FLOWS"
topology_dir = OUT / "TOPOLOGY"
flows_dir.mkdir(exist_ok=True)
topology_dir.mkdir(exist_ok=True)

write(flows_dir / "market_data.md", """# Market Data Flow

External Provider
    ↓
L0 Adapter
    ↓
Provider Registry / Router
    ↓
Market Data Service
    ↓
Bars / Price
    ↓
Replay / Sandbox
""")

write(flows_dir / "candidate_pipeline.md", """# Candidate Pipeline

Idea / Chat / Research
    ↓
Proposal Capture
    ↓
Candidate Sandbox
    ↓
Historical Replay
    ↓
Metrics
    ↓
Scorecard
    ↓
Manual Promotion Gate
""")

write(flows_dir / "execution_disabled.md", """# Execution Flow — Disabled

Strategy Decision
    ↓
Risk Gate
    ↓
Simulation Gate
    ↓
Paper Broker / Broker
    ↓
Ledger

Current certified state: disabled / locked.
""")

write(topology_dir / "node_graph.md", f"# Node Graph\n\n```text\n{node_map}\n```\n")
write(topology_dir / "dependency_graph.md", f"# Dependency Graph\n\n```text\n{dependency_graph}\n```\n")
write(topology_dir / "stack_graph.json", json.dumps(stack_topology_full, indent=2))

index = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_ATLAS_COMPILER",
    "output_dir": str(OUT),
    "phase_artifacts_scanned": len(rows),
    "python_import_files_scanned": len(imports["file_imports"]),
    "generated_files": [
        "ARCHITECTURE_ATLAS.md",
        "PHASE_TIMELINE.md",
        "STACK_OWNERSHIP.md",
        "LAYER_OWNERSHIP.md",
        "IMPORT_DEPENDENCY_ATLAS.json",
        "FLOWS/market_data.md",
        "FLOWS/candidate_pipeline.md",
        "FLOWS/execution_disabled.md",
        "TOPOLOGY/node_graph.md",
        "TOPOLOGY/dependency_graph.md",
        "TOPOLOGY/stack_graph.json",
    ],
    "certified": True,
}

write(OUT / "ARCHITECTURE_ATLAS.json", json.dumps(index, indent=2))

print(json.dumps(index, indent=2))
print(f"\nWROTE ARCHITECTURE ATLAS PACKAGE: {OUT}")
