#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
HANDOFF = ROOT / "handoff"
OUT = HANDOFF / "project_bible"

PHASE = "63A_PROJECT_BIBLE_GENERATOR"

OUT.mkdir(parents=True, exist_ok=True)


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


stats = read_json(HANDOFF / "repository_statistics.json")
cert_index = read_json(HANDOFF / "certified_phase_index.json")
topology = read_json(HANDOFF / "topology_summary.json")

repository_tree = read(HANDOFF / "repository_tree.txt")
backend_tree = read(HANDOFF / "backend_tree.txt")
frontend_tree = read(HANDOFF / "frontend_tree.txt")
runtime_tree = read(HANDOFF / "runtime_tree.txt")
audit_tree = read(HANDOFF / "audit_tree.txt")

layer_map = read(HANDOFF / "canonical_layer_map.txt")
stack_topology = read(HANDOFF / "stack_topology.txt")
node_map = read(HANDOFF / "runtime_node_graph.txt")
dependency_graph = read(HANDOFF / "dependency_graph.txt")
runtime_state_machine = read(HANDOFF / "runtime_state_machine.txt")
cert_timeline = read(HANDOFF / "certification_timeline.txt")

archive = read_json(ROOT / "runtime/strategy_candidate_sandbox/61A_archive_or_new_chat_handoff_summary_latest.json")
archive_summary = archive.get("archive_summary", {})

certified_count = cert_index.get("certified_count", 0)
uncertified_count = cert_index.get("uncertified_count", 0)

executive_summary = f"""
Generated: {datetime.now(UTC).isoformat()}
Controller: {PHASE}
Mode: READ ONLY DOCUMENTATION COMPILER

NeuroVest is a layered fintech/trading research system using strict stack isolation, audit-first development, runtime locks, and explicit certification artifacts.

This Project Bible compiles the existing 62A handoff package plus certified runtime artifacts into one usable new-chat/developer handoff.

Latest archive status:
- archive_mode: {archive_summary.get("archive_mode")}
- latest_certified_phase: {archive_summary.get("latest_certified_phase")}
- terminal_stage: {archive_summary.get("terminal_stage")}
- read_only_chain_closed: {archive_summary.get("read_only_chain_closed")}
- execution_surface_opened: {archive_summary.get("execution_surface_opened")}
- mutation_surface_opened: {archive_summary.get("mutation_surface_opened")}

Certified artifacts: {certified_count}
Uncertified / historical artifacts: {uncertified_count}
"""

architecture_philosophy = """
NeuroVest must remain stack-first, layer-aware, and safety-gated.

Canonical layer model:

L0_external_adapter:
External providers only. Examples: yfinance, SnapTrade, market data adapters.

L1_security_auth_safety:
Auth, permissions, firewalls, broker guards, risk guards, enablement gates.

L2_domain:
Pure trading/domain contracts, strategy math, signal contracts, scorecards, replay metrics.

L3_service_facade:
Stable service interfaces between domain logic, adapters, and API surfaces.

L4_runtime_orchestration:
Controllers, schedulers, runtime wiring, dependency traces, orchestration.

L5_api_presentation:
API routes and request/response presentation only.

L6_frontend:
Next.js UI, dashboard, chat shell, frontend service calls.

L7_tests:
Tests, fixtures, validation, certification probes.

Rule:
Do not cross layers just because it is faster. Preserve stack ownership and certify before runtime activation.
"""

confirmed_good = """
Confirmed good means the repo has generated artifacts showing:
- artifact exists
- phase reports certified true
- rollup checks passed
- safety locks remained false
- no execution surface opened
- no mutation surface opened

Important certified runway:
- Historical bars validation
- Bar-only replay metrics
- Candidate scorecard from replay metrics
- Manual promotion gate stub
- Hold-only trade simulation runway
- Entry signal generator disabled
- Exit signal generator disabled
- Strategy sandbox wiregraph
- Strategy rule enablement gate locked
- Trade simulation enablement gate locked
- Risk gate locked
- Master sandbox gate wiregraph
- Sandbox runtime dependency trace
- Qwen read-only architecture context
- Qwen response validator
- Qwen session contract
- Qwen loop boundary
- Qwen policy map
- Qwen policy boundary matrix
- Qwen final context package
- Qwen final handoff certification
- Qwen terminal freeze
- Archive/new-chat handoff
"""

