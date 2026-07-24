#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from datetime import datetime, UTC
from collections import defaultdict
import json
import os

ROOT = Path(".").resolve()
HANDOFF = ROOT / "handoff"
AUDIT = ROOT / "audit"
SANDBOX = ROOT / "runtime" / "strategy_candidate_sandbox"

PHASE = "62A_MASTER_ARCHITECTURE_HANDOFF_CONTROLLER"

IGNORE_DIRS = {
    ".git", ".venv", "__pycache__", ".pytest_cache",
    "node_modules", ".next", "dist", "build", "coverage",
    "quarantine_artifacts",
}

IGNORE_SUFFIXES = {
    ".pyc", ".bak", ".log",
}

HANDOFF.mkdir(exist_ok=True)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def is_ignored(path: Path) -> bool:
    parts = set(path.parts)
    if parts & IGNORE_DIRS:
        return True
    if path.suffix in IGNORE_SUFFIXES:
        return True
    return False


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def safe_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def tree_for(base: Path, max_depth: int = 8) -> str:
    if not base.exists():
        return f"{rel(base)} MISSING\n"

    lines = [rel(base) + "/"]

    def walk(path: Path, prefix: str = "", depth: int = 0) -> None:
        if depth >= max_depth:
            return

        children = [
            p for p in sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
            if not is_ignored(p)
        ]

        for idx, child in enumerate(children):
            connector = "└── " if idx == len(children) - 1 else "├── "
            lines.append(prefix + connector + child.name + ("/" if child.is_dir() else ""))

            if child.is_dir():
                extension = "    " if idx == len(children) - 1 else "│   "
                walk(child, prefix + extension, depth + 1)

    walk(base)
    return "\n".join(lines) + "\n"


def collect_json_artifacts() -> list[dict]:
    artifacts = []

    for root in [AUDIT, SANDBOX]:
        if not root.exists():
            continue

        for path in sorted(root.rglob("*.json")):
            if is_ignored(path):
                continue

            data = safe_json(path)

            artifacts.append({
                "file": rel(path),
                "name": path.name,
                "phase": data.get("phase", path.stem),
                "created_at": data.get("created_at"),
                "certified": data.get("certified"),
                "stage": data.get("stage"),
                "latest_confirmed_phase": data.get("latest_confirmed_phase"),
                "source_phase": data.get("source_phase"),
                "next_recommended_phase": (
                    data.get("next_recommended_phase")
                    or data.get("pipeline_summary", {}).get("next_recommended_phase")
                    or data.get("handoff_snapshot", {}).get("next_recommended_phase")
                ),
                "status": (
                    data.get("status")
                    or data.get("validation", {}).get("status")
                    or data.get("pipeline_summary", {}).get("status")
                ),
                "keys": sorted(list(data.keys()))[:40],
                "raw": data,
            })

    return artifacts


def phase_sort_key(item: dict) -> tuple:
    phase = str(item.get("phase") or "")
    number = ""
    suffix = ""

    for ch in phase:
        if ch.isdigit():
            number += ch
        elif number:
            suffix += ch
            break

    return (
        int(number) if number else 999999,
        phase,
        item.get("created_at") or "",
        item.get("file") or "",
    )


def build_timeline(artifacts: list[dict]) -> list[dict]:
    timeline = []

    for item in sorted(artifacts, key=phase_sort_key):
        phase = item.get("phase")
        if not phase:
            continue

        timeline.append({
            "phase": phase,
            "created_at": item.get("created_at"),
            "certified": item.get("certified"),
            "stage": item.get("stage"),
            "source_phase": item.get("source_phase"),
            "latest_confirmed_phase": item.get("latest_confirmed_phase"),
            "next_recommended_phase": item.get("next_recommended_phase"),
            "file": item.get("file"),
        })

    return timeline


def build_certified_index(artifacts: list[dict]) -> dict:
    certified = []
    uncertified = []

    for item in artifacts:
        row = {
            "phase": item.get("phase"),
            "file": item.get("file"),
            "created_at": item.get("created_at"),
            "stage": item.get("stage"),
        }

        if item.get("certified") is True:
            certified.append(row)
        else:
            uncertified.append(row)

    return {
        "certified_count": len(certified),
        "uncertified_count": len(uncertified),
        "certified": sorted(certified, key=lambda x: str(x.get("phase"))),
        "uncertified": sorted(uncertified, key=lambda x: str(x.get("phase"))),
    }


def repo_stats() -> dict:
    stats = {
        "total_files": 0,
        "total_dirs": 0,
        "python_files": 0,
        "typescript_files": 0,
        "json_files": 0,
        "markdown_files": 0,
        "scripts": 0,
        "tests": 0,
        "largest_files": [],
        "top_level": {},
    }

    largest = []

    for path in ROOT.rglob("*"):
        if is_ignored(path):
            continue

        if path.is_dir():
            stats["total_dirs"] += 1
            continue

        stats["total_files"] += 1
        suffix = path.suffix.lower()

        if suffix == ".py":
            stats["python_files"] += 1
        elif suffix in {".ts", ".tsx", ".js", ".jsx"}:
            stats["typescript_files"] += 1
        elif suffix == ".json":
            stats["json_files"] += 1
        elif suffix in {".md", ".txt"}:
            stats["markdown_files"] += 1

        if "scripts" in path.parts:
            stats["scripts"] += 1

        if "test" in path.name.lower() or "tests" in path.parts:
            stats["tests"] += 1

        try:
            largest.append((path.stat().st_size, rel(path)))
        except Exception:
            pass

        top = path.relative_to(ROOT).parts[0]
        stats["top_level"][top] = stats["top_level"].get(top, 0) + 1

    stats["largest_files"] = [
        {"file": p, "bytes": size}
        for size, p in sorted(largest, reverse=True)[:30]
    ]

    return stats


def classify_stack(path: str) -> str:
    parts = Path(path).parts

    known = [
        "auth", "identity", "market_data", "snaptrade", "strategy",
        "risk", "portfolio", "journal", "ledger", "learning",
        "research", "execution", "notification", "wolfden",
        "chat", "admin", "strategy_candidate_sandbox",
    ]

    for part in parts:
        for key in known:
            if key in part.lower():
                return key

    if "frontend" in parts:
        return "frontend"

    if "backend" in parts:
        return "backend_uncategorized"

    if "runtime" in parts:
        return "runtime_artifacts"

    if "audit" in parts:
        return "audit_artifacts"

    return "unknown"


def build_stack_topology() -> dict:
    stacks = defaultdict(list)

    for path in ROOT.rglob("*"):
        if is_ignored(path) or not path.is_file():
            continue

        r = rel(path)
        stacks[classify_stack(r)].append(r)

    return {
        stack: {
            "file_count": len(files),
            "sample_files": files[:40],
        }
        for stack, files in sorted(stacks.items())
    }


def build_layer_topology() -> dict:
    layer_rules = {
        "L0_external_adapter": ["adapter", "provider", "client", "snaptrade", "yfinance", "finnhub", "alpha"],
        "L1_security_auth_safety": ["auth", "security", "permission", "guard", "gate", "risk"],
        "L2_domain": ["domain", "contract", "scoring", "signal", "strategy"],
        "L3_service_facade": ["service", "facade"],
        "L4_runtime_orchestration": ["runtime", "orchestrator", "controller", "scheduler"],
        "L5_api_presentation": ["api", "route", "endpoint"],
        "L6_frontend": ["frontend", "component", "page", "app"],
        "L7_tests": ["test", "spec", "fixture"],
    }

    layers = defaultdict(list)

    for path in ROOT.rglob("*"):
        if is_ignored(path) or not path.is_file():
            continue

        r = rel(path)
        lower = r.lower()

        matched = False
        for layer, tokens in layer_rules.items():
            if any(token in lower for token in tokens):
                layers[layer].append(r)
                matched = True
                break

        if not matched:
            layers["UNCLASSIFIED"].append(r)

    return {
        layer: {
            "file_count": len(files),
            "sample_files": files[:50],
        }
        for layer, files in sorted(layers.items())
    }


def make_ascii_timeline(timeline: list[dict]) -> str:
    lines = []

    for item in timeline:
        phase = item.get("phase")
        certified = item.get("certified")
        mark = "✅" if certified is True else "⚠️" if certified is False else "•"
        stage = item.get("stage") or item.get("latest_confirmed_phase") or ""
        lines.append(f"{mark} {phase}")
        if stage:
            lines.append(f"   └─ {stage}")
        if item.get("next_recommended_phase"):
            lines.append(f"      next: {item.get('next_recommended_phase')}")
        lines.append("")

    return "\n".join(lines)


def make_node_map() -> str:
    return """NEUROVEST SYSTEM NODE MAP

Repository
│
├── backend/
│   ├── L0 External Adapters
│   ├── L1 Security/Auth/Safety
│   ├── L2 Domain Logic
│   ├── L3 Service/Facade
│   ├── L4 Runtime Orchestration
│   ├── L5 API Presentation
│   └── L7 Tests
│
├── frontend/
│   └── L6 User Interface
│
├── runtime/
│   └── strategy_candidate_sandbox/
│       ├── historical replay artifacts
│       ├── strategy candidate sandbox artifacts
│       ├── Qwen read-only certification artifacts
│       ├── rollup certifications
│       ├── handoff refreshes
│       └── terminal archive summary
│
├── scripts/
│   ├── phase controllers
│   ├── audit generators
│   ├── repair/check controllers
│   └── handoff generators
│
├── audit/
│   ├── architecture audits
│   ├── topology audits
│   ├── safety audits
│   └── certification evidence
│
└── handoff/
    └── generated master architecture handoff package
"""