disabled = """
Still disabled:
- file writes
- shell execution
- runtime execution
- source mutation
- policy mutation
- matrix mutation
- context package mutation
- handoff mutation
- terminal mutation
- runtime policy enforcement
- strategy enablement
- simulation enablement
- learning enablement
- promotion enablement
- broker execution
- live execution
- recursive self-execution
- autonomous phase execution

Critical locks remain false:
- live_execution_enabled
- broker_execution_enabled
- simulation_enabled
- registry_write_enabled
- promotion_enabled
- learning_enabled
"""

data_flow = """
MARKET DATA FLOW

External Provider
    ↓
L0 Provider Adapter
    ↓
Provider Registry / Router
    ↓
Market Data Service
    ↓
Historical Bars / Live Price
    ↓
Replay / Strategy Sandbox
    ↓
Metrics / Scorecard
    ↓
Manual Review Gate


STRATEGY CANDIDATE FLOW

Chat / Research / Human Idea
    ↓
Strategy Proposal Capture
    ↓
Candidate Sandbox
    ↓
Historical Replay
    ↓
Metrics Contract
    ↓
Scorecard
    ↓
Manual Promotion Gate
    ↓
Approved Strategy only after explicit certification


EXECUTION FLOW — DISABLED

Strategy Decision
    ↓
Risk Gate
    ↓
Simulation Gate
    ↓
Paper Broker / Broker
    ↓
Ledger

Current status: disabled / locked.
"""

qwen_architecture = """
QWEN READ-ONLY ARCHITECTURE

Qwen is certified only as a read-only architecture observer.

Allowed:
- read architecture state
- summarize architecture
- explain locked gates
- report missing context
- summarize disabled capabilities
- summarize certified capabilities
- inspect final context package
- inspect terminal snapshot

Forbidden:
- file writes
- patch generation
- shell execution
- runtime execution
- source mutation
- broker execution
- live trading
- recursive execution
- autonomous phase execution

Terminal state:
Qwen may read and summarize only, then stop.
"""

roadmap = """
Do not continue the Qwen read-only phase chain.

Next independent workstreams should be separate campaigns:

1. LLM orchestration architecture
   Define how Neuro, Qwen, local models, and future models are routed without giving Qwen execution authority.

2. Permission request model
   Let read-only systems request review without performing actions.

3. Sandbox runtime activation plan
   Bring sandbox runtime online behind certified gates only.

4. Strategy candidate lifecycle
   Formalize candidate creation, replay, scorecard, review, and versioned promotion.

5. Learning / promotion approval chain
   Keep learning and promotion locked until manually certified.

6. Broker/live execution safety model
   Design paper/canary/live escalation without opening broker execution by default.
"""

developer_rulebook = """
DEVELOPER RULEBOOK

Never:
- let Qwen write files
- let Qwen execute shell commands
- let Qwen mutate source
- let Qwen enable runtime
- let Qwen enable broker/live trading
- bypass manual gates
- collapse stacks for convenience
- place API logic in domain
- place broker calls in domain
- place frontend assumptions in backend domain logic
- enable learning or promotion without certification

Always:
- preserve L0-L7 topology
- keep stack ownership clear
- certify before activation
- write artifacts before trusting behavior
- prefer controller rollups over scattered one-off changes
- keep broker/live false until a dedicated certification campaign exists
"""

glossary = """
Candidate:
A proposed strategy or strategy variant not yet approved.

Replay:
Historical bar-based evaluation of a candidate.

Scorecard:
Metrics summary generated from replay results.

Promotion:
Manual approval process that turns a candidate into an approved strategy.

Gate:
A locked contract that must certify before a capability can activate.

Qwen:
External LLM currently certified only as a read-only observer.

Terminal Freeze:
A certified end state proving no next autonomous phase, execution, or mutation path exists.
"""

traceability = f"""
TRACEABILITY SOURCES

Primary generated evidence:
- handoff/MASTER_ARCHITECTURE_HANDOFF.md
- handoff/certification_timeline.txt
- handoff/certified_phase_index.json
- handoff/repository_tree.txt
- handoff/backend_tree.txt
- handoff/frontend_tree.txt
- handoff/runtime_tree.txt
- handoff/canonical_layer_map.txt
- handoff/stack_topology.txt
- handoff/runtime_node_graph.txt
- handoff/dependency_graph.txt
- handoff/runtime_state_machine.txt
- runtime/strategy_candidate_sandbox/61A_archive_or_new_chat_handoff_summary_latest.json

Certified count: {certified_count}
Uncertified / historical count: {uncertified_count}
"""