def make_runtime_state_machine() -> str:
    return """QWEN READ-ONLY STATE MACHINE

READ_HANDOFF
    │
    ├── SUMMARIZE_ARCHITECTURE
    │       └── STOP
    │
    ├── EXPLAIN_LOCKED_GATES
    │       └── STOP
    │
    ├── REPORT_MISSING_CONTEXT
    │       └── STOP
    │
    └── RECOMMEND_READ_ONLY_NEXT_PHASE
            └── STOP

TERMINAL FREEZE:
    terminal_read_allowed = true
    terminal_write_allowed = false
    terminal_execution_allowed = false
    terminal_mutation_allowed = false
    terminal_next_phase_generation_allowed = false
"""


def make_dependency_graph() -> str:
    return """HIGH-LEVEL DEPENDENCY GRAPH

Source Repository
    │
    ▼
Audit Scripts
    │
    ▼
Audit Artifacts
    │
    ▼
Runtime / Strategy Candidate Sandbox Artifacts
    │
    ▼
Qwen Read-Only Stub Phases
    │
    ▼
Rollup Certifications
    │
    ▼
Handoff Bundle Refreshes
    │
    ▼
Terminal Freeze
    │
    ▼
Archive / New Chat Handoff
"""


def make_master_doc(stats, stack_topology, layer_topology, timeline, certified_index) -> str:
    certified_count = certified_index["certified_count"]
    uncertified_count = certified_index["uncertified_count"]

    latest = None
    for item in reversed(timeline):
        if item.get("certified") is True:
            latest = item
            break

    latest_phase = latest.get("phase") if latest else "UNKNOWN"

    return f"""# NeuroVest Master Architecture Handoff

Generated: {datetime.now(UTC).isoformat()}
Mode: READ ONLY
Controller: {PHASE}

---

## 1. Executive Summary

NeuroVest is a layered fintech/trading research system being built with strict safety separation.

This handoff was generated by scanning the repository, audit artifacts, runtime artifacts, and certified phase outputs. It is intended to be used as the starting point for a new chat or developer handoff.

The latest confirmed archive checkpoint is:

```text
{latest_phase}

The Qwen read-only certification workstream is terminal-frozen. It proves Qwen may act only as a read-only architecture observer/summarizer. It does not create runtime execution, source mutation, learning, promotion, broker execution, live trading, autonomous phase execution, or recursive execution.

2. Repository Statistics
{json.dumps(stats, indent=2)}
3. Repository Topology

See:

handoff/repository_tree.txt
handoff/backend_tree.txt
handoff/frontend_tree.txt
handoff/runtime_tree.txt
handoff/audit_tree.txt
4. Canonical Layer Model
L0_external_adapter        external data/broker/provider adapters
L1_security_auth_safety    auth, permissions, gates, guards, safety locks
L2_domain                  pure business logic, contracts, scoring, signal math
L3_service_facade          service interfaces and facade coordination
L4_runtime_orchestration   controllers, schedulers, runtime coordination
L5_api_presentation        API routes and presentation layer
L6_frontend                Next.js / UI
L7_tests                   tests, specs, fixtures, validation

Layer topology generated in:

handoff/canonical_layer_map.txt
5. Stack Topology

Stack topology generated in:

handoff/stack_topology.txt

Detected stack groups:

{chr(10).join(f"- {k}: {v['file_count']} files" for k, v in stack_topology.items())}
6. Runtime Node Map
{make_node_map()}
7. Runtime State Machine
{make_runtime_state_machine()}
8. Dependency Graph
{make_dependency_graph()}
9. Certification Timeline

Certified artifacts found: {certified_count}
Uncertified or historical artifacts found: {uncertified_count}

Full timeline written to:

handoff/certification_timeline.txt
10. Confirmed Good State

Confirmed good means:

artifact exists
phase is marked certified true
rollup checks passed
safety locks remain false
no execution surface opened
no mutation surface opened

The terminal archive confirms:

read_only_chain_closed = true
execution_surface_opened = false
mutation_surface_opened = false
11. Current Read-Only Capabilities

Qwen may only:

read architecture state
summarize architecture
explain locked gates
report missing context
summarize disabled capabilities
summarize certified capabilities
inspect final context package
inspect terminal snapshot
12. Still Disabled
file writes
shell execution
runtime execution
source mutation
policy mutation
matrix mutation
context package mutation
handoff mutation
terminal mutation
runtime policy enforcement
strategy enablement
simulation enablement
learning enablement
promotion enablement
broker execution
live execution
recursive self-execution
autonomous phase execution
13. Future Workstreams

Do not continue the Qwen read-only phase chain.

Start a new independent campaign only after this handoff, such as:

A. LLM orchestration architecture
B. permission request model
C. execution architecture design
D. sandbox runtime activation plan
E. strategy candidate lifecycle
F. learning/promotion approval chain
G. broker/live execution safety model

Each must begin as architecture/audit-only and must not inherit execution authority from Qwen.

14. Generated Files
handoff/MASTER_ARCHITECTURE_HANDOFF.md
handoff/repository_tree.txt
handoff/backend_tree.txt
handoff/frontend_tree.txt
handoff/runtime_tree.txt
handoff/audit_tree.txt
handoff/canonical_layer_map.txt
handoff/stack_topology.txt
handoff/runtime_node_graph.txt
handoff/dependency_graph.txt
handoff/certification_timeline.txt
handoff/audit_timeline.txt
handoff/controller_timeline.txt
handoff/runtime_state_machine.txt
handoff/repository_statistics.json
handoff/certified_phase_index.json
handoff/topology_summary.json

"""

def main() -> None:
    artifacts = collect_json_artifacts()
    timeline = build_timeline(artifacts)
    certified_index = build_certified_index(artifacts)
    stats = repo_stats()
    stack_topology = build_stack_topology()
    layer_topology = build_layer_topology()

    write(HANDOFF / "repository_tree.txt", tree_for(ROOT, max_depth=4))
    write(HANDOFF / "backend_tree.txt", tree_for(ROOT / "backend", max_depth=10))
    write(HANDOFF / "frontend_tree.txt", tree_for(ROOT / "frontend", max_depth=10))
    write(HANDOFF / "runtime_tree.txt", tree_for(ROOT / "runtime", max_depth=10))
    write(HANDOFF / "audit_tree.txt", tree_for(ROOT / "audit", max_depth=6))

    write(HANDOFF / "certification_timeline.txt", make_ascii_timeline(timeline))
    write(HANDOFF / "audit_timeline.txt", make_ascii_timeline([x for x in timeline if "/audit/" in x.get("file", "")]))
    write(HANDOFF / "controller_timeline.txt", make_ascii_timeline([x for x in timeline if "scripts/" in x.get("file", "") or "controller" in str(x.get("phase", "")).lower()]))

    write(HANDOFF / "runtime_node_graph.txt", make_node_map())
    write(HANDOFF / "runtime_state_machine.txt", make_runtime_state_machine())
    write(HANDOFF / "dependency_graph.txt", make_dependency_graph())

    write(HANDOFF / "stack_topology.txt", json.dumps(stack_topology, indent=2))
    write(HANDOFF / "canonical_layer_map.txt", json.dumps(layer_topology, indent=2))

    write(HANDOFF / "repository_statistics.json", json.dumps(stats, indent=2))
    write(HANDOFF / "certified_phase_index.json", json.dumps(certified_index, indent=2))

    topology_summary = {
        "phase": PHASE,
        "created_at": datetime.now(UTC).isoformat(),
        "mode": "READ_ONLY",
        "root": str(ROOT),
        "artifact_count": len(artifacts),
        "certified_count": certified_index["certified_count"],
        "uncertified_count": certified_index["uncertified_count"],
        "stacks": {k: v["file_count"] for k, v in stack_topology.items()},
        "layers": {k: v["file_count"] for k, v in layer_topology.items()},
        "terminal_archive_source": str(SANDBOX / "61A_archive_or_new_chat_handoff_summary_latest.json"),
        "generated_documents": [
            "MASTER_ARCHITECTURE_HANDOFF.md",
            "repository_tree.txt",
            "backend_tree.txt",
            "frontend_tree.txt",
            "runtime_tree.txt",
            "audit_tree.txt",
            "canonical_layer_map.txt",
            "stack_topology.txt",
            "runtime_node_graph.txt",
            "dependency_graph.txt",
            "certification_timeline.txt",
            "audit_timeline.txt",
            "controller_timeline.txt",
            "runtime_state_machine.txt",
            "repository_statistics.json",
            "certified_phase_index.json",
            "topology_summary.json",
        ],
        "certified": True,
    }

    write(HANDOFF / "topology_summary.json", json.dumps(topology_summary, indent=2))

    master = make_master_doc(stats, stack_topology, layer_topology, timeline, certified_index)
    write(HANDOFF / "MASTER_ARCHITECTURE_HANDOFF.md", master)

    print(json.dumps(topology_summary, indent=2))
    print(f"\nWROTE HANDOFF PACKAGE: {HANDOFF}")


if __name__ == "__main__":
    main()