project_bible = ""
project_bible += section("Executive Summary", executive_summary)
project_bible += section("Architecture Philosophy", architecture_philosophy)
project_bible += section("Repository Node Map", f"```text\n{node_map}\n```")
project_bible += section("Dependency Graph", f"```text\n{dependency_graph}\n```")
project_bible += section("Runtime State Machine", f"```text\n{runtime_state_machine}\n```")
project_bible += section("Data Flow", data_flow)
project_bible += section("Qwen Read-Only Architecture", qwen_architecture)
project_bible += section("Confirmed Good Components", confirmed_good)
project_bible += section("Still Disabled / Locked", disabled)
project_bible += section("Repository Statistics", f"```json\n{json.dumps(stats, indent=2)}\n```")
project_bible += section("Canonical Layer Map", f"```json\n{layer_map}\n```")
project_bible += section("Stack Topology", f"```json\n{stack_topology}\n```")
project_bible += section("Repository Tree", f"```text\n{repository_tree}\n```")
project_bible += section("Backend Tree", f"```text\n{backend_tree}\n```")
project_bible += section("Frontend Tree", f"```text\n{frontend_tree}\n```")
project_bible += section("Runtime Tree", f"```text\n{runtime_tree}\n```")
project_bible += section("Audit Tree", f"```text\n{audit_tree}\n```")
project_bible += section("Certification Timeline", f"```text\n{cert_timeline}\n```")
project_bible += section("Future Roadmap", roadmap)
project_bible += section("Developer Rulebook", developer_rulebook)
project_bible += section("Glossary", glossary)
project_bible += section("Traceability Index", traceability)

write(OUT / "PROJECT_BIBLE.md", project_bible)
write(OUT / "EXECUTIVE_SUMMARY.md", executive_summary)
write(OUT / "NODE_MAP.md", f"# Node Map\n\n```text\n{node_map}\n```\n")
write(OUT / "DEPENDENCY_GRAPH.md", f"# Dependency Graph\n\n```text\n{dependency_graph}\n```\n")
write(OUT / "DATA_FLOW.md", f"# Data Flow\n\n{data_flow}\n")
write(OUT / "QWEN_READ_ONLY_ARCHITECTURE.md", f"# Qwen Read-Only Architecture\n\n{qwen_architecture}\n")
write(OUT / "DEVELOPER_RULEBOOK.md", f"# Developer Rulebook\n\n{developer_rulebook}\n")
write(OUT / "ROADMAP.md", f"# Roadmap\n\n{roadmap}\n")
write(OUT / "GLOSSARY.md", f"# Glossary\n\n{glossary}\n")
write(OUT / "TRACEABILITY_INDEX.md", f"# Traceability Index\n\n{traceability}\n")

index = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_DOCUMENTATION_COMPILER",
    "source_handoff_dir": str(HANDOFF),
    "output_dir": str(OUT),
    "certified_count": certified_count,
    "uncertified_count": uncertified_count,
    "archive_summary": archive_summary,
    "generated_files": sorted(p.name for p in OUT.iterdir() if p.is_file()),
    "certified": True,
}

write(OUT / "PROJECT_BIBLE.json", json.dumps(index, indent=2))

write(
    OUT / "INDEX.md",
    "\n".join([
        "# Project Bible Index",
        "",
        "- PROJECT_BIBLE.md",
        "- PROJECT_BIBLE.json",
        "- EXECUTIVE_SUMMARY.md",
        "- NODE_MAP.md",
        "- DEPENDENCY_GRAPH.md",
        "- DATA_FLOW.md",
        "- QWEN_READ_ONLY_ARCHITECTURE.md",
        "- DEVELOPER_RULEBOOK.md",
        "- ROADMAP.md",
        "- GLOSSARY.md",
        "- TRACEABILITY_INDEX.md",
        "",
    ])
)

print(json.dumps(index, indent=2))
print(f"\nWROTE PROJECT BIBLE PACKAGE: {OUT}")
