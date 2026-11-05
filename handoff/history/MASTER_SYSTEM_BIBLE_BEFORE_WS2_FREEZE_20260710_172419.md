# NEUROVEST MASTER SYSTEM BIBLE

Generated: 2026-07-07T03:21:37.654109+00:00
Compiler: 64A_MASTER_SYSTEM_BIBLE_COMPILER
Mode: READ ONLY DOCUMENTATION COMPILER

> This file is compiled from existing generated handoff, Project Bible, Architecture Atlas, topology, timeline, and traceability artifacts.

---

# Table of Contents

1. [Executive] Executive Summary
2. [Reference] Project Bible
3. [Reference] Architecture Atlas
4. [Reference] Master Architecture Handoff
5. [Reference] Index
6. [Repository Topology] Repository Tree
7. [Repository Topology] Backend Tree
8. [Repository Topology] Frontend Tree
9. [Repository Topology] Runtime Tree
10. [Repository Topology] Audit Tree
11. [Layer Architecture] Canonical Layer Map
12. [Layer Architecture] Layer Ownership
13. [Stack Architecture] Stack Topology
14. [Stack Architecture] Stack Ownership
15. [Stack Architecture] Stack Graph
16. [Node / Topology] Runtime Node Graph
17. [Node / Topology] Node Graph
18. [Node / Topology] Dependency Graph
19. [Node / Topology] Topology Summary
20. [Node / Topology] Node Map
21. [Dependency Atlas] Dependency Graph
22. [Dependency Atlas] Import Dependency Atlas
23. [Dependency Atlas] Dependency Graph
24. [Runtime State] Runtime State Machine
25. [Flows] Data Flow
26. [Flows] Market Data
27. [Flows] Candidate Pipeline
28. [Flows] Execution Disabled
29. [Qwen Read-Only] Qwen Read Only Architecture
30. [Certification History] Certification Timeline
31. [Certification History] Phase Timeline
32. [Certification History] Certified Phase Index
33. [Governance] Developer Rulebook
34. [Roadmap] Roadmap
35. [Glossary] Glossary
36. [Traceability] Traceability Index
37. [Machine Index] Repository Statistics
38. [Machine Index] Project Bible
39. [Machine Index] Architecture Atlas

---

# 1. [Executive] Executive Summary

Source: `handoff/project_bible/EXECUTIVE_SUMMARY.md`


Generated: 2026-07-07T03:05:48.838392+00:00
Controller: 63A_PROJECT_BIBLE_GENERATOR
Mode: READ ONLY DOCUMENTATION COMPILER

NeuroVest is a layered fintech/trading research system using strict stack isolation, audit-first development, runtime locks, and explicit certification artifacts.

This Project Bible compiles the existing 62A handoff package plus certified runtime artifacts into one usable new-chat/developer handoff.

Latest archive status:
- archive_mode: terminal_read_only_archive
- latest_certified_phase: 60B_QWEN_READ_ONLY_TERMINAL_FREEZE_ROLLUP_CERTIFICATION
- terminal_stage: Qwen Read-Only Terminal Freeze Certified
- read_only_chain_closed: True
- execution_surface_opened: False
- mutation_surface_opened: False

Certified artifacts: 110
Uncertified / historical artifacts: 43

---

# 2. [Reference] Project Bible

Source: `handoff/project_bible/PROJECT_BIBLE.md`



# Executive Summary

Generated: 2026-07-07T03:05:48.838392+00:00
Controller: 63A_PROJECT_BIBLE_GENERATOR
Mode: READ ONLY DOCUMENTATION COMPILER

NeuroVest is a layered fintech/trading research system using strict stack isolation, audit-first development, runtime locks, and explicit certification artifacts.

This Project Bible compiles the existing 62A handoff package plus certified runtime artifacts into one usable new-chat/developer handoff.

Latest archive status:
- archive_mode: terminal_read_only_archive
- latest_certified_phase: 60B_QWEN_READ_ONLY_TERMINAL_FREEZE_ROLLUP_CERTIFICATION
- terminal_stage: Qwen Read-Only Terminal Freeze Certified
- read_only_chain_closed: True
- execution_surface_opened: False
- mutation_surface_opened: False

Certified artifacts: 110
Uncertified / historical artifacts: 43


# Architecture Philosophy

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


# Repository Node Map

```text
NEUROVEST SYSTEM NODE MAP

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

```


# Dependency Graph

```text
HIGH-LEVEL DEPENDENCY GRAPH

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

```


# Runtime State Machine

```text
QWEN READ-ONLY STATE MACHINE

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

```


# Data Flow

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


# Qwen Read-Only Architecture

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


# Confirmed Good Components

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


# Still Disabled / Locked

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


# Repository Statistics

```json
{
  "total_files": 827,
  "total_dirs": 73,
  "python_files": 437,
  "typescript_files": 20,
  "json_files": 296,
  "markdown_files": 29,
  "scripts": 280,
  "tests": 231,
  "largest_files": [
    {
      "file": ".aider.tags.cache.v4/cache.db-wal",
      "bytes": 4124152
    },
    {
      "file": "runtime/graph_history/events.jsonl",
      "bytes": 2423897
    },
    {
      "file": "topology_wire_graph.png",
      "bytes": 1620490
    },
    {
      "file": "runtime/market_warehouse/history/AAPL_history.csv",
      "bytes": 1561584
    },
    {
      "file": "runtime/market_warehouse/history/MSFT_history.csv",
      "bytes": 1284408
    },
    {
      "file": "runtime/market_warehouse/history/TD_TO_history.csv",
      "bytes": 997917
    },
    {
      "file": "runtime/market_warehouse/history/RY_TO_history.csv",
      "bytes": 995607
    },
    {
      "file": "runtime/market_warehouse/history/NVDA_history.csv",
      "bytes": 956580
    },
    {
      "file": "cursor.AppImage",
      "bytes": 690286
    },
    {
      "file": "domain_runtime_overlay_graph.png",
      "bytes": 566611
    },
    {
      "file": "runtime/market_warehouse/history/TSLA_history.csv",
      "bytes": 539919
    },
    {
      "file": "runtime/market_warehouse/history/VFV_TO_history.csv",
      "bytes": 452228
    },
    {
      "file": "runtime/market_warehouse/history/VUN_TO_history.csv",
      "bytes": 426620
    },
    {
      "file": "domain_subsystem_graph.png",
      "bytes": 318287
    },
    {
      "file": "topology_wire_graph_canonical.png",
      "bytes": 308830
    },
    {
      "file": ".aider.chat.history.md",
      "bytes": 294388
    },
    {
      "file": "runtime/repo_memory/repo_index_v2.json",
      "bytes": 250378
    },
    {
      "file": ".aider.tags.cache.v4/cache.db",
      "bytes": 237568
    },
    {
      "file": "frontend/package-lock.json",
      "bytes": 221605
    },
    {
      "file": "neuro_cli_file_inspection.json",
      "bytes": 71718
    },
    {
      "file": "runtime/repo_memory/dependency_graph_v1.json",
      "bytes": 64283
    },
    {
      "file": "runtime/handoff_snapshot/neurovest_training_handoff_bundle_latest.json",
      "bytes": 59780
    },
    {
      "file": "frontend/app/page.tsx",
      "bytes": 35077
    },
    {
      "file": ".aider.input.history",
      "bytes": 33797
    },
    {
      "file": ".aider.tags.cache.v4/cache.db-shm",
      "bytes": 32768
    },
    {
      "file": "runtime/certifications/phase6b_dependency_validation_certification_latest.json",
      "bytes": 32429
    },
    {
      "file": "runtime/repo_memory/component_overlay_v1.json",
      "bytes": 30215
    },
    {
      "file": "runtime/handoff_snapshot/file_manifest_latest.txt",
      "bytes": 28495
    },
    {
      "file": "runtime/repo_memory/repo_index.json",
      "bytes": 27818
    },
    {
      "file": "runtime/handoff_snapshot/topology_tree_latest.txt",
      "bytes": 26518
    }
  ],
  "top_level": {
    "OUTPUT": 1,
    "ARCHITECTURE_REPAIR_PLAN.json": 1,
    "TOPOLOGY_NORMALIZED_STATE.json": 1,
    "ARCH_GOVERNANCE.md": 1,
    "fix_phase9_self_fingerprint.sh": 1,
    "TOPOLOGY_STATE.json": 1,
    "topology_wire_graph.png": 1,
    "neurovest_repo_context.md": 1,
    "Directory Structure": 1,
    "ORPHAN_RESOLUTION_PLAN.json": 1,
    "topology_wire_graph_canonical.png": 1,
    ".env.example": 1,
    "domain_subsystem_graph.png": 1,
    "generate_wire_graph.py": 1,
    "neuro_health.sh": 1,
    "neuro_cli_file_inspection.json": 1,
    ".aider.input.history": 1,
    "FINAL_ARCHITECTURE_STATE.json": 1,
    "system_tree.txt": 1,
    "docker-compose.yml": 1,
    "ARCH_ENFORCEMENT_REPORT.json": 1,
    "spine_mvp_full.sh": 1,
    "pytest.ini": 1,
    ".gitignore": 1,
    "$OUTPUT": 1,
    "SERVICE_RELOCATION_PLAN_RECONCILED.json": 1,
    ".env": 1,
    "domain_runtime_overlay_graph.png": 1,
    ".aider.chat.history.md": 1,
    "cursor.AppImage": 1,
    "neuro": 1,
    "neuro_cli.py": 1,
    "neuro_engineer.py": 1,
    "SERVICE_RELOCATION_PLAN.json": 1,
    "architecture_backup": 1,
    "scripts": 279,
    "backend": 157,
    ".aider.tags.cache.v4": 3,
    "frontend": 36,
    "backups": 1,
    "runtime": 315,
    ".github": 1
  }
}
```


# Canonical Layer Map

```json
{
  "L0_external_adapter": {
    "file_count": 52,
    "sample_files": [
      "scripts/phase30g_yfinance_historical_bars_adapter_wire.py",
      "scripts/phase30a_yfinance_historical_bars_provider_probe_certification.py",
      "scripts/phase2_yfinance_market_warehouse.py",
      "scripts/phase30a_yfinance_historical_bars_provider_probe.py",
      "scripts/phase30e_yfinance_historical_bars_adapter_shape_validation.py",
      "scripts/phase30b_yfinance_provider_selection_snapshot.py",
      "scripts/phase30f_yfinance_historical_bars_adapter_wire_preview_certification.py",
      "scripts/phase30d_yfinance_historical_bars_adapter_stub_certification.py",
      "scripts/phase30f_yfinance_historical_bars_adapter_wire_preview.py",
      "scripts/phase29g_historical_replay_provider_readiness_snapshot.py",
      "scripts/phase30g_yfinance_historical_bars_adapter_wire_certification.py",
      "scripts/phase29f_historical_replay_provider_adapter_stub.py",
      "scripts/phase29e_historical_replay_market_data_provider_contract_certification.py",
      "scripts/phase29f_historical_replay_provider_adapter_stub_certification.py",
      "scripts/phase29e_historical_replay_market_data_provider_contract.py",
      "scripts/phase30d_yfinance_historical_bars_adapter_stub.py",
      "scripts/phase30e_yfinance_historical_bars_adapter_shape_validation_certification.py",
      "backend/app/snaptrade/executions/config.py",
      "backend/app/snaptrade/executions/execution_layer.py",
      "backend/app/stacks/chat_public/ollama_chat_client.py",
      "backend/app/stacks/market_data/yfinance_ingestor.py",
      "backend/app/stacks/market_data/provider_registry.py",
      "backend/app/stacks/market_data/provider_router.py",
      "backend/app/stacks/market_data/yfinance_historical_bars_adapter.py",
      "backend/app/stacks/market_data/provider_cache.py",
      "backend/app/stacks/snaptrade/__init__.py",
      "backend/app/stacks/snaptrade/execution.py",
      "backend/app/stacks/snaptrade/adapter.py",
      "backend/app/stacks/snaptrade/broker.py",
      "backend/app/stacks/snaptrade/base.py",
      "runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_stub_latest.json",
      "runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_shape_validation_latest.txt",
      "runtime/strategy_candidate_sandbox/historical_replay_market_data_provider_contract_v1.txt",
      "runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_stub_latest.txt",
      "runtime/strategy_candidate_sandbox/historical_replay_market_data_provider_contract_v1.json",
      "runtime/strategy_candidate_sandbox/historical_replay_provider_adapter_stub_latest.json",
      "runtime/strategy_candidate_sandbox/yfinance_historical_bars_provider_probe_latest.json",
      "runtime/strategy_candidate_sandbox/yfinance_historical_bars_provider_probe_latest.txt",
      "runtime/strategy_candidate_sandbox/historical_replay_provider_adapter_stub_latest.txt",
      "runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_wire_preview_latest.json",
      "runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_wire_preview_latest.txt",
      "runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_shape_validation_latest.json",
      "runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_wire_latest.json",
      "runtime/certifications/phase30f_yfinance_historical_bars_adapter_wire_preview_certification_latest.json",
      "runtime/certifications/phase30b_yfinance_provider_selection_snapshot_latest.json",
      "runtime/certifications/phase29e_historical_replay_market_data_provider_contract_certification_latest.json",
      "runtime/certifications/phase29g_historical_replay_provider_readiness_snapshot_latest.json",
      "runtime/certifications/phase30a_yfinance_historical_bars_provider_probe_certification_latest.json",
      "runtime/certifications/phase29f_historical_replay_provider_adapter_stub_certification_latest.json",
      "runtime/certifications/phase30g_yfinance_historical_bars_adapter_wire_certification_latest.json"
    ]
  },
  "L1_security_auth_safety": {
    "file_count": 68,
    "sample_files": [
      "scripts/phase52b_qwen_read_only_final_guardrail_summary_rollup_certification.py",
      "scripts/phase36a_strategy_rule_enablement_gate_contract_stub.py",
      "scripts/phase39b_master_sandbox_gate_wiregraph_rollup_certification.py",
      "scripts/phase36b_enablement_gate_validation_stub.py",
      "scripts/phase45a_qwen_read_only_architecture_summary_gate_stub.py",
      "scripts/phase15_risk_gate_service_chain.py",
      "scripts/phase37a_trade_simulation_enablement_gate_contract_stub.py",
      "scripts/phase39a_master_sandbox_gate_wiregraph_refresh.py",
      "scripts/phase15g_add_risk_chain_to_dashboard.py",
      "scripts/phase37b_trade_simulation_enablement_gate_validation_stub.py",
      "scripts/phase38b_risk_gate_validation_stub.py",
      "scripts/phase15e_risk_service_chain_graph_export.py",
      "scripts/phase38c_risk_gate_pipeline_rollup_certification.py",
      "scripts/phase15g_risk_chain_dashboard_certification.py",
      "scripts/phase45b_qwen_read_only_architecture_summary_gate_rollup_certification.py",
      "scripts/phase26c_chat_safety_prompt_live_execution_guard_certification.py",
      "scripts/phase52a_qwen_read_only_final_guardrail_summary_stub.py",
      "scripts/phase15f_risk_gate_service_chain_certification.py",
      "scripts/phase38a_risk_gate_contract_stub.py",
      "scripts/phase36c_enablement_gate_pipeline_rollup_certification.py",
      "scripts/phase32c_manual_promotion_gate_stub.py",
      "scripts/phase37c_trade_simulation_enablement_gate_pipeline_rollup_certification.py",
      "frontend/services/riskService.ts",
      "frontend/app/api/v1/risk/gate/[symbol]/route.ts",
      "backend/app/stacks/auth_identity/__init__.py",
      "backend/app/stacks/auth_identity/base.py",
      "backend/app/stacks/auth_identity/validator.py",
      "backend/app/stacks/auth_identity/gate.py",
      "backend/app/stacks/strategy_candidate_sandbox/strategy_rule_enablement_gate_contract.py",
      "backend/app/stacks/strategy_candidate_sandbox/qwen_read_only_architecture_summary_gate.py",
      "backend/app/stacks/strategy_candidate_sandbox/trade_simulation_enablement_gate_contract.py",
      "backend/app/stacks/strategy_candidate_sandbox/risk_gate_validator.py",
      "backend/app/stacks/strategy_candidate_sandbox/strategy_rule_enablement_gate_validator.py",
      "backend/app/stacks/strategy_candidate_sandbox/manual_promotion_gate.py",
      "backend/app/stacks/strategy_candidate_sandbox/trade_simulation_enablement_gate_validator.py",
      "backend/app/stacks/strategy_candidate_sandbox/risk_gate_contract.py",
      "backend/app/stacks/risk/loss_streak_guard.py",
      "backend/app/stacks/risk/__init__.py",
      "backend/app/stacks/risk/drawdown_guard.py",
      "backend/app/stacks/risk/risk_runtime_service.py",
      "backend/app/stacks/risk/exposure.py",
      "backend/app/stacks/risk/kill_switch.py",
      "backend/app/stacks/risk/limits.py",
      "backend/app/stacks/risk/base.py",
      "backend/app/stacks/risk/risk_service.py",
      "runtime/strategy_candidate_sandbox/39B_master_sandbox_gate_wiregraph_rollup_certification_latest.json",
      "runtime/strategy_candidate_sandbox/45B_qwen_read_only_architecture_summary_gate_rollup_certification_latest.json",
      "runtime/strategy_candidate_sandbox/45A_qwen_read_only_architecture_summary_gate_stub_latest.json",
      "runtime/strategy_candidate_sandbox/36C_enablement_gate_pipeline_rollup_certification_latest.json",
      "runtime/strategy_candidate_sandbox/39A_master_sandbox_gate_wiregraph_latest.mmd"
    ]
  },
  "L2_domain": {
    "file_count": 243,
    "sample_files": [
      "domain_subsystem_graph.png",
      "domain_runtime_overlay_graph.png",
      "scripts/phase35a_exit_signal_rule_contract_stub.py",
      "scripts/phase27a_strategy_proposal_capture_certification.py",
      "scripts/phase29b_historical_replay_input_contract_certification.py",
      "scripts/phase31f_replay_metrics_contract.py",
      "scripts/phase43b_qwen_context_response_contract_rollup_certification.py",
      "scripts/phase33d_entry_exit_signal_contract_stub.py",
      "scripts/phase27b_strategy_candidate_review_index.py",
      "scripts/phase35c_exit_signal_generator_disabled_stub.py",
      "scripts/phase35d_exit_signal_pipeline_rollup_certification.py",
      "scripts/phase34b_entry_signal_rule_validation_stub.py",
      "scripts/phase10_domain_subsystem_visualization.py",
      "scripts/phase35e_strategy_sandbox_wiregraph_certification.py",
      "scripts/phase34d_entry_signal_pipeline_rollup_certification.py",
      "scripts/phase14e_strategy_service_chain_graph_export.py",
      "scripts/phase49a_qwen_read_only_architecture_session_contract_stub.py",
      "scripts/phase27b_strategy_candidate_review_index_certification.py",
      "scripts/phase14f_strategy_decision_service_chain_certification.py",
      "scripts/phase14g_strategy_chain_dashboard_certification.py",
      "scripts/phase14g_add_strategy_chain_to_dashboard.py",
      "scripts/phase33e_hold_signal_generator_stub.py",
      "scripts/phase34c_entry_signal_generator_disabled_stub.py",
      "scripts/phase43a_qwen_context_response_contract_stub.py",
      "scripts/phase29b_historical_replay_input_contract.py",
      "scripts/phase30c_historical_bars_contract.py",
      "scripts/phase28d_candidate_sandbox_execution_contract_certification.py",
      "scripts/phase10c_domain_runtime_overlay_visualization.py",
      "scripts/phase27a_strategy_proposal_capture.py",
      "scripts/phase28d_candidate_sandbox_execution_contract.py",
      "scripts/phase30c_historical_bars_contract_certification.py",
      "scripts/phase35b_exit_signal_rule_validation_stub.py",
      "scripts/phase14_strategy_decision_service_chain.py",
      "scripts/phase49b_qwen_read_only_architecture_session_contract_rollup_certification.py",
      "scripts/phase33a_trade_simulation_contract_stub.py",
      "scripts/phase10_domain_subsystem_visualization_certification.py",
      "scripts/phase34a_entry_signal_rule_contract_stub.py",
      "scripts/phase9k_domain_subsystem_graph_export.py",
      "frontend/services/strategyService.ts",
      "frontend/app/api/v1/strategy/decision/[symbol]/route.ts",
      "backend/app/stacks/strategy/strategy_registry.py",
      "backend/app/stacks/strategy/strategy_service.py",
      "backend/app/stacks/strategy/strategy_runtime.py",
      "backend/app/stacks/strategy/__init__.py",
      "backend/app/stacks/strategy/selector.py",
      "backend/app/stacks/strategy/signal.py",
      "backend/app/stacks/strategy/engine.py",
      "backend/app/stacks/strategy/evolution_engine.py",
      "backend/app/stacks/strategy/llm_strategy_engine.py",
      "backend/app/stacks/strategy/candidate_registry.py"
    ]
  },
  "L3_service_facade": {
    "file_count": 36,
    "sample_files": [
      "SERVICE_RELOCATION_PLAN_RECONCILED.json",
      "SERVICE_RELOCATION_PLAN.json",
      "architecture_backup/dashboard_service.py",
      "scripts/phase13f_portfolio_positions_service_chain_certification.py",
      "scripts/phase12g_service_chain_repair.py",
      "scripts/phase21_fix_chat_service_generator.py",
      "scripts/phase12_service_layer_alignment.py",
      "scripts/phase12g_service_chain_dashboard_certification.py",
      "scripts/phase12f_service_chain_certification.py",
      "scripts/phase13e_portfolio_service_chain_graph_export.py",
      "scripts/phase20_floating_chat_widget_service_chain.py",
      "scripts/phase13_portfolio_positions_service_chain.py",
      "scripts/apply_service_relocation_v1.py",
      "scripts/phase12g_add_service_chain_to_dashboard.py",
      "scripts/service_stack_relocator_v1.py",
      "scripts/phase12e_service_chain_graph_export.py",
      "scripts/phase20e_chat_service_chain_graph_export.py",
      "frontend/services/observabilityTimelineService.ts",
      "frontend/services/graphService.ts",
      "frontend/services/marketService.ts",
      "frontend/services/requestNormalizer.ts",
      "frontend/services/chatService.ts",
      "frontend/services/requestObservability.ts",
      "frontend/services/backendHealthService.ts",
      "frontend/services/portfolioService.ts",
      "backend/app/services/__init__.py",
      "backend/app/stacks/portfolio/portfolio_service.py",
      "backend/app/stacks/portfolio/dashboard_service.py",
      "backend/app/stacks/chat_public/chat_service.py",
      "backend/app/stacks/market_data/market_data_service.py",
      "runtime/certifications/phase12g_service_chain_dashboard_certification_latest.json",
      "runtime/certifications/phase13f_portfolio_positions_service_chain_certification_latest.json",
      "runtime/certifications/phase12f_service_chain_certification_latest.json",
      "runtime/repo_memory/service_chain_graph_v1.json",
      "runtime/repo_memory/chat_service_chain_graph_v1.json",
      "runtime/repo_memory/portfolio_service_chain_graph_v1.json"
    ]
  },
  "L4_runtime_orchestration": {
    "file_count": 112,
    "sample_files": [
      "scripts/phase10d_runtime_static_dependency_diff_certification.py",
      "scripts/phase40b_sandbox_runtime_dependency_trace_rollup_certification.py",
      "scripts/phase40a_sandbox_runtime_dependency_trace_stub.py",
      "scripts/phase10c_runtime_flow_overlay_export.py",
      "scripts/phase10e_classify_runtime_static_diff_edges.py",
      "scripts/phase10c_runtime_flow_overlay_certification.py",
      "scripts/phase26b_wire_ollama_into_chat_runtime.py",
      "scripts/phase10d_runtime_static_dependency_diff.py",
      "scripts/phase62a_master_architecture_handoff_controller.py",
      "backend/app/core/runtime_firewall_v1.py",
      "backend/app/stacks/portfolio/portfolio_runtime.py",
      "backend/app/stacks/execution/sandbox_runtime.py",
      "backend/app/stacks/wolfden_ai/orchestrator.py",
      "backend/app/stacks/wolfden_ai/runtime.py",
      "backend/app/stacks/chat_public/chat_runtime.py",
      "backend/app/stacks/learning_research/research_runtime.py",
      "runtime/market_warehouse/symbol_registry.json",
      "runtime/handoff_snapshot/live_graph_validate_latest.json",
      "runtime/handoff_snapshot/file_manifest_latest.txt",
      "runtime/handoff_snapshot/topology_tree_latest.txt",
      "runtime/handoff_snapshot/neurovest_training_handoff_bundle_latest.json",
      "runtime/certifications/phase11_live_market_price_api_bridge_certification_latest.json",
      "runtime/certifications/phase22b_live_graph_visualization_certification_latest.json",
      "runtime/certifications/phase25b_tab_layout_polish_chat_panel_certification_latest.json",
      "runtime/certifications/phase17_dashboard_route_map_certification_latest.json",
      "runtime/certifications/phase10d_runtime_static_dependency_diff_certification_latest.json",
      "runtime/certifications/phase22_live_graph_tab_certification_latest.json",
      "runtime/certifications/phase28a_candidate_sandbox_simulation_harness_stub_certification_latest.json",
      "runtime/certifications/phase25c_split_dashboard_panels_into_tab_workspaces_certification_latest.json",
      "runtime/certifications/phase19c_endpoint_activation_certification_latest.json",
      "runtime/certifications/phase3m_graph_certification_latest.json",
      "runtime/certifications/phase5c_repo_memory_certification_v2_latest.json",
      "runtime/certifications/phase25a_dashboard_tab_shell_layout_navigation_certification_latest.json",
      "runtime/certifications/phase26e_chat_metadata_chips_typing_enter_certification_latest.json",
      "runtime/certifications/phase27e_candidate_sandbox_result_stub_generator_certification_latest.json",
      "runtime/certifications/phase27f_candidate_sandbox_readiness_lock_snapshot_latest.json",
      "runtime/certifications/phase24b_persist_observability_backend_health_certification_latest.json",
      "runtime/certifications/phase18_real_positions_panel_certification_latest.json",
      "runtime/certifications/phase21ab_chat_cache_history_certification_latest.json",
      "runtime/certifications/phase11f_frontend_type_lint_repair_certification_latest.json",
      "runtime/certifications/phase11c_frontend_polling_api_cleanup_certification_latest.json",
      "runtime/certifications/phase20f_floating_chat_widget_certification_latest.json",
      "runtime/certifications/phase10h_architecture_dashboard_command_certification_latest.json",
      "runtime/certifications/phase6d_dependency_graph_certification_latest.json",
      "runtime/certifications/phase23a_frontend_request_normalizer_certification_latest.json",
      "runtime/certifications/phase26d_frontend_chat_response_normalizer_certification_latest.json",
      "runtime/certifications/phase27d_candidate_sandbox_result_schema_certification_latest.json",
      "runtime/certifications/phase10e_diff_classification_certification_latest.json",
      "runtime/certifications/phase29d_historical_replay_readiness_snapshot_latest.json",
      "runtime/certifications/phase11g_live_market_dashboard_expansion_certification_latest.json"
    ]
  },
  "L5_api_presentation": {
    "file_count": 20,
    "sample_files": [
      "scripts/phase11c_frontend_polling_api_cleanup.py",
      "scripts/phase26a_chat_intent_regex_ollama_router.py",
      "scripts/phase11d_next_api_proxy_live_price.py",
      "scripts/phase11_live_market_price_api_bridge_certification.py",
      "scripts/phase11_live_market_price_api_bridge.py",
      "scripts/phase19b_endpoint_activation_probe_repair.py",
      "scripts/phase11d_next_api_proxy_live_price_certification.py",
      "scripts/phase19c_endpoint_activation_certification.py",
      "scripts/phase17_dashboard_route_map_frontend_card_verification.py",
      "scripts/phase16_api_route_separation_certification.py",
      "scripts/phase17_dashboard_route_map_certification.py",
      "scripts/phase11c_frontend_polling_api_cleanup_certification.py",
      "frontend/app/api/v1/chat/route.ts",
      "frontend/app/api/v1/graph/live/route.ts",
      "frontend/app/api/v1/market/live-price/[symbol]/route.ts",
      "frontend/app/api/v1/portfolio/positions/route.ts",
      "backend/app/api/graph_ws.py",
      "backend/app/routers/__init__.py",
      "backend/app/stacks/wolfden_ai/agent_router.py",
      "backend/app/stacks/chat_public/chat_api.py"
    ]
  },
  "L6_frontend": {
    "file_count": 104,
    "sample_files": [
      "cursor.AppImage",
      "scripts/phase23a_frontend_request_normalizer_certification.py",
      "scripts/phase26d_frontend_chat_response_normalizer_certification.py",
      "scripts/phase18_real_positions_panel_component.py",
      "scripts/phase23a_frontend_request_normalizer.py",
      "scripts/phase24a_frontend_observability_dashboard.py",
      "scripts/phase9b_component_overlay_export.py",
      "scripts/phase11f_frontend_type_lint_repair.py",
      "scripts/phase26d_frontend_chat_response_normalizer.py",
      "scripts/phase11e_frontend_build_type_certification.py",
      "scripts/phase11b_frontend_live_price_card_certification.py",
      "scripts/phase11f_frontend_type_lint_repair_certification.py",
      "scripts/phase11b_frontend_live_price_card.py",
      "scripts/phase24a_frontend_observability_dashboard_certification.py",
      "frontend/next-env.d.ts",
      "frontend/package-lock.json",
      "frontend/CLAUDE.md",
      "frontend/next.config.ts",
      "frontend/eslint.config.mjs",
      "frontend/tsconfig.json",
      "frontend/postcss.config.mjs",
      "frontend/README.md",
      "frontend/.gitignore",
      "frontend/package.json",
      "frontend/AGENTS.md",
      "frontend/app/globals.css",
      "frontend/app/layout.tsx",
      "frontend/app/page.tsx",
      "frontend/app/favicon.ico",
      "frontend/public/window.svg",
      "frontend/public/file.svg",
      "frontend/public/vercel.svg",
      "frontend/public/globe.svg",
      "frontend/public/next.svg",
      "backend/app/main.py",
      "backend/app/__init__.py",
      "backend/app/schemas/__init__.py",
      "backend/app/schemas/dashboard.py",
      "backend/app/test/test_neuro_repo_companion.py",
      "backend/app/test/test_trading_pipeline.py",
      "backend/app/analysis/architecture.py",
      "backend/app/core/cognitive_nodes.py",
      "backend/app/core/__init__.py",
      "backend/app/core/cognitive_types.py",
      "backend/app/core/config.py",
      "backend/app/core/cognitive_graph_state.py",
      "backend/app/core/cognitive_event_bus.py",
      "backend/app/core/global_firewall_v1.py",
      "backend/app/stacks/__init__.py",
      "backend/app/stacks/registry.json"
    ]
  },
  "L7_tests": {
    "file_count": 4,
    "sample_files": [
      "neuro_cli_file_inspection.json",
      "pytest.ini",
      "scripts/phase41a_safe_read_only_architecture_inspector_stub.py",
      "scripts/phase41b_safe_read_only_architecture_inspector_rollup_certification.py"
    ]
  },
  "UNCLASSIFIED": {
    "file_count": 188,
    "sample_files": [
      "OUTPUT",
      "ARCHITECTURE_REPAIR_PLAN.json",
      "TOPOLOGY_NORMALIZED_STATE.json",
      "ARCH_GOVERNANCE.md",
      "fix_phase9_self_fingerprint.sh",
      "TOPOLOGY_STATE.json",
      "topology_wire_graph.png",
      "neurovest_repo_context.md",
      "Directory Structure",
      "ORPHAN_RESOLUTION_PLAN.json",
      "topology_wire_graph_canonical.png",
      ".env.example",
      "generate_wire_graph.py",
      "neuro_health.sh",
      ".aider.input.history",
      "FINAL_ARCHITECTURE_STATE.json",
      "system_tree.txt",
      "docker-compose.yml",
      "ARCH_ENFORCEMENT_REPORT.json",
      "spine_mvp_full.sh",
      ".gitignore",
      "$OUTPUT",
      ".env",
      ".aider.chat.history.md",
      "neuro",
      "neuro_cli.py",
      "neuro_engineer.py",
      "scripts/phase59b_qwen_read_only_final_handoff_certification_rollup_certification.py",
      "scripts/phase22_live_graph_tab_certification.py",
      "scripts/phase20f_floating_chat_widget_certification.py",
      "scripts/phase48c_handoff_bundle_refresh.py",
      "scripts/phase51a_qwen_read_only_architecture_loop_boundary_stub.py",
      "scripts/phase23b_polling_governor_certification.py",
      "scripts/phase29c_historical_replay_validation_stub.py",
      "scripts/phase26f_chat_ui_state_cleanup_metadata_rendering_certification.py",
      "scripts/phase6c_dependency_graph_export.py",
      "scripts/phase25a_dashboard_tab_shell_layout_navigation_certification.py",
      "scripts/phase27d_candidate_sandbox_result_schema_certification.py",
      "scripts/phase10h_architecture_dashboard_command_certification.py",
      "scripts/phase31a_historical_bars_fetch_validation.py",
      "scripts/phase27e_candidate_sandbox_result_stub_generator.py",
      "scripts/phase54a_qwen_read_only_handoff_export_summary_stub.py",
      "scripts/phase26f_chat_ui_state_cleanup_metadata_rendering.py",
      "scripts/phase4g_repo_memory_certification.py",
      "scripts/phase25a_dashboard_tab_shell_layout_navigation.py",
      "scripts/phase21cd_chat_ux_persistent_cache.py",
      "scripts/phase47b_qwen_read_only_recommendation_filter_rollup_certification.py",
      "scripts/phase11g_live_market_dashboard_expansion.py",
      "scripts/phase28b_candidate_sandbox_mock_metrics_generator.py",
      "scripts/phase32a_real_metrics_generation.py"
    ]
  }
}
```


# Stack Topology

```json
{
  "auth": {
    "file_count": 4,
    "sample_files": [
      "backend/app/stacks/auth_identity/__init__.py",
      "backend/app/stacks/auth_identity/base.py",
      "backend/app/stacks/auth_identity/validator.py",
      "backend/app/stacks/auth_identity/gate.py"
    ]
  },
  "backend_uncategorized": {
    "file_count": 27,
    "sample_files": [
      "backend/__init__.py",
      "backend/requirements.txt",
      "backend/app/main.py",
      "backend/app/__init__.py",
      "backend/scripts/backup_db.sh",
      "backend/app/schemas/__init__.py",
      "backend/app/schemas/dashboard.py",
      "backend/app/test/test_neuro_repo_companion.py",
      "backend/app/test/test_trading_pipeline.py",
      "backend/app/api/graph_ws.py",
      "backend/app/services/__init__.py",
      "backend/app/analysis/architecture.py",
      "backend/app/core/cognitive_nodes.py",
      "backend/app/core/__init__.py",
      "backend/app/core/cognitive_types.py",
      "backend/app/core/config.py",
      "backend/app/core/cognitive_graph_state.py",
      "backend/app/core/cognitive_event_bus.py",
      "backend/app/core/runtime_firewall_v1.py",
      "backend/app/core/global_firewall_v1.py",
      "backend/app/stacks/__init__.py",
      "backend/app/stacks/registry.json",
      "backend/app/routers/__init__.py",
      "backend/app/stacks/db_model/__init__.py",
      "backend/app/stacks/db_model/market_schema.py",
      "backend/app/stacks/db_model/base.py",
      "backend/app/stacks/events/broker.py"
    ]
  },
  "chat": {
    "file_count": 43,
    "sample_files": [
      ".aider.chat.history.md",
      "scripts/phase20f_floating_chat_widget_certification.py",
      "scripts/phase26f_chat_ui_state_cleanup_metadata_rendering_certification.py",
      "scripts/phase26d_frontend_chat_response_normalizer_certification.py",
      "scripts/phase26f_chat_ui_state_cleanup_metadata_rendering.py",
      "scripts/phase21cd_chat_ux_persistent_cache.py",
      "scripts/phase21_fix_chat_service_generator.py",
      "scripts/phase26a_chat_intent_regex_ollama_router.py",
      "scripts/phase26e_chat_metadata_chips_typing_enter_certification.py",
      "scripts/phase20_floating_chat_widget_service_chain.py",
      "scripts/phase21cd_chat_ux_persistent_cache_certification.py",
      "scripts/phase26b_wire_ollama_into_chat_runtime.py",
      "scripts/phase25b_tab_layout_polish_chat_panel.py",
      "scripts/phase26d_frontend_chat_response_normalizer.py",
      "scripts/phase21ab_chat_cache_history_certification.py",
      "scripts/phase61a_archive_or_new_chat_handoff_summary.py",
      "scripts/phase26e_chat_metadata_chips_typing_enter.py",
      "scripts/phase21ab_chat_cache_history.py",
      "scripts/phase20e_chat_service_chain_graph_export.py",
      "scripts/phase25b_tab_layout_polish_chat_panel_certification.py",
      "frontend/services/chatService.ts",
      "frontend/app/api/v1/chat/route.ts",
      "backend/app/stacks/chat_public/chat_intent_regex.py",
      "backend/app/stacks/chat_public/context_loader.py",
      "backend/app/stacks/chat_public/__init__.py",
      "backend/app/stacks/chat_public/chat_runtime.py",
      "backend/app/stacks/chat_public/chat_system_prompt.py",
      "backend/app/stacks/chat_public/conversation_store.py",
      "backend/app/stacks/chat_public/chat_memory.py",
      "backend/app/stacks/chat_public/ollama_chat_client.py",
      "backend/app/stacks/chat_public/chat_service.py",
      "backend/app/stacks/chat_public/time_context.py",
      "backend/app/stacks/chat_public/strategy_proposal_capture.py",
      "backend/app/stacks/chat_public/base.py",
      "backend/app/stacks/chat_public/chat_api.py",
      "runtime/certifications/phase25b_tab_layout_polish_chat_panel_certification_latest.json",
      "runtime/certifications/phase26e_chat_metadata_chips_typing_enter_certification_latest.json",
      "runtime/certifications/phase21ab_chat_cache_history_certification_latest.json",
      "runtime/certifications/phase20f_floating_chat_widget_certification_latest.json",
      "runtime/certifications/phase26d_frontend_chat_response_normalizer_certification_latest.json"
    ]
  },
  "execution": {
    "file_count": 19,
    "sample_files": [
      "scripts/phase28d_candidate_sandbox_execution_contract_certification.py",
      "scripts/phase28d_candidate_sandbox_execution_contract.py",
      "scripts/phase26c_chat_safety_prompt_live_execution_guard_certification.py",
      "backend/app/stacks/execution/__init__.py",
      "backend/app/stacks/execution/sandbox_runtime.py",
      "backend/app/stacks/execution/commission_engine.py",
      "backend/app/stacks/execution/sandbox.py",
      "backend/app/stacks/execution/regime_modes.py",
      "backend/app/stacks/execution/pnl_engine.py",
      "backend/app/stacks/execution/executor.py",
      "backend/app/stacks/execution/trade_ledger.py",
      "backend/app/stacks/execution/regime_simulator.py",
      "backend/app/stacks/execution/paper_broker.py",
      "backend/app/stacks/execution/broker.py",
      "backend/app/stacks/execution/fill_engine.py",
      "backend/app/stacks/execution/base.py",
      "backend/app/stacks/execution/accounting_engine.py",
      "runtime/certifications/phase26c_chat_safety_prompt_live_execution_guard_certification_latest.json",
      "runtime/certifications/phase28d_candidate_sandbox_execution_contract_certification_latest.json"
    ]
  },
  "frontend": {
    "file_count": 28,
    "sample_files": [
      "frontend/next-env.d.ts",
      "frontend/package-lock.json",
      "frontend/CLAUDE.md",
      "frontend/next.config.ts",
      "frontend/eslint.config.mjs",
      "frontend/tsconfig.json",
      "frontend/postcss.config.mjs",
      "frontend/README.md",
      "frontend/.gitignore",
      "frontend/package.json",
      "frontend/AGENTS.md",
      "frontend/app/globals.css",
      "frontend/app/layout.tsx",
      "frontend/app/page.tsx",
      "frontend/app/favicon.ico",
      "frontend/services/observabilityTimelineService.ts",
      "frontend/services/graphService.ts",
      "frontend/services/marketService.ts",
      "frontend/services/requestNormalizer.ts",
      "frontend/services/requestObservability.ts",
      "frontend/services/backendHealthService.ts",
      "frontend/public/window.svg",
      "frontend/public/file.svg",
      "frontend/public/vercel.svg",
      "frontend/public/globe.svg",
      "frontend/public/next.svg",
      "frontend/app/api/v1/graph/live/route.ts",
      "frontend/app/api/v1/market/live-price/[symbol]/route.ts"
    ]
  },
  "journal": {
    "file_count": 4,
    "sample_files": [
      "backend/app/stacks/journal_ledger/ledger.py",
      "backend/app/stacks/journal_ledger/__init__.py",
      "backend/app/stacks/journal_ledger/record.py",
      "backend/app/stacks/journal_ledger/base.py"
    ]
  },
  "learning": {
    "file_count": 9,
    "sample_files": [
      "backend/app/stacks/learning_research/strategy_evaluator.py",
      "backend/app/stacks/learning_research/__init__.py",
      "backend/app/stacks/learning_research/monte_carlo_mix.py",
      "backend/app/stacks/learning_research/monte_carlo.py",
      "backend/app/stacks/learning_research/research_loader.py",
      "backend/app/stacks/learning_research/probability_engine.py",
      "backend/app/stacks/learning_research/research_runtime.py",
      "backend/app/stacks/learning_research/base.py",
      "backend/app/stacks/learning_research/backtest_engine.py"
    ]
  },
  "market_data": {
    "file_count": 15,
    "sample_files": [
      "scripts/phase29e_historical_replay_market_data_provider_contract_certification.py",
      "scripts/phase29e_historical_replay_market_data_provider_contract.py",
      "backend/app/stacks/market_data/yfinance_ingestor.py",
      "backend/app/stacks/market_data/provider_registry.py",
      "backend/app/stacks/market_data/__init__.py",
      "backend/app/stacks/market_data/feed.py",
      "backend/app/stacks/market_data/market_data_service.py",
      "backend/app/stacks/market_data/bars.py",
      "backend/app/stacks/market_data/market_session.py",
      "backend/app/stacks/market_data/provider_router.py",
      "backend/app/stacks/market_data/price.py",
      "backend/app/stacks/market_data/yfinance_historical_bars_adapter.py",
      "backend/app/stacks/market_data/provider_cache.py",
      "backend/app/stacks/market_data/base.py",
      "runtime/certifications/phase29e_historical_replay_market_data_provider_contract_certification_latest.json"
    ]
  },
  "notification": {
    "file_count": 2,
    "sample_files": [
      "backend/app/stacks/notification/__init__.py",
      "backend/app/stacks/notification/base.py"
    ]
  },
  "portfolio": {
    "file_count": 19,
    "sample_files": [
      "scripts/phase13f_portfolio_positions_service_chain_certification.py",
      "scripts/phase13e_portfolio_service_chain_graph_export.py",
      "scripts/phase13_portfolio_positions_service_chain.py",
      "scripts/phase13g_portfolio_chain_dashboard_certification.py",
      "scripts/phase13g_add_portfolio_chain_to_dashboard.py",
      "frontend/services/portfolioService.ts",
      "frontend/app/api/v1/portfolio/positions/route.ts",
      "backend/app/stacks/portfolio/portfolio_service.py",
      "backend/app/stacks/portfolio/allocator.py",
      "backend/app/stacks/portfolio/__init__.py",
      "backend/app/stacks/portfolio/accounting.py",
      "backend/app/stacks/portfolio/portfolio_runtime.py",
      "backend/app/stacks/portfolio/reconciliation.py",
      "backend/app/stacks/portfolio/dashboard_service.py",
      "backend/app/stacks/portfolio/rebalance.py",
      "backend/app/stacks/portfolio/base.py",
      "runtime/certifications/phase13f_portfolio_positions_service_chain_certification_latest.json",
      "runtime/certifications/phase13g_portfolio_chain_dashboard_certification_latest.json",
      "runtime/repo_memory/portfolio_service_chain_graph_v1.json"
    ]
  },
  "research": {
    "file_count": 2,
    "sample_files": [
      "scripts/phase1_repo_research_market_bootstrap.py",
      "runtime/research_db/research_seed.json"
    ]
  },
  "risk": {
    "file_count": 22,
    "sample_files": [
      "scripts/phase15_risk_gate_service_chain.py",
      "scripts/phase15g_add_risk_chain_to_dashboard.py",
      "scripts/phase38b_risk_gate_validation_stub.py",
      "scripts/phase15e_risk_service_chain_graph_export.py",
      "scripts/phase38c_risk_gate_pipeline_rollup_certification.py",
      "scripts/phase15g_risk_chain_dashboard_certification.py",
      "scripts/phase15f_risk_gate_service_chain_certification.py",
      "scripts/phase38a_risk_gate_contract_stub.py",
      "frontend/services/riskService.ts",
      "frontend/app/api/v1/risk/gate/[symbol]/route.ts",
      "backend/app/stacks/risk/loss_streak_guard.py",
      "backend/app/stacks/risk/__init__.py",
      "backend/app/stacks/risk/drawdown_guard.py",
      "backend/app/stacks/risk/risk_runtime_service.py",
      "backend/app/stacks/risk/exposure.py",
      "backend/app/stacks/risk/kill_switch.py",
      "backend/app/stacks/risk/limits.py",
      "backend/app/stacks/risk/base.py",
      "backend/app/stacks/risk/risk_service.py",
      "runtime/certifications/phase15g_risk_chain_dashboard_certification_latest.json",
      "runtime/certifications/phase15f_risk_gate_service_chain_certification_latest.json",
      "runtime/repo_memory/risk_service_chain_graph_v1.json"
    ]
  },
  "runtime_artifacts": {
    "file_count": 103,
    "sample_files": [
      "runtime/market_warehouse/symbol_registry.json",
      "runtime/handoff_snapshot/live_graph_validate_latest.json",
      "runtime/handoff_snapshot/file_manifest_latest.txt",
      "runtime/handoff_snapshot/simulate_trade_guard_latest.json",
      "runtime/handoff_snapshot/topology_tree_latest.txt",
      "runtime/handoff_snapshot/neurovest_training_handoff_bundle_latest.json",
      "runtime/certifications/phase11_live_market_price_api_bridge_certification_latest.json",
      "runtime/certifications/phase22b_live_graph_visualization_certification_latest.json",
      "runtime/certifications/phase30f_yfinance_historical_bars_adapter_wire_preview_certification_latest.json",
      "runtime/certifications/phase17_dashboard_route_map_certification_latest.json",
      "runtime/certifications/phase30b_yfinance_provider_selection_snapshot_latest.json",
      "runtime/certifications/phase10d_runtime_static_dependency_diff_certification_latest.json",
      "runtime/certifications/phase12g_service_chain_dashboard_certification_latest.json",
      "runtime/certifications/phase22_live_graph_tab_certification_latest.json",
      "runtime/certifications/phase28a_candidate_sandbox_simulation_harness_stub_certification_latest.json",
      "runtime/certifications/phase25c_split_dashboard_panels_into_tab_workspaces_certification_latest.json",
      "runtime/certifications/phase19c_endpoint_activation_certification_latest.json",
      "runtime/certifications/phase3m_graph_certification_latest.json",
      "runtime/certifications/phase5c_repo_memory_certification_v2_latest.json",
      "runtime/certifications/phase25a_dashboard_tab_shell_layout_navigation_certification_latest.json",
      "runtime/certifications/phase27e_candidate_sandbox_result_stub_generator_certification_latest.json",
      "runtime/certifications/phase29g_historical_replay_provider_readiness_snapshot_latest.json",
      "runtime/certifications/phase27f_candidate_sandbox_readiness_lock_snapshot_latest.json",
      "runtime/certifications/phase24b_persist_observability_backend_health_certification_latest.json",
      "runtime/certifications/phase30a_yfinance_historical_bars_provider_probe_certification_latest.json",
      "runtime/certifications/phase18_real_positions_panel_certification_latest.json",
      "runtime/certifications/phase11f_frontend_type_lint_repair_certification_latest.json",
      "runtime/certifications/phase11c_frontend_polling_api_cleanup_certification_latest.json",
      "runtime/certifications/phase10h_architecture_dashboard_command_certification_latest.json",
      "runtime/certifications/phase6d_dependency_graph_certification_latest.json",
      "runtime/certifications/phase23a_frontend_request_normalizer_certification_latest.json",
      "runtime/certifications/phase29f_historical_replay_provider_adapter_stub_certification_latest.json",
      "runtime/certifications/phase27d_candidate_sandbox_result_schema_certification_latest.json",
      "runtime/certifications/phase10e_diff_classification_certification_latest.json",
      "runtime/certifications/phase30g_yfinance_historical_bars_adapter_wire_certification_latest.json",
      "runtime/certifications/phase10_domain_subsystem_visualization_certification_latest.json",
      "runtime/certifications/phase29d_historical_replay_readiness_snapshot_latest.json",
      "runtime/certifications/phase11g_live_market_dashboard_expansion_certification_latest.json",
      "runtime/certifications/phase9e_canonical_graph_certification_latest.json",
      "runtime/certifications/phase24d_observability_lock_handoff_snapshot_latest.json"
    ]
  },
  "snaptrade": {
    "file_count": 7,
    "sample_files": [
      "backend/app/snaptrade/executions/config.py",
      "backend/app/snaptrade/executions/execution_layer.py",
      "backend/app/stacks/snaptrade/__init__.py",
      "backend/app/stacks/snaptrade/execution.py",
      "backend/app/stacks/snaptrade/adapter.py",
      "backend/app/stacks/snaptrade/broker.py",
      "backend/app/stacks/snaptrade/base.py"
    ]
  },
  "strategy": {
    "file_count": 247,
    "sample_files": [
      "scripts/phase36a_strategy_rule_enablement_gate_contract_stub.py",
      "scripts/phase27a_strategy_proposal_capture_certification.py",
      "scripts/phase27b_strategy_candidate_review_index.py",
      "scripts/phase35e_strategy_sandbox_wiregraph_certification.py",
      "scripts/phase14e_strategy_service_chain_graph_export.py",
      "scripts/phase27b_strategy_candidate_review_index_certification.py",
      "scripts/phase14f_strategy_decision_service_chain_certification.py",
      "scripts/phase14g_strategy_chain_dashboard_certification.py",
      "scripts/phase14g_add_strategy_chain_to_dashboard.py",
      "scripts/phase27a_strategy_proposal_capture.py",
      "scripts/phase14_strategy_decision_service_chain.py",
      "frontend/services/strategyService.ts",
      "frontend/app/api/v1/strategy/decision/[symbol]/route.ts",
      "backend/app/stacks/strategy/strategy_registry.py",
      "backend/app/stacks/strategy/strategy_service.py",
      "backend/app/stacks/strategy/strategy_runtime.py",
      "backend/app/stacks/strategy/__init__.py",
      "backend/app/stacks/strategy/selector.py",
      "backend/app/stacks/strategy/signal.py",
      "backend/app/stacks/strategy/engine.py",
      "backend/app/stacks/strategy/evolution_engine.py",
      "backend/app/stacks/strategy/llm_strategy_engine.py",
      "backend/app/stacks/strategy/candidate_registry.py",
      "backend/app/stacks/strategy/base.py",
      "backend/app/stacks/strategy_candidate_sandbox/replay_metrics_generator.py",
      "backend/app/stacks/strategy_candidate_sandbox/hold_signal_generator_stub.py",
      "backend/app/stacks/strategy_candidate_sandbox/qwen_context_response_contract.py",
      "backend/app/stacks/strategy_candidate_sandbox/replay_metrics_contract.py",
      "backend/app/stacks/strategy_candidate_sandbox/strategy_rule_enablement_gate_contract.py",
      "backend/app/stacks/strategy_candidate_sandbox/safe_read_only_architecture_inspector.py",
      "backend/app/stacks/strategy_candidate_sandbox/trade_event_validator.py",
      "backend/app/stacks/strategy_candidate_sandbox/entry_exit_signal_contract.py",
      "backend/app/stacks/strategy_candidate_sandbox/hold_decision_to_hold_event_bridge.py",
      "backend/app/stacks/strategy_candidate_sandbox/entry_signal_rule_contract.py",
      "backend/app/stacks/strategy_candidate_sandbox/exit_signal_rule_contract.py",
      "backend/app/stacks/strategy_candidate_sandbox/qwen_read_only_architecture_summary_gate.py",
      "backend/app/stacks/strategy_candidate_sandbox/trade_simulation_enablement_gate_contract.py",
      "backend/app/stacks/strategy_candidate_sandbox/exit_signal_rule_validator.py",
      "backend/app/stacks/strategy_candidate_sandbox/qwen_read_only_architecture_context.py",
      "backend/app/stacks/strategy_candidate_sandbox/risk_gate_validator.py"
    ]
  },
  "unknown": {
    "file_count": 269,
    "sample_files": [
      "OUTPUT",
      "ARCHITECTURE_REPAIR_PLAN.json",
      "TOPOLOGY_NORMALIZED_STATE.json",
      "ARCH_GOVERNANCE.md",
      "fix_phase9_self_fingerprint.sh",
      "TOPOLOGY_STATE.json",
      "topology_wire_graph.png",
      "neurovest_repo_context.md",
      "Directory Structure",
      "ORPHAN_RESOLUTION_PLAN.json",
      "topology_wire_graph_canonical.png",
      ".env.example",
      "domain_subsystem_graph.png",
      "generate_wire_graph.py",
      "neuro_health.sh",
      "neuro_cli_file_inspection.json",
      ".aider.input.history",
      "FINAL_ARCHITECTURE_STATE.json",
      "system_tree.txt",
      "docker-compose.yml",
      "ARCH_ENFORCEMENT_REPORT.json",
      "spine_mvp_full.sh",
      "pytest.ini",
      ".gitignore",
      "$OUTPUT",
      "SERVICE_RELOCATION_PLAN_RECONCILED.json",
      ".env",
      "domain_runtime_overlay_graph.png",
      "cursor.AppImage",
      "neuro",
      "neuro_cli.py",
      "neuro_engineer.py",
      "SERVICE_RELOCATION_PLAN.json",
      "architecture_backup/dashboard_service.py",
      "scripts/phase59b_qwen_read_only_final_handoff_certification_rollup_certification.py",
      "scripts/phase22_live_graph_tab_certification.py",
      "scripts/phase48c_handoff_bundle_refresh.py",
      "scripts/phase51a_qwen_read_only_architecture_loop_boundary_stub.py",
      "scripts/phase30g_yfinance_historical_bars_adapter_wire.py",
      "scripts/phase10d_runtime_static_dependency_diff_certification.py"
    ]
  },
  "wolfden": {
    "file_count": 7,
    "sample_files": [
      "backend/app/stacks/wolfden_ai/memory.py",
      "backend/app/stacks/wolfden_ai/__init__.py",
      "backend/app/stacks/wolfden_ai/agent_router.py",
      "backend/app/stacks/wolfden_ai/orchestrator.py",
      "backend/app/stacks/wolfden_ai/routing.py",
      "backend/app/stacks/wolfden_ai/runtime.py",
      "backend/app/stacks/wolfden_ai/base.py"
    ]
  }
}
```


# Repository Tree

```text
./
├── .aider.tags.cache.v4/
│   ├── cache.db
│   ├── cache.db-shm
│   └── cache.db-wal
├── .github/
│   └── workflows/
│       └── architecture_ci.yml
├── architecture_backup/
│   └── dashboard_service.py
├── backend/
│   ├── app/
│   │   ├── analysis/
│   │   │   └── architecture.py
│   │   ├── api/
│   │   │   └── graph_ws.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── cognitive_event_bus.py
│   │   │   ├── cognitive_graph_state.py
│   │   │   ├── cognitive_nodes.py
│   │   │   ├── cognitive_types.py
│   │   │   ├── config.py
│   │   │   ├── global_firewall_v1.py
│   │   │   └── runtime_firewall_v1.py
│   │   ├── models/
│   │   ├── routers/
│   │   │   └── __init__.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── dashboard.py
│   │   ├── services/
│   │   │   └── __init__.py
│   │   ├── snaptrade/
│   │   │   └── executions/
│   │   ├── stacks/
│   │   │   ├── auth_identity/
│   │   │   ├── chat_public/
│   │   │   ├── db_model/
│   │   │   ├── events/
│   │   │   ├── execution/
│   │   │   ├── journal_ledger/
│   │   │   ├── learning_research/
│   │   │   ├── market_data/
│   │   │   ├── notification/
│   │   │   ├── portfolio/
│   │   │   ├── risk/
│   │   │   ├── snaptrade/
│   │   │   ├── strategy/
│   │   │   ├── strategy_candidate_sandbox/
│   │   │   ├── wolfden_ai/
│   │   │   ├── __init__.py
│   │   │   └── registry.json
│   │   ├── test/
│   │   │   ├── test_neuro_repo_companion.py
│   │   │   └── test_trading_pipeline.py
│   │   ├── __init__.py
│   │   └── main.py
│   ├── scripts/
│   │   └── backup_db.sh
│   ├── __init__.py
│   └── requirements.txt
├── backups/
│   └── neurovest_backup_20260703_215801.sql.gz
├── frontend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   ├── favicon.ico
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── public/
│   │   ├── file.svg
│   │   ├── globe.svg
│   │   ├── next.svg
│   │   ├── vercel.svg
│   │   └── window.svg
│   ├── services/
│   │   ├── backendHealthService.ts
│   │   ├── chatService.ts
│   │   ├── graphService.ts
│   │   ├── marketService.ts
│   │   ├── observabilityTimelineService.ts
│   │   ├── portfolioService.ts
│   │   ├── requestNormalizer.ts
│   │   ├── requestObservability.ts
│   │   ├── riskService.ts
│   │   └── strategyService.ts
│   ├── .gitignore
│   ├── AGENTS.md
│   ├── CLAUDE.md
│   ├── eslint.config.mjs
│   ├── next-env.d.ts
│   ├── next.config.ts
│   ├── package-lock.json
│   ├── package.json
│   ├── postcss.config.mjs
│   ├── README.md
│   └── tsconfig.json
├── handoff/
├── runtime/
│   ├── certifications/
│   │   ├── phase10_domain_subsystem_visualization_certification_latest.json
│   │   ├── phase10c_runtime_flow_overlay_certification_latest.json
│   │   ├── phase10d_runtime_static_dependency_diff_certification_latest.json
│   │   ├── phase10e_diff_classification_certification_latest.json
│   │   ├── phase10f_architecture_drift_watch_certification_latest.json
│   │   ├── phase10g_architecture_drift_dashboard_certification_latest.json
│   │   ├── phase10h_architecture_dashboard_command_certification_latest.json
│   │   ├── phase11_live_market_price_api_bridge_certification_latest.json
│   │   ├── phase11b_frontend_live_price_card_certification_latest.json
│   │   ├── phase11c_frontend_polling_api_cleanup_certification_latest.json
│   │   ├── phase11d_next_api_proxy_live_price_certification_latest.json
│   │   ├── phase11e_frontend_build_type_certification_latest.json
│   │   ├── phase11f_frontend_type_lint_repair_certification_latest.json
│   │   ├── phase11g_live_market_dashboard_expansion_certification_latest.json
│   │   ├── phase12f_service_chain_certification_latest.json
│   │   ├── phase12g_service_chain_dashboard_certification_latest.json
│   │   ├── phase13f_portfolio_positions_service_chain_certification_latest.json
│   │   ├── phase13g_portfolio_chain_dashboard_certification_latest.json
│   │   ├── phase14f_strategy_decision_service_chain_certification_latest.json
│   │   ├── phase14g_strategy_chain_dashboard_certification_latest.json
│   │   ├── phase15f_risk_gate_service_chain_certification_latest.json
│   │   ├── phase15g_risk_chain_dashboard_certification_latest.json
│   │   ├── phase16_api_route_separation_certification_latest.json
│   │   ├── phase17_dashboard_route_map_certification_latest.json
│   │   ├── phase18_real_positions_panel_certification_latest.json
│   │   ├── phase19_dashboard_visual_layout_certification_latest.json
│   │   ├── phase19c_endpoint_activation_certification_latest.json
│   │   ├── phase20f_floating_chat_widget_certification_latest.json
│   │   ├── phase21ab_chat_cache_history_certification_latest.json
│   │   ├── phase21cd_chat_ux_persistent_cache_certification_latest.json
│   │   ├── phase22_live_graph_tab_certification_latest.json
│   │   ├── phase22b_live_graph_visualization_certification_latest.json
│   │   ├── phase23a_frontend_request_normalizer_certification_latest.json
│   │   ├── phase23b_polling_governor_certification_latest.json
│   │   ├── phase24a_frontend_observability_dashboard_certification_latest.json
│   │   ├── phase24b_persist_observability_backend_health_certification_latest.json
│   │   ├── phase24c_observability_event_timeline_certification_latest.json
│   │   ├── phase24d_observability_lock_handoff_snapshot_latest.json
│   │   ├── phase25a_dashboard_tab_shell_layout_navigation_certification_latest.json
│   │   ├── phase25b_tab_layout_polish_chat_panel_certification_latest.json
│   │   ├── phase25c_split_dashboard_panels_into_tab_workspaces_certification_latest.json
│   │   ├── phase26c_chat_safety_prompt_live_execution_guard_certification_latest.json
│   │   ├── phase26d_frontend_chat_response_normalizer_certification_latest.json
│   │   ├── phase26e_chat_metadata_chips_typing_enter_certification_latest.json
│   │   ├── phase26f_chat_ui_state_cleanup_metadata_rendering_certification_latest.json
│   │   ├── phase27a_strategy_proposal_capture_certification_latest.json
│   │   ├── phase27b_strategy_candidate_review_index_certification_latest.json
│   │   ├── phase27c_candidate_sandbox_dry_run_stub_certification_latest.json
│   │   ├── phase27d_candidate_sandbox_result_schema_certification_latest.json
│   │   ├── phase27e_candidate_sandbox_result_stub_generator_certification_latest.json
│   │   ├── phase27f_candidate_sandbox_readiness_lock_snapshot_latest.json
│   │   ├── phase28a_candidate_sandbox_simulation_harness_stub_certification_latest.json
│   │   ├── phase28b_candidate_sandbox_mock_metrics_generator_certification_latest.json
│   │   ├── phase28c_candidate_sandbox_mock_scorecard_certification_latest.json
│   │   ├── phase28d_candidate_sandbox_execution_contract_certification_latest.json
│   │   ├── phase29a_historical_replay_engine_stub_certification_latest.json
│   │   ├── phase29b_historical_replay_input_contract_certification_latest.json
│   │   ├── phase29c_historical_replay_validation_stub_certification_latest.json
│   │   ├── phase29d_historical_replay_readiness_snapshot_latest.json
│   │   ├── phase29e_historical_replay_market_data_provider_contract_certification_latest.json
│   │   ├── phase29f_historical_replay_provider_adapter_stub_certification_latest.json
│   │   ├── phase29g_historical_replay_provider_readiness_snapshot_latest.json
│   │   ├── phase30a_yfinance_historical_bars_provider_probe_certification_latest.json
│   │   ├── phase30b_yfinance_provider_selection_snapshot_latest.json
│   │   ├── phase30c_historical_bars_contract_certification_latest.json
│   │   ├── phase30d_yfinance_historical_bars_adapter_stub_certification_latest.json
│   │   ├── phase30e_yfinance_historical_bars_adapter_shape_validation_certification_latest.json
│   │   ├── phase30f_yfinance_historical_bars_adapter_wire_preview_certification_latest.json
│   │   ├── phase30g_yfinance_historical_bars_adapter_wire_certification_latest.json
│   │   ├── phase3m_graph_certification_latest.json
│   │   ├── phase4g_repo_memory_certification_latest.json
│   │   ├── phase5c_repo_memory_certification_v2_latest.json
│   │   ├── phase6b_dependency_validation_certification_latest.json
│   │   ├── phase6d_dependency_graph_certification_latest.json
│   │   ├── phase7g_graph_visualization_certification_latest.json
│   │   ├── phase8c_neuro_cli_hotspots_certification_latest.json
│   │   ├── phase9e_canonical_graph_certification_latest.json
│   │   └── phase9m_canonical_graph_certification_v2_latest.json
│   ├── graph_history/
│   │   ├── current_snapshot.json
│   │   └── events.jsonl
│   ├── handoff_snapshot/
│   │   ├── file_manifest_latest.txt
│   │   ├── live_graph_validate_latest.json
│   │   ├── neurovest_training_handoff_bundle_latest.json
│   │   ├── simulate_trade_guard_latest.json
│   │   └── topology_tree_latest.txt
│   ├── market_warehouse/
│   │   ├── history/
│   │   │   ├── AAPL_history.csv
│   │   │   ├── MSFT_history.csv
│   │   │   ├── NVDA_history.csv
│   │   │   ├── RY_TO_history.csv
│   │   │   ├── TD_TO_history.csv
│   │   │   ├── TSLA_history.csv
│   │   │   ├── VFV_TO_history.csv
│   │   │   └── VUN_TO_history.csv
│   │   ├── live/
│   │   │   ├── AAPL_live.json
│   │   │   ├── MSFT_live.json
│   │   │   ├── NVDA_live.json
│   │   │   ├── RY_TO_live.json
│   │   │   ├── TD_TO_live.json
│   │   │   ├── TSLA_live.json
│   │   │   ├── VFV_TO_live.json
│   │   │   └── VUN_TO_live.json
│   │   └── symbol_registry.json
│   ├── repo_memory/
│   │   ├── architecture_drift_dashboard_v1.json
│   │   ├── architecture_drift_dashboard_v1.txt
│   │   ├── canonical_layer_graph_v1.json
│   │   ├── chat_service_chain_graph_v1.json
│   │   ├── component_overlay_v1.json
│   │   ├── dashboard_route_map_v1.json
│   │   ├── dependency_graph_v1.json
│   │   ├── dependency_topology_overlay_v1.json
│   │   ├── domain_subsystem_graph_v1.json
│   │   ├── phase4c_loose_root_duplicate_quarantine_plan_latest.json
│   │   ├── phase4d_root_shadow_diff_report_latest.json
│   │   ├── phase4d_root_shadow_diff_report_latest.txt
│   │   ├── phase4e_quarantine_root_shadows_latest.json
│   │   ├── portfolio_service_chain_graph_v1.json
│   │   ├── repo_index.json
│   │   ├── repo_index_v2.json
│   │   ├── risk_service_chain_graph_v1.json
│   │   ├── runtime_flow_overlay_v1.json
│   │   ├── runtime_static_dependency_diff_v1.json
│   │   ├── runtime_static_diff_classification_v1.json
│   │   ├── service_chain_graph_v1.json
│   │   ├── stack_layer_sankey_v1.json
│   │   └── strategy_service_chain_graph_v1.json
│   ├── research_db/
│   │   └── research_seed.json
│   ├── strategy_candidate_sandbox/
│   │   ├── 31A_historical_bars_fetch_validation_latest.json
│   │   ├── 31B_historical_bars_multi_symbol_validation_latest.json
│   │   ├── 31C_historical_replay_executor_stub_latest.json
│   │   ├── 31D_historical_replay_bar_iterator_latest.json
│   │   ├── 31E_first_single_candidate_replay_dry_run_latest.json
│   │   ├── 31F_replay_metrics_contract_latest.json
│   │   ├── 32A_real_metrics_generation_latest.json
│   │   ├── 32B_candidate_scorecard_from_replay_metrics_latest.json
│   │   ├── 32C_manual_promotion_gate_stub_latest.json
│   │   ├── 32D_pipeline_rollup_certification_latest.json
│   │   ├── 32E_handoff_bundle_refresh_latest.json
│   │   ├── 33A_trade_simulation_contract_stub_latest.json
│   │   ├── 33B_trade_event_validation_stub_latest.json
│   │   ├── 33C_trade_simulation_dry_run_stub_latest.json
│   │   ├── 33D_entry_exit_signal_contract_stub_latest.json
│   │   ├── 33E_hold_signal_generator_stub_latest.json
│   │   ├── 33F_entry_exit_decision_engine_stub_latest.json
│   │   ├── 33G_hold_decision_to_hold_event_bridge_latest.json
│   │   ├── 33H_trade_simulation_pipeline_rollup_certification_latest.json
│   │   ├── 33I_handoff_bundle_refresh_latest.json
│   │   ├── 34A_entry_signal_rule_contract_stub_latest.json
│   │   ├── 34B_entry_signal_rule_validation_stub_latest.json
│   │   ├── 34C_entry_signal_generator_disabled_stub_latest.json
│   │   ├── 34D_entry_signal_pipeline_rollup_certification_latest.json
│   │   ├── 34E_handoff_bundle_refresh_latest.json
│   │   ├── 35A_exit_signal_rule_contract_stub_latest.json
│   │   ├── 35B_exit_signal_rule_validation_stub_latest.json
│   │   ├── 35C_exit_signal_generator_disabled_stub_latest.json
│   │   ├── 35D_exit_signal_pipeline_rollup_certification_latest.json
│   │   ├── 35E_strategy_sandbox_wiregraph_latest.json
│   │   ├── 35E_strategy_sandbox_wiregraph_latest.mmd
│   │   ├── 35F_handoff_bundle_refresh_latest.json
│   │   ├── 36A_strategy_rule_enablement_gate_contract_stub_latest.json
│   │   ├── 36B_enablement_gate_validation_stub_latest.json
│   │   ├── 36C_enablement_gate_pipeline_rollup_certification_latest.json
│   │   ├── 36D_handoff_bundle_refresh_latest.json
│   │   ├── 37A_trade_simulation_enablement_gate_contract_stub_latest.json
│   │   ├── 37B_trade_simulation_enablement_gate_validation_stub_latest.json
│   │   ├── 37C_trade_simulation_enablement_gate_pipeline_rollup_certification_latest.json
│   │   ├── 37D_handoff_bundle_refresh_latest.json
│   │   ├── 38A_risk_gate_contract_stub_latest.json
│   │   ├── 38B_risk_gate_validation_stub_latest.json
│   │   ├── 38C_risk_gate_pipeline_rollup_certification_latest.json
│   │   ├── 38D_handoff_bundle_refresh_latest.json
│   │   ├── 39A_master_sandbox_gate_wiregraph_latest.json
│   │   ├── 39A_master_sandbox_gate_wiregraph_latest.mmd
│   │   ├── 39B_master_sandbox_gate_wiregraph_rollup_certification_latest.json
│   │   ├── 39C_handoff_bundle_refresh_latest.json
│   │   ├── 40A_sandbox_runtime_dependency_trace_stub_latest.json
│   │   ├── 40B_sandbox_runtime_dependency_trace_rollup_certification_latest.json
│   │   ├── 40C_handoff_bundle_refresh_latest.json
│   │   ├── 41A_safe_read_only_architecture_inspector_stub_latest.json
│   │   ├── 41B_safe_read_only_architecture_inspector_rollup_certification_latest.json
│   │   ├── 41C_handoff_bundle_refresh_latest.json
│   │   ├── 42A_qwen_read_only_architecture_context_stub_latest.json
│   │   ├── 42B_qwen_read_only_architecture_context_rollup_certification_latest.json
│   │   ├── 42C_handoff_bundle_refresh_latest.json
│   │   ├── 43A_qwen_context_response_contract_stub_latest.json
│   │   ├── 43B_qwen_context_response_contract_rollup_certification_latest.json
│   │   ├── 43C_handoff_bundle_refresh_latest.json
│   │   ├── 44A_qwen_read_only_response_sample_stub_latest.json
│   │   ├── 44B_qwen_read_only_response_sample_rollup_certification_latest.json
│   │   ├── 44C_handoff_bundle_refresh_latest.json
│   │   ├── 45A_qwen_read_only_architecture_summary_gate_stub_latest.json
│   │   ├── 45B_qwen_read_only_architecture_summary_gate_rollup_certification_latest.json
│   │   ├── 45C_handoff_bundle_refresh_latest.json
│   │   ├── 46A_qwen_read_only_missing_context_detector_stub_latest.json
│   │   ├── 46B_qwen_read_only_missing_context_detector_rollup_certification_latest.json
│   │   ├── 46C_handoff_bundle_refresh_latest.json
│   │   ├── 47A_qwen_read_only_recommendation_filter_stub_latest.json
│   │   ├── 47B_qwen_read_only_recommendation_filter_rollup_certification_latest.json
│   │   ├── 47C_handoff_bundle_refresh_latest.json
│   │   ├── 48A_qwen_read_only_response_validator_stub_latest.json
│   │   ├── 48B_qwen_read_only_response_validator_rollup_certification_latest.json
│   │   ├── 48C_handoff_bundle_refresh_latest.json
│   │   ├── 49A_qwen_read_only_architecture_session_contract_stub_latest.json
│   │   ├── 49B_qwen_read_only_architecture_session_contract_rollup_certification_latest.json
│   │   ├── 49C_handoff_bundle_refresh_latest.json
│   │   ├── 50A_qwen_read_only_session_response_bridge_stub_latest.json
│   │   ├── 50B_qwen_read_only_session_response_bridge_rollup_certification_latest.json
│   │   ├── 50C_handoff_bundle_refresh_latest.json
│   │   ├── 51A_qwen_read_only_architecture_loop_boundary_stub_latest.json
│   │   ├── 51B_qwen_read_only_architecture_loop_boundary_rollup_certification_latest.json
│   │   ├── 51C_handoff_bundle_refresh_latest.json
│   │   ├── 52A_qwen_read_only_final_guardrail_summary_stub_latest.json
│   │   ├── 52B_qwen_read_only_final_guardrail_summary_rollup_certification_latest.json
│   │   ├── 52C_handoff_bundle_refresh_latest.json
│   │   ├── 53A_qwen_read_only_handoff_freeze_stub_latest.json
│   │   ├── 53B_qwen_read_only_handoff_freeze_rollup_certification_latest.json
│   │   ├── 53C_handoff_bundle_refresh_latest.json
│   │   ├── 54A_qwen_read_only_handoff_export_summary_stub_latest.json
│   │   ├── 54B_qwen_read_only_handoff_export_summary_rollup_certification_latest.json
│   │   ├── 54C_handoff_bundle_refresh_latest.json
│   │   ├── 55A_qwen_read_only_architecture_state_machine_stub_latest.json
│   │   ├── 55B_qwen_read_only_architecture_state_machine_rollup_certification_latest.json
│   │   ├── 55C_handoff_bundle_refresh_latest.json
│   │   ├── 56A_qwen_read_only_architecture_policy_map_stub_latest.json
│   │   ├── 56B_qwen_read_only_architecture_policy_map_rollup_certification_latest.json
│   │   ├── 56C_handoff_bundle_refresh_latest.json
│   │   ├── 57A_qwen_read_only_policy_boundary_matrix_stub_latest.json
│   │   ├── 57B_qwen_read_only_policy_boundary_matrix_rollup_certification_latest.json
│   │   ├── 57C_handoff_bundle_refresh_latest.json
│   │   ├── 58A_qwen_read_only_final_context_package_stub_latest.json
│   │   ├── 58B_qwen_read_only_final_context_package_rollup_certification_latest.json
│   │   ├── 58C_handoff_bundle_refresh_latest.json
│   │   ├── 59A_qwen_read_only_final_handoff_certification_stub_latest.json
│   │   ├── 59B_qwen_read_only_final_handoff_certification_rollup_certification_latest.json
│   │   ├── 59C_handoff_bundle_refresh_latest.json
│   │   ├── 60A_qwen_read_only_terminal_freeze_stub_latest.json
│   │   ├── 60B_qwen_read_only_terminal_freeze_rollup_certification_latest.json
│   │   ├── 60C_handoff_bundle_refresh_latest.json
│   │   ├── 61A_archive_or_new_chat_handoff_summary_latest.json
│   │   ├── candidate_20260706_144431_8a545b3c_mock_metrics.json
│   │   ├── candidate_20260706_144431_8a545b3c_mock_scorecard.json
│   │   ├── candidate_20260706_144431_8a545b3c_sandbox_result_stub.json
│   │   ├── candidate_20260706_144431_8a545b3c_sandbox_stub.json
│   │   ├── candidate_20260706_145350_816903d1_mock_metrics.json
│   │   ├── candidate_20260706_145350_816903d1_mock_scorecard.json
│   │   ├── candidate_20260706_145350_816903d1_sandbox_result_stub.json
│   │   ├── candidate_20260706_145350_816903d1_sandbox_stub.json
│   │   ├── candidate_20260706_150540_4fc7b8ab_mock_metrics.json
│   │   ├── candidate_20260706_150540_4fc7b8ab_mock_scorecard.json
│   │   ├── candidate_20260706_150540_4fc7b8ab_sandbox_result_stub.json
│   │   ├── candidate_20260706_150540_4fc7b8ab_sandbox_stub.json
│   │   ├── candidate_20260706_151330_9f852272_mock_metrics.json
│   │   ├── candidate_20260706_151330_9f852272_mock_scorecard.json
│   │   ├── candidate_20260706_151330_9f852272_sandbox_result_stub.json
│   │   ├── candidate_20260706_151330_9f852272_sandbox_stub.json
│   │   ├── candidate_20260706_152354_e2129e4e_mock_metrics.json
│   │   ├── candidate_20260706_152354_e2129e4e_mock_scorecard.json
│   │   ├── candidate_20260706_152354_e2129e4e_sandbox_result_stub.json
│   │   ├── candidate_20260706_152354_e2129e4e_sandbox_stub.json
│   │   ├── candidate_20260706_152930_73031c40_mock_metrics.json
│   │   ├── candidate_20260706_152930_73031c40_mock_scorecard.json
│   │   ├── candidate_20260706_152930_73031c40_sandbox_result_stub.json
│   │   ├── candidate_20260706_152930_73031c40_sandbox_stub.json
│   │   ├── candidate_sandbox_execution_contract_v1.json
│   │   ├── candidate_sandbox_execution_contract_v1.txt
│   │   ├── candidate_sandbox_mock_metrics_index_latest.json
│   │   ├── candidate_sandbox_mock_metrics_index_latest.txt
│   │   ├── candidate_sandbox_mock_scorecard_latest.json
│   │   ├── candidate_sandbox_mock_scorecard_latest.txt
│   │   ├── candidate_sandbox_result_example_latest.json
│   │   ├── candidate_sandbox_result_schema_v1.json
│   │   ├── candidate_sandbox_result_stub_index_latest.json
│   │   ├── candidate_sandbox_result_stub_index_latest.txt
│   │   ├── historical_bars_contract_v1.json
│   │   ├── historical_bars_contract_v1.txt
│   │   ├── historical_replay_engine_stub_latest.json
│   │   ├── historical_replay_engine_stub_latest.txt
│   │   ├── historical_replay_input_contract_v1.json
│   │   ├── historical_replay_input_contract_v1.txt
│   │   ├── historical_replay_market_data_provider_contract_v1.json
│   │   ├── historical_replay_market_data_provider_contract_v1.txt
│   │   ├── historical_replay_provider_adapter_stub_latest.json
│   │   ├── historical_replay_provider_adapter_stub_latest.txt
│   │   ├── historical_replay_validation_stub_latest.json
│   │   ├── historical_replay_validation_stub_latest.txt
│   │   ├── sandbox_dry_run_index_latest.json
│   │   ├── sandbox_dry_run_index_latest.txt
│   │   ├── simulation_harness_stub_latest.json
│   │   ├── simulation_harness_stub_latest.txt
│   │   ├── yfinance_historical_bars_adapter_shape_validation_latest.json
│   │   ├── yfinance_historical_bars_adapter_shape_validation_latest.txt
│   │   ├── yfinance_historical_bars_adapter_stub_latest.json
│   │   ├── yfinance_historical_bars_adapter_stub_latest.txt
│   │   ├── yfinance_historical_bars_adapter_wire_latest.json
│   │   ├── yfinance_historical_bars_adapter_wire_preview_latest.json
│   │   ├── yfinance_historical_bars_adapter_wire_preview_latest.txt
│   │   ├── yfinance_historical_bars_provider_probe_latest.json
│   │   └── yfinance_historical_bars_provider_probe_latest.txt
│   └── strategy_candidates/
│       ├── candidate_20260706_144431_8a545b3c.json
│       ├── candidate_20260706_145350_816903d1.json
│       ├── candidate_20260706_150540_4fc7b8ab.json
│       ├── candidate_20260706_151330_9f852272.json
│       ├── candidate_20260706_152354_e2129e4e.json
│       ├── candidate_20260706_152930_73031c40.json
│       ├── candidate_20260706_171550_aca89979.json
│       ├── candidate_20260706_171803_7979fee4.json
│       ├── candidate_20260706_171835_2412645f.json
│       ├── candidate_20260706_190850_245c152e.json
│       ├── candidate_20260706_190919_18dff139.json
│       ├── candidate_20260706_190955_47174fc4.json
│       ├── candidate_20260706_201713_2d8f8e9e.json
│       ├── candidate_20260706_201808_d90bd687.json
│       ├── candidate_20260706_221600_b8f7600a.json
│       ├── candidate_20260706_234404_20bfeb59.json
│       ├── review_index_latest.json
│       └── review_index_latest.txt
├── scripts/
│   ├── ci/
│   │   └── architecture_ci_guard_v1.py
│   ├── apply_service_relocation_v1.py
│   ├── architecture_enforcement_v1.py
│   ├── architecture_normalization_engine_v1.py
│   ├── orphan_finalizer_v1.py
│   ├── orphan_resolution_engine_v1.py
│   ├── phase10_domain_subsystem_visualization.py
│   ├── phase10_domain_subsystem_visualization_certification.py
│   ├── phase10c_domain_runtime_overlay_visualization.py
│   ├── phase10c_runtime_flow_overlay_certification.py
│   ├── phase10c_runtime_flow_overlay_export.py
│   ├── phase10d_runtime_static_dependency_diff.py
│   ├── phase10d_runtime_static_dependency_diff_certification.py
│   ├── phase10e_classify_runtime_static_diff_edges.py
│   ├── phase10e_diff_classification_certification.py
│   ├── phase10f_architecture_drift_watch_certification.py
│   ├── phase10g_architecture_drift_dashboard_certification.py
│   ├── phase10g_architecture_drift_dashboard_summary.py
│   ├── phase10h_architecture_dashboard_command_certification.py
│   ├── phase11_live_market_price_api_bridge.py
│   ├── phase11_live_market_price_api_bridge_certification.py
│   ├── phase11b_frontend_live_price_card.py
│   ├── phase11b_frontend_live_price_card_certification.py
│   ├── phase11c_frontend_polling_api_cleanup.py
│   ├── phase11c_frontend_polling_api_cleanup_certification.py
│   ├── phase11d_next_api_proxy_live_price.py
│   ├── phase11d_next_api_proxy_live_price_certification.py
│   ├── phase11e_frontend_build_type_certification.py
│   ├── phase11f_frontend_type_lint_repair.py
│   ├── phase11f_frontend_type_lint_repair_certification.py
│   ├── phase11g_live_market_dashboard_expansion.py
│   ├── phase11g_live_market_dashboard_expansion_certification.py
│   ├── phase12_service_layer_alignment.py
│   ├── phase12e_service_chain_graph_export.py
│   ├── phase12f_service_chain_certification.py
│   ├── phase12g_add_service_chain_to_dashboard.py
│   ├── phase12g_service_chain_dashboard_certification.py
│   ├── phase12g_service_chain_repair.py
│   ├── phase13_portfolio_positions_service_chain.py
│   ├── phase13e_portfolio_service_chain_graph_export.py
│   ├── phase13f_portfolio_positions_service_chain_certification.py
│   ├── phase13g_add_portfolio_chain_to_dashboard.py
│   ├── phase13g_portfolio_chain_dashboard_certification.py
│   ├── phase14_strategy_decision_service_chain.py
│   ├── phase14e_strategy_service_chain_graph_export.py
│   ├── phase14f_strategy_decision_service_chain_certification.py
│   ├── phase14g_add_strategy_chain_to_dashboard.py
│   ├── phase14g_strategy_chain_dashboard_certification.py
│   ├── phase15_risk_gate_service_chain.py
│   ├── phase15e_risk_service_chain_graph_export.py
│   ├── phase15f_risk_gate_service_chain_certification.py
│   ├── phase15g_add_risk_chain_to_dashboard.py
│   ├── phase15g_risk_chain_dashboard_certification.py
│   ├── phase16_api_route_separation_certification.py
│   ├── phase17_dashboard_route_map_certification.py
│   ├── phase17_dashboard_route_map_frontend_card_verification.py
│   ├── phase18_real_positions_panel_certification.py
│   ├── phase18_real_positions_panel_component.py
│   ├── phase19_dashboard_visual_layout_certification.py
│   ├── phase19_dashboard_visual_layout_hardening.py
│   ├── phase19b_endpoint_activation_probe_repair.py
│   ├── phase19c_endpoint_activation_certification.py
│   ├── phase1_repo_research_market_bootstrap.py
│   ├── phase20_floating_chat_widget_service_chain.py
│   ├── phase20e_chat_service_chain_graph_export.py
│   ├── phase20f_floating_chat_widget_certification.py
│   ├── phase21_fix_chat_service_generator.py
│   ├── phase21ab_chat_cache_history.py
│   ├── phase21ab_chat_cache_history_certification.py
│   ├── phase21cd_chat_ux_persistent_cache.py
│   ├── phase21cd_chat_ux_persistent_cache_certification.py
│   ├── phase22_live_graph_tab.py
│   ├── phase22_live_graph_tab_certification.py
│   ├── phase22b_live_graph_visualization.py
│   ├── phase22b_live_graph_visualization_certification.py
│   ├── phase23a_frontend_request_normalizer.py
│   ├── phase23a_frontend_request_normalizer_certification.py
│   ├── phase23b_polling_governor_certification.py
│   ├── phase24a_frontend_observability_dashboard.py
│   ├── phase24a_frontend_observability_dashboard_certification.py
│   ├── phase24b_persist_observability_backend_health.py
│   ├── phase24b_persist_observability_backend_health_certification.py
│   ├── phase24c_observability_event_timeline.py
│   ├── phase24c_observability_event_timeline_certification.py
│   ├── phase24d_observability_lock_handoff_snapshot.py
│   ├── phase25a_dashboard_tab_shell_layout_navigation.py
│   ├── phase25a_dashboard_tab_shell_layout_navigation_certification.py
│   ├── phase25b_tab_layout_polish_chat_panel.py
│   ├── phase25b_tab_layout_polish_chat_panel_certification.py
│   ├── phase25c_split_dashboard_panels_into_tab_workspaces.py
│   ├── phase25c_split_dashboard_panels_into_tab_workspaces_certification.py
│   ├── phase26a_chat_intent_regex_ollama_router.py
│   ├── phase26b_wire_ollama_into_chat_runtime.py
│   ├── phase26c_chat_safety_prompt_live_execution_guard_certification.py
│   ├── phase26d_frontend_chat_response_normalizer.py
│   ├── phase26d_frontend_chat_response_normalizer_certification.py
│   ├── phase26e_chat_metadata_chips_typing_enter.py
│   ├── phase26e_chat_metadata_chips_typing_enter_certification.py
│   ├── phase26f_chat_ui_state_cleanup_metadata_rendering.py
│   ├── phase26f_chat_ui_state_cleanup_metadata_rendering_certification.py
│   ├── phase27a_strategy_proposal_capture.py
│   ├── phase27a_strategy_proposal_capture_certification.py
│   ├── phase27b_strategy_candidate_review_index.py
│   ├── phase27b_strategy_candidate_review_index_certification.py
│   ├── phase27c_candidate_sandbox_dry_run_stub.py
│   ├── phase27c_candidate_sandbox_dry_run_stub_certification.py
│   ├── phase27d_candidate_sandbox_result_schema.py
│   ├── phase27d_candidate_sandbox_result_schema_certification.py
│   ├── phase27e_candidate_sandbox_result_stub_generator.py
│   ├── phase27e_candidate_sandbox_result_stub_generator_certification.py
│   ├── phase27f_candidate_sandbox_readiness_lock_snapshot.py
│   ├── phase28a_candidate_sandbox_simulation_harness_stub.py
│   ├── phase28a_candidate_sandbox_simulation_harness_stub_certification.py
│   ├── phase28b_candidate_sandbox_mock_metrics_generator.py
│   ├── phase28b_candidate_sandbox_mock_metrics_generator_certification.py
│   ├── phase28c_candidate_sandbox_mock_scorecard.py
│   ├── phase28c_candidate_sandbox_mock_scorecard_certification.py
│   ├── phase28d_candidate_sandbox_execution_contract.py
│   ├── phase28d_candidate_sandbox_execution_contract_certification.py
│   ├── phase29a_historical_replay_engine_stub.py
│   ├── phase29a_historical_replay_engine_stub_certification.py
│   ├── phase29b_historical_replay_input_contract.py
│   ├── phase29b_historical_replay_input_contract_certification.py
│   ├── phase29c_historical_replay_validation_stub.py
│   ├── phase29c_historical_replay_validation_stub_certification.py
│   ├── phase29d_historical_replay_readiness_snapshot.py
│   ├── phase29e_historical_replay_market_data_provider_contract.py
│   ├── phase29e_historical_replay_market_data_provider_contract_certification.py
│   ├── phase29f_historical_replay_provider_adapter_stub.py
│   ├── phase29f_historical_replay_provider_adapter_stub_certification.py
│   ├── phase29g_historical_replay_provider_readiness_snapshot.py
│   ├── phase2_yfinance_market_warehouse.py
│   ├── phase30a_yfinance_historical_bars_provider_probe.py
│   ├── phase30a_yfinance_historical_bars_provider_probe_certification.py
│   ├── phase30b_yfinance_provider_selection_snapshot.py
│   ├── phase30c_historical_bars_contract.py
│   ├── phase30c_historical_bars_contract_certification.py
│   ├── phase30d_yfinance_historical_bars_adapter_stub.py
│   ├── phase30d_yfinance_historical_bars_adapter_stub_certification.py
│   ├── phase30e_yfinance_historical_bars_adapter_shape_validation.py
│   ├── phase30e_yfinance_historical_bars_adapter_shape_validation_certification.py
│   ├── phase30f_yfinance_historical_bars_adapter_wire_preview.py
│   ├── phase30f_yfinance_historical_bars_adapter_wire_preview_certification.py
│   ├── phase30g_yfinance_historical_bars_adapter_wire.py
│   ├── phase30g_yfinance_historical_bars_adapter_wire_certification.py
│   ├── phase31a_historical_bars_fetch_validation.py
│   ├── phase31b_historical_bars_multi_symbol_validation.py
│   ├── phase31c_historical_replay_executor_stub.py
│   ├── phase31d_historical_replay_bar_iterator.py
│   ├── phase31e_first_single_candidate_replay_dry_run.py
│   ├── phase31f_replay_metrics_contract.py
│   ├── phase32a_real_metrics_generation.py
│   ├── phase32b_candidate_scorecard_from_replay_metrics.py
│   ├── phase32c_manual_promotion_gate_stub.py
│   ├── phase32d_pipeline_rollup_certification.py
│   ├── phase32e_handoff_bundle_refresh.py
│   ├── phase33a_trade_simulation_contract_stub.py
│   ├── phase33b_trade_event_validation_stub.py
│   ├── phase33c_trade_simulation_dry_run_stub.py
│   ├── phase33d_entry_exit_signal_contract_stub.py
│   ├── phase33e_hold_signal_generator_stub.py
│   ├── phase33f_entry_exit_decision_engine_stub.py
│   ├── phase33g_hold_decision_to_hold_event_bridge.py
│   ├── phase33h_trade_simulation_pipeline_rollup_certification.py
│   ├── phase33i_handoff_bundle_refresh.py
│   ├── phase34a_entry_signal_rule_contract_stub.py
│   ├── phase34b_entry_signal_rule_validation_stub.py
│   ├── phase34c_entry_signal_generator_disabled_stub.py
│   ├── phase34d_entry_signal_pipeline_rollup_certification.py
│   ├── phase34e_handoff_bundle_refresh.py
│   ├── phase35a_exit_signal_rule_contract_stub.py
│   ├── phase35b_exit_signal_rule_validation_stub.py
│   ├── phase35c_exit_signal_generator_disabled_stub.py
│   ├── phase35d_exit_signal_pipeline_rollup_certification.py
│   ├── phase35e_strategy_sandbox_wiregraph_certification.py
│   ├── phase35f_handoff_bundle_refresh.py
│   ├── phase36a_strategy_rule_enablement_gate_contract_stub.py
│   ├── phase36b_enablement_gate_validation_stub.py
│   ├── phase36c_enablement_gate_pipeline_rollup_certification.py
│   ├── phase36d_handoff_bundle_refresh.py
│   ├── phase37a_trade_simulation_enablement_gate_contract_stub.py
│   ├── phase37b_trade_simulation_enablement_gate_validation_stub.py
│   ├── phase37c_trade_simulation_enablement_gate_pipeline_rollup_certification.py
│   ├── phase37d_handoff_bundle_refresh.py
│   ├── phase38a_risk_gate_contract_stub.py
│   ├── phase38b_risk_gate_validation_stub.py
│   ├── phase38c_risk_gate_pipeline_rollup_certification.py
│   ├── phase38d_handoff_bundle_refresh.py
│   ├── phase39a_master_sandbox_gate_wiregraph_refresh.py
│   ├── phase39b_master_sandbox_gate_wiregraph_rollup_certification.py
│   ├── phase39c_handoff_bundle_refresh.py
│   ├── phase3m_graph_certification.py
│   ├── phase40a_sandbox_runtime_dependency_trace_stub.py
│   ├── phase40b_sandbox_runtime_dependency_trace_rollup_certification.py
│   ├── phase40c_handoff_bundle_refresh.py
│   ├── phase41a_safe_read_only_architecture_inspector_stub.py
│   ├── phase41b_safe_read_only_architecture_inspector_rollup_certification.py
│   ├── phase41c_handoff_bundle_refresh.py
│   ├── phase42a_qwen_read_only_architecture_context_stub.py
│   ├── phase42b_qwen_read_only_architecture_context_rollup_certification.py
│   ├── phase42c_handoff_bundle_refresh.py
│   ├── phase43a_qwen_context_response_contract_stub.py
│   ├── phase43b_qwen_context_response_contract_rollup_certification.py
│   ├── phase43c_handoff_bundle_refresh.py
│   ├── phase44a_qwen_read_only_response_sample_stub.py
│   ├── phase44b_qwen_read_only_response_sample_rollup_certification.py
│   ├── phase44c_handoff_bundle_refresh.py
│   ├── phase45a_qwen_read_only_architecture_summary_gate_stub.py
│   ├── phase45b_qwen_read_only_architecture_summary_gate_rollup_certification.py
│   ├── phase45c_handoff_bundle_refresh.py
│   ├── phase46a_qwen_read_only_missing_context_detector_stub.py
│   ├── phase46b_qwen_read_only_missing_context_detector_rollup_certification.py
│   ├── phase46c_handoff_bundle_refresh.py
│   ├── phase47a_qwen_read_only_recommendation_filter_stub.py
│   ├── phase47b_qwen_read_only_recommendation_filter_rollup_certification.py
│   ├── phase47c_handoff_bundle_refresh.py
│   ├── phase48a_qwen_read_only_response_validator_stub.py
│   ├── phase48b_qwen_read_only_response_validator_rollup_certification.py
│   ├── phase48c_handoff_bundle_refresh.py
│   ├── phase49a_qwen_read_only_architecture_session_contract_stub.py
│   ├── phase49b_qwen_read_only_architecture_session_contract_rollup_certification.py
│   ├── phase49c_handoff_bundle_refresh.py
│   ├── phase4_repo_memory_indexer_v2.py
│   ├── phase4c_loose_root_duplicate_quarantine_plan.py
│   ├── phase4d_root_shadow_diff_report.py
│   ├── phase4e_quarantine_root_shadows.py
│   ├── phase4g_repo_memory_certification.py
│   ├── phase50a_qwen_read_only_session_response_bridge_stub.py
│   ├── phase50b_qwen_read_only_session_response_bridge_rollup_certification.py
│   ├── phase50c_handoff_bundle_refresh.py
│   ├── phase51a_qwen_read_only_architecture_loop_boundary_stub.py
│   ├── phase51b_qwen_read_only_architecture_loop_boundary_rollup_certification.py
│   ├── phase51c_handoff_bundle_refresh.py
│   ├── phase52a_qwen_read_only_final_guardrail_summary_stub.py
│   ├── phase52b_qwen_read_only_final_guardrail_summary_rollup_certification.py
│   ├── phase52c_handoff_bundle_refresh.py
│   ├── phase53a_qwen_read_only_handoff_freeze_stub.py
│   ├── phase53b_qwen_read_only_handoff_freeze_rollup_certification.py
│   ├── phase53c_handoff_bundle_refresh.py
│   ├── phase54a_qwen_read_only_handoff_export_summary_stub.py
│   ├── phase54b_qwen_read_only_handoff_export_summary_rollup_certification.py
│   ├── phase54c_handoff_bundle_refresh.py
│   ├── phase55a_qwen_read_only_architecture_state_machine_stub.py
│   ├── phase55b_qwen_read_only_architecture_state_machine_rollup_certification.py
│   ├── phase55c_handoff_bundle_refresh.py
│   ├── phase56a_qwen_read_only_architecture_policy_map_stub.py
│   ├── phase56b_qwen_read_only_architecture_policy_map_rollup_certification.py
│   ├── phase56c_handoff_bundle_refresh.py
│   ├── phase57a_qwen_read_only_policy_boundary_matrix_stub.py
│   ├── phase57b_qwen_read_only_policy_boundary_matrix_rollup_certification.py
│   ├── phase57c_handoff_bundle_refresh.py
│   ├── phase58a_qwen_read_only_final_context_package_stub.py
│   ├── phase58b_qwen_read_only_final_context_package_rollup_certification.py
│   ├── phase58c_handoff_bundle_refresh.py
│   ├── phase59a_qwen_read_only_final_handoff_certification_stub.py
│   ├── phase59b_qwen_read_only_final_handoff_certification_rollup_certification.py
│   ├── phase59c_handoff_bundle_refresh.py
│   ├── phase5c_repo_memory_certification_v2.py
│   ├── phase60a_qwen_read_only_terminal_freeze_stub.py
│   ├── phase60b_qwen_read_only_terminal_freeze_rollup_certification.py
│   ├── phase60c_handoff_bundle_refresh.py
│   ├── phase61a_archive_or_new_chat_handoff_summary.py
│   ├── phase62a_master_architecture_handoff_controller.py
│   ├── phase6b_dependency_validation_certification.py
│   ├── phase6c_dependency_graph_export.py
│   ├── phase6d_dependency_graph_certification.py
│   ├── phase7a_dependency_topology_overlay_export.py
│   ├── phase7g_graph_visualization_certification.py
│   ├── phase8c_neuro_cli_hotspots_certification.py
│   ├── phase9a_canonical_layer_graph_export.py
│   ├── phase9b_component_overlay_export.py
│   ├── phase9c_generate_layer_colored_wire_graph.py
│   ├── phase9e_canonical_graph_certification.py
│   ├── phase9k_domain_subsystem_graph_export.py
│   ├── phase9l_stack_layer_sankey_export.py
│   ├── phase9m_canonical_graph_certification_v2.py
│   ├── reconcile_repo_state_v1.py
│   ├── service_stack_relocator_v1.py
│   └── topology_state_lock_v1.py
├── $OUTPUT
├── .aider.chat.history.md
├── .aider.input.history
├── .env
├── .env.example
├── .gitignore
├── ARCH_ENFORCEMENT_REPORT.json
├── ARCH_GOVERNANCE.md
├── ARCHITECTURE_REPAIR_PLAN.json
├── cursor.AppImage
├── Directory Structure
├── docker-compose.yml
├── domain_runtime_overlay_graph.png
├── domain_subsystem_graph.png
├── FINAL_ARCHITECTURE_STATE.json
├── fix_phase9_self_fingerprint.sh
├── generate_wire_graph.py
├── neuro
├── neuro_cli.py
├── neuro_cli_file_inspection.json
├── neuro_engineer.py
├── neuro_health.sh
├── neurovest_repo_context.md
├── ORPHAN_RESOLUTION_PLAN.json
├── OUTPUT
├── pytest.ini
├── SERVICE_RELOCATION_PLAN.json
├── SERVICE_RELOCATION_PLAN_RECONCILED.json
├── spine_mvp_full.sh
├── system_tree.txt
├── TOPOLOGY_NORMALIZED_STATE.json
├── TOPOLOGY_STATE.json
├── topology_wire_graph.png
└── topology_wire_graph_canonical.png

```


# Backend Tree

```text
backend/
├── app/
│   ├── analysis/
│   │   └── architecture.py
│   ├── api/
│   │   └── graph_ws.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── cognitive_event_bus.py
│   │   ├── cognitive_graph_state.py
│   │   ├── cognitive_nodes.py
│   │   ├── cognitive_types.py
│   │   ├── config.py
│   │   ├── global_firewall_v1.py
│   │   └── runtime_firewall_v1.py
│   ├── models/
│   ├── routers/
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── dashboard.py
│   ├── services/
│   │   └── __init__.py
│   ├── snaptrade/
│   │   └── executions/
│   │       ├── config.py
│   │       └── execution_layer.py
│   ├── stacks/
│   │   ├── auth_identity/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── gate.py
│   │   │   └── validator.py
│   │   ├── chat_public/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── chat_api.py
│   │   │   ├── chat_intent_regex.py
│   │   │   ├── chat_memory.py
│   │   │   ├── chat_runtime.py
│   │   │   ├── chat_service.py
│   │   │   ├── chat_system_prompt.py
│   │   │   ├── context_loader.py
│   │   │   ├── conversation_store.py
│   │   │   ├── ollama_chat_client.py
│   │   │   ├── strategy_proposal_capture.py
│   │   │   └── time_context.py
│   │   ├── db_model/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   └── market_schema.py
│   │   ├── events/
│   │   │   └── broker.py
│   │   ├── execution/
│   │   │   ├── __init__.py
│   │   │   ├── accounting_engine.py
│   │   │   ├── base.py
│   │   │   ├── broker.py
│   │   │   ├── commission_engine.py
│   │   │   ├── executor.py
│   │   │   ├── fill_engine.py
│   │   │   ├── paper_broker.py
│   │   │   ├── pnl_engine.py
│   │   │   ├── regime_modes.py
│   │   │   ├── regime_simulator.py
│   │   │   ├── sandbox.py
│   │   │   ├── sandbox_runtime.py
│   │   │   └── trade_ledger.py
│   │   ├── journal_ledger/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── ledger.py
│   │   │   └── record.py
│   │   ├── learning_research/
│   │   │   ├── dataset/
│   │   │   │   ├── finance/
│   │   │   │   └── papers/
│   │   │   ├── __init__.py
│   │   │   ├── backtest_engine.py
│   │   │   ├── base.py
│   │   │   ├── monte_carlo.py
│   │   │   ├── monte_carlo_mix.py
│   │   │   ├── probability_engine.py
│   │   │   ├── research_loader.py
│   │   │   ├── research_runtime.py
│   │   │   └── strategy_evaluator.py
│   │   ├── market_data/
│   │   │   ├── __init__.py
│   │   │   ├── bars.py
│   │   │   ├── base.py
│   │   │   ├── feed.py
│   │   │   ├── market_data_service.py
│   │   │   ├── market_session.py
│   │   │   ├── price.py
│   │   │   ├── provider_cache.py
│   │   │   ├── provider_registry.py
│   │   │   ├── provider_router.py
│   │   │   ├── yfinance_historical_bars_adapter.py
│   │   │   └── yfinance_ingestor.py
│   │   ├── notification/
│   │   │   ├── __init__.py
│   │   │   └── base.py
│   │   ├── portfolio/
│   │   │   ├── __init__.py
│   │   │   ├── accounting.py
│   │   │   ├── allocator.py
│   │   │   ├── base.py
│   │   │   ├── dashboard_service.py
│   │   │   ├── portfolio_runtime.py
│   │   │   ├── portfolio_service.py
│   │   │   ├── rebalance.py
│   │   │   └── reconciliation.py
│   │   ├── risk/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── drawdown_guard.py
│   │   │   ├── exposure.py
│   │   │   ├── kill_switch.py
│   │   │   ├── limits.py
│   │   │   ├── loss_streak_guard.py
│   │   │   ├── risk_runtime_service.py
│   │   │   └── risk_service.py
│   │   ├── snaptrade/
│   │   │   ├── __init__.py
│   │   │   ├── adapter.py
│   │   │   ├── base.py
│   │   │   ├── broker.py
│   │   │   └── execution.py
│   │   ├── strategy/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── candidate_registry.py
│   │   │   ├── engine.py
│   │   │   ├── evolution_engine.py
│   │   │   ├── llm_strategy_engine.py
│   │   │   ├── selector.py
│   │   │   ├── signal.py
│   │   │   ├── strategy_registry.py
│   │   │   ├── strategy_runtime.py
│   │   │   └── strategy_service.py
│   │   ├── strategy_candidate_sandbox/
│   │   │   ├── candidate_scorecard_from_replay_metrics.py
│   │   │   ├── entry_exit_decision_engine_stub.py
│   │   │   ├── entry_exit_signal_contract.py
│   │   │   ├── entry_signal_generator_disabled_stub.py
│   │   │   ├── entry_signal_rule_contract.py
│   │   │   ├── entry_signal_rule_validator.py
│   │   │   ├── exit_signal_generator_disabled_stub.py
│   │   │   ├── exit_signal_rule_contract.py
│   │   │   ├── exit_signal_rule_validator.py
│   │   │   ├── historical_replay_bar_iterator.py
│   │   │   ├── historical_replay_executor.py
│   │   │   ├── hold_decision_to_hold_event_bridge.py
│   │   │   ├── hold_signal_generator_stub.py
│   │   │   ├── manual_promotion_gate.py
│   │   │   ├── qwen_context_response_contract.py
│   │   │   ├── qwen_read_only_architecture_context.py
│   │   │   ├── qwen_read_only_architecture_summary_gate.py
│   │   │   ├── replay_metrics_contract.py
│   │   │   ├── replay_metrics_generator.py
│   │   │   ├── risk_gate_contract.py
│   │   │   ├── risk_gate_validator.py
│   │   │   ├── safe_read_only_architecture_inspector.py
│   │   │   ├── strategy_rule_enablement_gate_contract.py
│   │   │   ├── strategy_rule_enablement_gate_validator.py
│   │   │   ├── trade_event_validator.py
│   │   │   ├── trade_simulation_contract.py
│   │   │   ├── trade_simulation_dry_run_stub.py
│   │   │   ├── trade_simulation_enablement_gate_contract.py
│   │   │   └── trade_simulation_enablement_gate_validator.py
│   │   ├── wolfden_ai/
│   │   │   ├── repo_memory/
│   │   │   │   └── index/
│   │   │   ├── __init__.py
│   │   │   ├── agent_router.py
│   │   │   ├── base.py
│   │   │   ├── memory.py
│   │   │   ├── orchestrator.py
│   │   │   ├── routing.py
│   │   │   └── runtime.py
│   │   ├── __init__.py
│   │   └── registry.json
│   ├── test/
│   │   ├── test_neuro_repo_companion.py
│   │   └── test_trading_pipeline.py
│   ├── __init__.py
│   └── main.py
├── scripts/
│   └── backup_db.sh
├── __init__.py
└── requirements.txt

```


# Frontend Tree

```text
frontend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── chat/
│   │       │   └── route.ts
│   │       ├── graph/
│   │       │   └── live/
│   │       │       └── route.ts
│   │       ├── market/
│   │       │   └── live-price/
│   │       │       └── [symbol]/
│   │       │           └── route.ts
│   │       ├── portfolio/
│   │       │   └── positions/
│   │       │       └── route.ts
│   │       ├── risk/
│   │       │   └── gate/
│   │       │       └── [symbol]/
│   │       │           └── route.ts
│   │       └── strategy/
│   │           └── decision/
│   │               └── [symbol]/
│   │                   └── route.ts
│   ├── favicon.ico
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx
├── public/
│   ├── file.svg
│   ├── globe.svg
│   ├── next.svg
│   ├── vercel.svg
│   └── window.svg
├── services/
│   ├── backendHealthService.ts
│   ├── chatService.ts
│   ├── graphService.ts
│   ├── marketService.ts
│   ├── observabilityTimelineService.ts
│   ├── portfolioService.ts
│   ├── requestNormalizer.ts
│   ├── requestObservability.ts
│   ├── riskService.ts
│   └── strategyService.ts
├── .gitignore
├── AGENTS.md
├── CLAUDE.md
├── eslint.config.mjs
├── next-env.d.ts
├── next.config.ts
├── package-lock.json
├── package.json
├── postcss.config.mjs
├── README.md
└── tsconfig.json

```


# Runtime Tree

```text
runtime/
├── certifications/
│   ├── phase10_domain_subsystem_visualization_certification_latest.json
│   ├── phase10c_runtime_flow_overlay_certification_latest.json
│   ├── phase10d_runtime_static_dependency_diff_certification_latest.json
│   ├── phase10e_diff_classification_certification_latest.json
│   ├── phase10f_architecture_drift_watch_certification_latest.json
│   ├── phase10g_architecture_drift_dashboard_certification_latest.json
│   ├── phase10h_architecture_dashboard_command_certification_latest.json
│   ├── phase11_live_market_price_api_bridge_certification_latest.json
│   ├── phase11b_frontend_live_price_card_certification_latest.json
│   ├── phase11c_frontend_polling_api_cleanup_certification_latest.json
│   ├── phase11d_next_api_proxy_live_price_certification_latest.json
│   ├── phase11e_frontend_build_type_certification_latest.json
│   ├── phase11f_frontend_type_lint_repair_certification_latest.json
│   ├── phase11g_live_market_dashboard_expansion_certification_latest.json
│   ├── phase12f_service_chain_certification_latest.json
│   ├── phase12g_service_chain_dashboard_certification_latest.json
│   ├── phase13f_portfolio_positions_service_chain_certification_latest.json
│   ├── phase13g_portfolio_chain_dashboard_certification_latest.json
│   ├── phase14f_strategy_decision_service_chain_certification_latest.json
│   ├── phase14g_strategy_chain_dashboard_certification_latest.json
│   ├── phase15f_risk_gate_service_chain_certification_latest.json
│   ├── phase15g_risk_chain_dashboard_certification_latest.json
│   ├── phase16_api_route_separation_certification_latest.json
│   ├── phase17_dashboard_route_map_certification_latest.json
│   ├── phase18_real_positions_panel_certification_latest.json
│   ├── phase19_dashboard_visual_layout_certification_latest.json
│   ├── phase19c_endpoint_activation_certification_latest.json
│   ├── phase20f_floating_chat_widget_certification_latest.json
│   ├── phase21ab_chat_cache_history_certification_latest.json
│   ├── phase21cd_chat_ux_persistent_cache_certification_latest.json
│   ├── phase22_live_graph_tab_certification_latest.json
│   ├── phase22b_live_graph_visualization_certification_latest.json
│   ├── phase23a_frontend_request_normalizer_certification_latest.json
│   ├── phase23b_polling_governor_certification_latest.json
│   ├── phase24a_frontend_observability_dashboard_certification_latest.json
│   ├── phase24b_persist_observability_backend_health_certification_latest.json
│   ├── phase24c_observability_event_timeline_certification_latest.json
│   ├── phase24d_observability_lock_handoff_snapshot_latest.json
│   ├── phase25a_dashboard_tab_shell_layout_navigation_certification_latest.json
│   ├── phase25b_tab_layout_polish_chat_panel_certification_latest.json
│   ├── phase25c_split_dashboard_panels_into_tab_workspaces_certification_latest.json
│   ├── phase26c_chat_safety_prompt_live_execution_guard_certification_latest.json
│   ├── phase26d_frontend_chat_response_normalizer_certification_latest.json
│   ├── phase26e_chat_metadata_chips_typing_enter_certification_latest.json
│   ├── phase26f_chat_ui_state_cleanup_metadata_rendering_certification_latest.json
│   ├── phase27a_strategy_proposal_capture_certification_latest.json
│   ├── phase27b_strategy_candidate_review_index_certification_latest.json
│   ├── phase27c_candidate_sandbox_dry_run_stub_certification_latest.json
│   ├── phase27d_candidate_sandbox_result_schema_certification_latest.json
│   ├── phase27e_candidate_sandbox_result_stub_generator_certification_latest.json
│   ├── phase27f_candidate_sandbox_readiness_lock_snapshot_latest.json
│   ├── phase28a_candidate_sandbox_simulation_harness_stub_certification_latest.json
│   ├── phase28b_candidate_sandbox_mock_metrics_generator_certification_latest.json
│   ├── phase28c_candidate_sandbox_mock_scorecard_certification_latest.json
│   ├── phase28d_candidate_sandbox_execution_contract_certification_latest.json
│   ├── phase29a_historical_replay_engine_stub_certification_latest.json
│   ├── phase29b_historical_replay_input_contract_certification_latest.json
│   ├── phase29c_historical_replay_validation_stub_certification_latest.json
│   ├── phase29d_historical_replay_readiness_snapshot_latest.json
│   ├── phase29e_historical_replay_market_data_provider_contract_certification_latest.json
│   ├── phase29f_historical_replay_provider_adapter_stub_certification_latest.json
│   ├── phase29g_historical_replay_provider_readiness_snapshot_latest.json
│   ├── phase30a_yfinance_historical_bars_provider_probe_certification_latest.json
│   ├── phase30b_yfinance_provider_selection_snapshot_latest.json
│   ├── phase30c_historical_bars_contract_certification_latest.json
│   ├── phase30d_yfinance_historical_bars_adapter_stub_certification_latest.json
│   ├── phase30e_yfinance_historical_bars_adapter_shape_validation_certification_latest.json
│   ├── phase30f_yfinance_historical_bars_adapter_wire_preview_certification_latest.json
│   ├── phase30g_yfinance_historical_bars_adapter_wire_certification_latest.json
│   ├── phase3m_graph_certification_latest.json
│   ├── phase4g_repo_memory_certification_latest.json
│   ├── phase5c_repo_memory_certification_v2_latest.json
│   ├── phase6b_dependency_validation_certification_latest.json
│   ├── phase6d_dependency_graph_certification_latest.json
│   ├── phase7g_graph_visualization_certification_latest.json
│   ├── phase8c_neuro_cli_hotspots_certification_latest.json
│   ├── phase9e_canonical_graph_certification_latest.json
│   └── phase9m_canonical_graph_certification_v2_latest.json
├── graph_history/
│   ├── current_snapshot.json
│   └── events.jsonl
├── handoff_snapshot/
│   ├── file_manifest_latest.txt
│   ├── live_graph_validate_latest.json
│   ├── neurovest_training_handoff_bundle_latest.json
│   ├── simulate_trade_guard_latest.json
│   └── topology_tree_latest.txt
├── market_warehouse/
│   ├── history/
│   │   ├── AAPL_history.csv
│   │   ├── MSFT_history.csv
│   │   ├── NVDA_history.csv
│   │   ├── RY_TO_history.csv
│   │   ├── TD_TO_history.csv
│   │   ├── TSLA_history.csv
│   │   ├── VFV_TO_history.csv
│   │   └── VUN_TO_history.csv
│   ├── live/
│   │   ├── AAPL_live.json
│   │   ├── MSFT_live.json
│   │   ├── NVDA_live.json
│   │   ├── RY_TO_live.json
│   │   ├── TD_TO_live.json
│   │   ├── TSLA_live.json
│   │   ├── VFV_TO_live.json
│   │   └── VUN_TO_live.json
│   └── symbol_registry.json
├── repo_memory/
│   ├── architecture_drift_dashboard_v1.json
│   ├── architecture_drift_dashboard_v1.txt
│   ├── canonical_layer_graph_v1.json
│   ├── chat_service_chain_graph_v1.json
│   ├── component_overlay_v1.json
│   ├── dashboard_route_map_v1.json
│   ├── dependency_graph_v1.json
│   ├── dependency_topology_overlay_v1.json
│   ├── domain_subsystem_graph_v1.json
│   ├── phase4c_loose_root_duplicate_quarantine_plan_latest.json
│   ├── phase4d_root_shadow_diff_report_latest.json
│   ├── phase4d_root_shadow_diff_report_latest.txt
│   ├── phase4e_quarantine_root_shadows_latest.json
│   ├── portfolio_service_chain_graph_v1.json
│   ├── repo_index.json
│   ├── repo_index_v2.json
│   ├── risk_service_chain_graph_v1.json
│   ├── runtime_flow_overlay_v1.json
│   ├── runtime_static_dependency_diff_v1.json
│   ├── runtime_static_diff_classification_v1.json
│   ├── service_chain_graph_v1.json
│   ├── stack_layer_sankey_v1.json
│   └── strategy_service_chain_graph_v1.json
├── research_db/
│   └── research_seed.json
├── strategy_candidate_sandbox/
│   ├── 31A_historical_bars_fetch_validation_latest.json
│   ├── 31B_historical_bars_multi_symbol_validation_latest.json
│   ├── 31C_historical_replay_executor_stub_latest.json
│   ├── 31D_historical_replay_bar_iterator_latest.json
│   ├── 31E_first_single_candidate_replay_dry_run_latest.json
│   ├── 31F_replay_metrics_contract_latest.json
│   ├── 32A_real_metrics_generation_latest.json
│   ├── 32B_candidate_scorecard_from_replay_metrics_latest.json
│   ├── 32C_manual_promotion_gate_stub_latest.json
│   ├── 32D_pipeline_rollup_certification_latest.json
│   ├── 32E_handoff_bundle_refresh_latest.json
│   ├── 33A_trade_simulation_contract_stub_latest.json
│   ├── 33B_trade_event_validation_stub_latest.json
│   ├── 33C_trade_simulation_dry_run_stub_latest.json
│   ├── 33D_entry_exit_signal_contract_stub_latest.json
│   ├── 33E_hold_signal_generator_stub_latest.json
│   ├── 33F_entry_exit_decision_engine_stub_latest.json
│   ├── 33G_hold_decision_to_hold_event_bridge_latest.json
│   ├── 33H_trade_simulation_pipeline_rollup_certification_latest.json
│   ├── 33I_handoff_bundle_refresh_latest.json
│   ├── 34A_entry_signal_rule_contract_stub_latest.json
│   ├── 34B_entry_signal_rule_validation_stub_latest.json
│   ├── 34C_entry_signal_generator_disabled_stub_latest.json
│   ├── 34D_entry_signal_pipeline_rollup_certification_latest.json
│   ├── 34E_handoff_bundle_refresh_latest.json
│   ├── 35A_exit_signal_rule_contract_stub_latest.json
│   ├── 35B_exit_signal_rule_validation_stub_latest.json
│   ├── 35C_exit_signal_generator_disabled_stub_latest.json
│   ├── 35D_exit_signal_pipeline_rollup_certification_latest.json
│   ├── 35E_strategy_sandbox_wiregraph_latest.json
│   ├── 35E_strategy_sandbox_wiregraph_latest.mmd
│   ├── 35F_handoff_bundle_refresh_latest.json
│   ├── 36A_strategy_rule_enablement_gate_contract_stub_latest.json
│   ├── 36B_enablement_gate_validation_stub_latest.json
│   ├── 36C_enablement_gate_pipeline_rollup_certification_latest.json
│   ├── 36D_handoff_bundle_refresh_latest.json
│   ├── 37A_trade_simulation_enablement_gate_contract_stub_latest.json
│   ├── 37B_trade_simulation_enablement_gate_validation_stub_latest.json
│   ├── 37C_trade_simulation_enablement_gate_pipeline_rollup_certification_latest.json
│   ├── 37D_handoff_bundle_refresh_latest.json
│   ├── 38A_risk_gate_contract_stub_latest.json
│   ├── 38B_risk_gate_validation_stub_latest.json
│   ├── 38C_risk_gate_pipeline_rollup_certification_latest.json
│   ├── 38D_handoff_bundle_refresh_latest.json
│   ├── 39A_master_sandbox_gate_wiregraph_latest.json
│   ├── 39A_master_sandbox_gate_wiregraph_latest.mmd
│   ├── 39B_master_sandbox_gate_wiregraph_rollup_certification_latest.json
│   ├── 39C_handoff_bundle_refresh_latest.json
│   ├── 40A_sandbox_runtime_dependency_trace_stub_latest.json
│   ├── 40B_sandbox_runtime_dependency_trace_rollup_certification_latest.json
│   ├── 40C_handoff_bundle_refresh_latest.json
│   ├── 41A_safe_read_only_architecture_inspector_stub_latest.json
│   ├── 41B_safe_read_only_architecture_inspector_rollup_certification_latest.json
│   ├── 41C_handoff_bundle_refresh_latest.json
│   ├── 42A_qwen_read_only_architecture_context_stub_latest.json
│   ├── 42B_qwen_read_only_architecture_context_rollup_certification_latest.json
│   ├── 42C_handoff_bundle_refresh_latest.json
│   ├── 43A_qwen_context_response_contract_stub_latest.json
│   ├── 43B_qwen_context_response_contract_rollup_certification_latest.json
│   ├── 43C_handoff_bundle_refresh_latest.json
│   ├── 44A_qwen_read_only_response_sample_stub_latest.json
│   ├── 44B_qwen_read_only_response_sample_rollup_certification_latest.json
│   ├── 44C_handoff_bundle_refresh_latest.json
│   ├── 45A_qwen_read_only_architecture_summary_gate_stub_latest.json
│   ├── 45B_qwen_read_only_architecture_summary_gate_rollup_certification_latest.json
│   ├── 45C_handoff_bundle_refresh_latest.json
│   ├── 46A_qwen_read_only_missing_context_detector_stub_latest.json
│   ├── 46B_qwen_read_only_missing_context_detector_rollup_certification_latest.json
│   ├── 46C_handoff_bundle_refresh_latest.json
│   ├── 47A_qwen_read_only_recommendation_filter_stub_latest.json
│   ├── 47B_qwen_read_only_recommendation_filter_rollup_certification_latest.json
│   ├── 47C_handoff_bundle_refresh_latest.json
│   ├── 48A_qwen_read_only_response_validator_stub_latest.json
│   ├── 48B_qwen_read_only_response_validator_rollup_certification_latest.json
│   ├── 48C_handoff_bundle_refresh_latest.json
│   ├── 49A_qwen_read_only_architecture_session_contract_stub_latest.json
│   ├── 49B_qwen_read_only_architecture_session_contract_rollup_certification_latest.json
│   ├── 49C_handoff_bundle_refresh_latest.json
│   ├── 50A_qwen_read_only_session_response_bridge_stub_latest.json
│   ├── 50B_qwen_read_only_session_response_bridge_rollup_certification_latest.json
│   ├── 50C_handoff_bundle_refresh_latest.json
│   ├── 51A_qwen_read_only_architecture_loop_boundary_stub_latest.json
│   ├── 51B_qwen_read_only_architecture_loop_boundary_rollup_certification_latest.json
│   ├── 51C_handoff_bundle_refresh_latest.json
│   ├── 52A_qwen_read_only_final_guardrail_summary_stub_latest.json
│   ├── 52B_qwen_read_only_final_guardrail_summary_rollup_certification_latest.json
│   ├── 52C_handoff_bundle_refresh_latest.json
│   ├── 53A_qwen_read_only_handoff_freeze_stub_latest.json
│   ├── 53B_qwen_read_only_handoff_freeze_rollup_certification_latest.json
│   ├── 53C_handoff_bundle_refresh_latest.json
│   ├── 54A_qwen_read_only_handoff_export_summary_stub_latest.json
│   ├── 54B_qwen_read_only_handoff_export_summary_rollup_certification_latest.json
│   ├── 54C_handoff_bundle_refresh_latest.json
│   ├── 55A_qwen_read_only_architecture_state_machine_stub_latest.json
│   ├── 55B_qwen_read_only_architecture_state_machine_rollup_certification_latest.json
│   ├── 55C_handoff_bundle_refresh_latest.json
│   ├── 56A_qwen_read_only_architecture_policy_map_stub_latest.json
│   ├── 56B_qwen_read_only_architecture_policy_map_rollup_certification_latest.json
│   ├── 56C_handoff_bundle_refresh_latest.json
│   ├── 57A_qwen_read_only_policy_boundary_matrix_stub_latest.json
│   ├── 57B_qwen_read_only_policy_boundary_matrix_rollup_certification_latest.json
│   ├── 57C_handoff_bundle_refresh_latest.json
│   ├── 58A_qwen_read_only_final_context_package_stub_latest.json
│   ├── 58B_qwen_read_only_final_context_package_rollup_certification_latest.json
│   ├── 58C_handoff_bundle_refresh_latest.json
│   ├── 59A_qwen_read_only_final_handoff_certification_stub_latest.json
│   ├── 59B_qwen_read_only_final_handoff_certification_rollup_certification_latest.json
│   ├── 59C_handoff_bundle_refresh_latest.json
│   ├── 60A_qwen_read_only_terminal_freeze_stub_latest.json
│   ├── 60B_qwen_read_only_terminal_freeze_rollup_certification_latest.json
│   ├── 60C_handoff_bundle_refresh_latest.json
│   ├── 61A_archive_or_new_chat_handoff_summary_latest.json
│   ├── candidate_20260706_144431_8a545b3c_mock_metrics.json
│   ├── candidate_20260706_144431_8a545b3c_mock_scorecard.json
│   ├── candidate_20260706_144431_8a545b3c_sandbox_result_stub.json
│   ├── candidate_20260706_144431_8a545b3c_sandbox_stub.json
│   ├── candidate_20260706_145350_816903d1_mock_metrics.json
│   ├── candidate_20260706_145350_816903d1_mock_scorecard.json
│   ├── candidate_20260706_145350_816903d1_sandbox_result_stub.json
│   ├── candidate_20260706_145350_816903d1_sandbox_stub.json
│   ├── candidate_20260706_150540_4fc7b8ab_mock_metrics.json
│   ├── candidate_20260706_150540_4fc7b8ab_mock_scorecard.json
│   ├── candidate_20260706_150540_4fc7b8ab_sandbox_result_stub.json
│   ├── candidate_20260706_150540_4fc7b8ab_sandbox_stub.json
│   ├── candidate_20260706_151330_9f852272_mock_metrics.json
│   ├── candidate_20260706_151330_9f852272_mock_scorecard.json
│   ├── candidate_20260706_151330_9f852272_sandbox_result_stub.json
│   ├── candidate_20260706_151330_9f852272_sandbox_stub.json
│   ├── candidate_20260706_152354_e2129e4e_mock_metrics.json
│   ├── candidate_20260706_152354_e2129e4e_mock_scorecard.json
│   ├── candidate_20260706_152354_e2129e4e_sandbox_result_stub.json
│   ├── candidate_20260706_152354_e2129e4e_sandbox_stub.json
│   ├── candidate_20260706_152930_73031c40_mock_metrics.json
│   ├── candidate_20260706_152930_73031c40_mock_scorecard.json
│   ├── candidate_20260706_152930_73031c40_sandbox_result_stub.json
│   ├── candidate_20260706_152930_73031c40_sandbox_stub.json
│   ├── candidate_sandbox_execution_contract_v1.json
│   ├── candidate_sandbox_execution_contract_v1.txt
│   ├── candidate_sandbox_mock_metrics_index_latest.json
│   ├── candidate_sandbox_mock_metrics_index_latest.txt
│   ├── candidate_sandbox_mock_scorecard_latest.json
│   ├── candidate_sandbox_mock_scorecard_latest.txt
│   ├── candidate_sandbox_result_example_latest.json
│   ├── candidate_sandbox_result_schema_v1.json
│   ├── candidate_sandbox_result_stub_index_latest.json
│   ├── candidate_sandbox_result_stub_index_latest.txt
│   ├── historical_bars_contract_v1.json
│   ├── historical_bars_contract_v1.txt
│   ├── historical_replay_engine_stub_latest.json
│   ├── historical_replay_engine_stub_latest.txt
│   ├── historical_replay_input_contract_v1.json
│   ├── historical_replay_input_contract_v1.txt
│   ├── historical_replay_market_data_provider_contract_v1.json
│   ├── historical_replay_market_data_provider_contract_v1.txt
│   ├── historical_replay_provider_adapter_stub_latest.json
│   ├── historical_replay_provider_adapter_stub_latest.txt
│   ├── historical_replay_validation_stub_latest.json
│   ├── historical_replay_validation_stub_latest.txt
│   ├── sandbox_dry_run_index_latest.json
│   ├── sandbox_dry_run_index_latest.txt
│   ├── simulation_harness_stub_latest.json
│   ├── simulation_harness_stub_latest.txt
│   ├── yfinance_historical_bars_adapter_shape_validation_latest.json
│   ├── yfinance_historical_bars_adapter_shape_validation_latest.txt
│   ├── yfinance_historical_bars_adapter_stub_latest.json
│   ├── yfinance_historical_bars_adapter_stub_latest.txt
│   ├── yfinance_historical_bars_adapter_wire_latest.json
│   ├── yfinance_historical_bars_adapter_wire_preview_latest.json
│   ├── yfinance_historical_bars_adapter_wire_preview_latest.txt
│   ├── yfinance_historical_bars_provider_probe_latest.json
│   └── yfinance_historical_bars_provider_probe_latest.txt
└── strategy_candidates/
    ├── candidate_20260706_144431_8a545b3c.json
    ├── candidate_20260706_145350_816903d1.json
    ├── candidate_20260706_150540_4fc7b8ab.json
    ├── candidate_20260706_151330_9f852272.json
    ├── candidate_20260706_152354_e2129e4e.json
    ├── candidate_20260706_152930_73031c40.json
    ├── candidate_20260706_171550_aca89979.json
    ├── candidate_20260706_171803_7979fee4.json
    ├── candidate_20260706_171835_2412645f.json
    ├── candidate_20260706_190850_245c152e.json
    ├── candidate_20260706_190919_18dff139.json
    ├── candidate_20260706_190955_47174fc4.json
    ├── candidate_20260706_201713_2d8f8e9e.json
    ├── candidate_20260706_201808_d90bd687.json
    ├── candidate_20260706_221600_b8f7600a.json
    ├── candidate_20260706_234404_20bfeb59.json
    ├── review_index_latest.json
    └── review_index_latest.txt

```


# Audit Tree

```text
audit MISSING

```


# Certification Timeline

```text
• candidate_sandbox_result_schema_v1

• 27C_CANDIDATE_SANDBOX_DRY_RUN_STUB

• 27E_CANDIDATE_SANDBOX_RESULT_STUB_GENERATOR

• 28A_CANDIDATE_SANDBOX_SIMULATION_HARNESS_STUB

• 28B_CANDIDATE_SANDBOX_MOCK_METRICS_GENERATOR

• 28C_CANDIDATE_SANDBOX_MOCK_SCORECARD

• 28D_CANDIDATE_SANDBOX_EXECUTION_CONTRACT

• 29A_HISTORICAL_REPLAY_ENGINE_STUB

• 29B_HISTORICAL_REPLAY_INPUT_CONTRACT

• 29C_HISTORICAL_REPLAY_VALIDATION_STUB

• 29E_HISTORICAL_REPLAY_MARKET_DATA_PROVIDER_CONTRACT

• 29F_HISTORICAL_REPLAY_PROVIDER_ADAPTER_STUB

• 30A_YFINANCE_HISTORICAL_BARS_PROVIDER_PROBE

• 30C_HISTORICAL_BARS_CONTRACT

• 30D_YFINANCE_HISTORICAL_BARS_ADAPTER_STUB

• 30E_YFINANCE_HISTORICAL_BARS_ADAPTER_SHAPE_VALIDATION

• 30F_YFINANCE_HISTORICAL_BARS_ADAPTER_WIRE_PREVIEW

• 30G_YFINANCE_HISTORICAL_BARS_ADAPTER_WIRE

✅ 31A_HISTORICAL_BARS_FETCH_VALIDATION

✅ 31B_HISTORICAL_BARS_MULTI_SYMBOL_VALIDATION

✅ 31C_HISTORICAL_REPLAY_EXECUTOR_STUB

✅ 31D_HISTORICAL_REPLAY_BAR_ITERATOR

✅ 31E_FIRST_SINGLE_CANDIDATE_REPLAY_DRY_RUN

✅ 31F_REPLAY_METRICS_CONTRACT

✅ 32A_REAL_METRICS_GENERATION

✅ 32B_CANDIDATE_SCORECARD_FROM_REPLAY_METRICS

✅ 32C_MANUAL_PROMOTION_GATE_STUB

✅ 32D_PIPELINE_ROLLUP_CERTIFICATION

✅ 32E_HANDOFF_BUNDLE_REFRESH
   └─ Early Training Infrastructure + Bar-Only Replay Metrics Pipeline Complete
      next: 33A_TRADE_SIMULATION_CONTRACT_STUB

✅ 33A_TRADE_SIMULATION_CONTRACT_STUB

✅ 33B_TRADE_EVENT_VALIDATION_STUB

✅ 33C_TRADE_SIMULATION_DRY_RUN_STUB

✅ 33D_ENTRY_EXIT_SIGNAL_CONTRACT_STUB

✅ 33E_HOLD_SIGNAL_GENERATOR_STUB

✅ 33F_ENTRY_EXIT_DECISION_ENGINE_STUB

✅ 33G_HOLD_DECISION_TO_HOLD_EVENT_BRIDGE

✅ 33H_TRADE_SIMULATION_PIPELINE_ROLLUP_CERTIFICATION
      next: 33I_HANDOFF_BUNDLE_REFRESH

✅ 33I_HANDOFF_BUNDLE_REFRESH
   └─ Early Training Infrastructure + Bar-Only Metrics + Hold-Only Trade Simulation Runway Complete
      next: 34A_ENTRY_SIGNAL_RULE_CONTRACT_STUB

✅ 34A_ENTRY_SIGNAL_RULE_CONTRACT_STUB

✅ 34B_ENTRY_SIGNAL_RULE_VALIDATION_STUB

✅ 34C_ENTRY_SIGNAL_GENERATOR_DISABLED_STUB

✅ 34D_ENTRY_SIGNAL_PIPELINE_ROLLUP_CERTIFICATION
      next: 34E_HANDOFF_BUNDLE_REFRESH

✅ 34E_HANDOFF_BUNDLE_REFRESH
   └─ Early Training Infrastructure + Hold-Only Simulation Runway + Disabled Entry Signal Pipeline Complete
      next: 35A_EXIT_SIGNAL_RULE_CONTRACT_STUB

✅ 35A_EXIT_SIGNAL_RULE_CONTRACT_STUB

✅ 35B_EXIT_SIGNAL_RULE_VALIDATION_STUB

✅ 35C_EXIT_SIGNAL_GENERATOR_DISABLED_STUB

✅ 35D_EXIT_SIGNAL_PIPELINE_ROLLUP_CERTIFICATION
      next: 35E_HANDOFF_BUNDLE_REFRESH

✅ 35E_STRATEGY_SANDBOX_WIREGRAPH_CERTIFICATION
   └─ Strategy sandbox wiregraph certified

✅ 35F_HANDOFF_BUNDLE_REFRESH
   └─ Strategy Sandbox Wiregraph Complete With Entry/Exit Generation Disabled
      next: 36A_STRATEGY_RULE_ENABLEMENT_GATE_CONTRACT_STUB

✅ 36A_STRATEGY_RULE_ENABLEMENT_GATE_CONTRACT_STUB

✅ 36B_ENABLEMENT_GATE_VALIDATION_STUB

✅ 36C_ENABLEMENT_GATE_PIPELINE_ROLLUP_CERTIFICATION
      next: 36D_HANDOFF_BUNDLE_REFRESH

✅ 36D_HANDOFF_BUNDLE_REFRESH
   └─ Strategy Rule Enablement Gate Certified (Locked)
      next: 37A_TRADE_SIMULATION_ENABLEMENT_GATE_CONTRACT_STUB

✅ 37A_TRADE_SIMULATION_ENABLEMENT_GATE_CONTRACT_STUB

✅ 37B_TRADE_SIMULATION_ENABLEMENT_GATE_VALIDATION_STUB

✅ 37C_TRADE_SIMULATION_ENABLEMENT_GATE_PIPELINE_ROLLUP_CERTIFICATION
      next: 37D_HANDOFF_BUNDLE_REFRESH

✅ 37D_HANDOFF_BUNDLE_REFRESH
   └─ Trade Simulation Enablement Gate Certified Locked
      next: 38A_RISK_GATE_CONTRACT_STUB

✅ 38A_RISK_GATE_CONTRACT_STUB

✅ 38B_RISK_GATE_VALIDATION_STUB

✅ 38C_RISK_GATE_PIPELINE_ROLLUP_CERTIFICATION
      next: 38D_HANDOFF_BUNDLE_REFRESH

✅ 38D_HANDOFF_BUNDLE_REFRESH
   └─ Risk Gate Certified Locked
      next: 39A_MASTER_SANDBOX_GATE_WIREGRAPH_REFRESH

✅ 39A_MASTER_SANDBOX_GATE_WIREGRAPH_REFRESH
   └─ Master sandbox gate dependency wiregraph refreshed

✅ 39B_MASTER_SANDBOX_GATE_WIREGRAPH_ROLLUP_CERTIFICATION
      next: 39C_HANDOFF_BUNDLE_REFRESH

✅ 39C_HANDOFF_BUNDLE_REFRESH
   └─ Master Sandbox Gate Wiregraph Certified
      next: 40A_SANDBOX_RUNTIME_DEPENDENCY_TRACE_STUB

✅ 40A_SANDBOX_RUNTIME_DEPENDENCY_TRACE_STUB

✅ 40B_SANDBOX_RUNTIME_DEPENDENCY_TRACE_ROLLUP_CERTIFICATION
      next: 40C_HANDOFF_BUNDLE_REFRESH

✅ 40C_HANDOFF_BUNDLE_REFRESH
   └─ Sandbox Runtime Dependency Trace Certified Locked
      next: 41A_SAFE_READ_ONLY_ARCHITECTURE_INSPECTOR_STUB

✅ 41A_SAFE_READ_ONLY_ARCHITECTURE_INSPECTOR_STUB

✅ 41B_SAFE_READ_ONLY_ARCHITECTURE_INSPECTOR_ROLLUP_CERTIFICATION
      next: 41C_HANDOFF_BUNDLE_REFRESH

✅ 41C_HANDOFF_BUNDLE_REFRESH
   └─ Read-Only Architecture Inspector Certified
      next: 42A_QWEN_READ_ONLY_ARCHITECTURE_CONTEXT_STUB

✅ 42A_QWEN_READ_ONLY_ARCHITECTURE_CONTEXT_STUB

✅ 42B_QWEN_READ_ONLY_ARCHITECTURE_CONTEXT_ROLLUP_CERTIFICATION
      next: 42C_HANDOFF_BUNDLE_REFRESH

✅ 42C_HANDOFF_BUNDLE_REFRESH
   └─ Qwen Read-Only Architecture Context Certified
      next: 43A_QWEN_CONTEXT_RESPONSE_CONTRACT_STUB

✅ 43A_QWEN_CONTEXT_RESPONSE_CONTRACT_STUB

✅ 43B_QWEN_CONTEXT_RESPONSE_CONTRACT_ROLLUP_CERTIFICATION
      next: 43C_HANDOFF_BUNDLE_REFRESH

✅ 43C_HANDOFF_BUNDLE_REFRESH
   └─ Qwen Read-Only Response Contract Certified
      next: 44A_QWEN_READ_ONLY_RESPONSE_SAMPLE_STUB

✅ 44A_QWEN_READ_ONLY_RESPONSE_SAMPLE_STUB

✅ 44B_QWEN_READ_ONLY_RESPONSE_SAMPLE_ROLLUP_CERTIFICATION
      next: 44C_HANDOFF_BUNDLE_REFRESH

✅ 44C_HANDOFF_BUNDLE_REFRESH
   └─ Qwen Read-Only Response Sample Certified
      next: 45A_QWEN_READ_ONLY_ARCHITECTURE_SUMMARY_GATE_STUB

✅ 45A_QWEN_READ_ONLY_ARCHITECTURE_SUMMARY_GATE_STUB

✅ 45B_QWEN_READ_ONLY_ARCHITECTURE_SUMMARY_GATE_ROLLUP_CERTIFICATION
      next: 45C_HANDOFF_BUNDLE_REFRESH

✅ 45C_HANDOFF_BUNDLE_REFRESH
   └─ Qwen Read-Only Architecture Summary Gate Certified
      next: 46A_QWEN_READ_ONLY_MISSING_CONTEXT_DETECTOR_STUB

✅ 46A_QWEN_READ_ONLY_MISSING_CONTEXT_DETECTOR_STUB

✅ 46B_QWEN_READ_ONLY_MISSING_CONTEXT_DETECTOR_ROLLUP_CERTIFICATION
      next: 46C_HANDOFF_BUNDLE_REFRESH

✅ 46C_HANDOFF_BUNDLE_REFRESH
   └─ Qwen Read-Only Missing Context Detector Certified
      next: 47A_QWEN_READ_ONLY_RECOMMENDATION_FILTER_STUB

✅ 47A_QWEN_READ_ONLY_RECOMMENDATION_FILTER_STUB

✅ 47B_QWEN_READ_ONLY_RECOMMENDATION_FILTER_ROLLUP_CERTIFICATION
      next: 47C_HANDOFF_BUNDLE_REFRESH

✅ 47C_HANDOFF_BUNDLE_REFRESH
   └─ Qwen Read-Only Recommendation Filter Certified
      next: 48A_QWEN_READ_ONLY_RESPONSE_VALIDATOR_STUB

✅ 48A_QWEN_READ_ONLY_RESPONSE_VALIDATOR_STUB

✅ 48B_QWEN_READ_ONLY_RESPONSE_VALIDATOR_ROLLUP_CERTIFICATION
      next: 48C_HANDOFF_BUNDLE_REFRESH

✅ 48C_HANDOFF_BUNDLE_REFRESH
   └─ Qwen Read-Only Response Validator Certified
      next: 49A_QWEN_READ_ONLY_ARCHITECTURE_SESSION_CONTRACT_STUB

✅ 49A_QWEN_READ_ONLY_ARCHITECTURE_SESSION_CONTRACT_STUB

✅ 49B_QWEN_READ_ONLY_ARCHITECTURE_SESSION_CONTRACT_ROLLUP_CERTIFICATION
      next: 49C_HANDOFF_BUNDLE_REFRESH

✅ 49C_HANDOFF_BUNDLE_REFRESH
   └─ Qwen Read-Only Architecture Session Contract Certified
      next: 50A_QWEN_READ_ONLY_SESSION_RESPONSE_BRIDGE_STUB

✅ 50A_QWEN_READ_ONLY_SESSION_RESPONSE_BRIDGE_STUB

✅ 50B_QWEN_READ_ONLY_SESSION_RESPONSE_BRIDGE_ROLLUP_CERTIFICATION
      next: 50C_HANDOFF_BUNDLE_REFRESH

✅ 50C_HANDOFF_BUNDLE_REFRESH
   └─ Qwen Read-Only Session Response Bridge Certified
      next: 51A_QWEN_READ_ONLY_ARCHITECTURE_LOOP_BOUNDARY_STUB

✅ 51A_QWEN_READ_ONLY_ARCHITECTURE_LOOP_BOUNDARY_STUB

✅ 51B_QWEN_READ_ONLY_ARCHITECTURE_LOOP_BOUNDARY_ROLLUP_CERTIFICATION
      next: 51C_HANDOFF_BUNDLE_REFRESH

✅ 51C_HANDOFF_BUNDLE_REFRESH
   └─ Qwen Read-Only Architecture Loop Boundary Certified
      next: 52A_QWEN_READ_ONLY_FINAL_GUARDRAIL_SUMMARY_STUB

✅ 52A_QWEN_READ_ONLY_FINAL_GUARDRAIL_SUMMARY_STUB

✅ 52B_QWEN_READ_ONLY_FINAL_GUARDRAIL_SUMMARY_ROLLUP_CERTIFICATION
      next: 52C_HANDOFF_BUNDLE_REFRESH

✅ 52C_HANDOFF_BUNDLE_REFRESH
   └─ Qwen Read-Only Final Guardrail Summary Certified
      next: 53A_QWEN_READ_ONLY_HANDOFF_FREEZE_STUB

✅ 53A_QWEN_READ_ONLY_HANDOFF_FREEZE_STUB

✅ 53B_QWEN_READ_ONLY_HANDOFF_FREEZE_ROLLUP_CERTIFICATION
      next: 53C_HANDOFF_BUNDLE_REFRESH

✅ 53C_HANDOFF_BUNDLE_REFRESH
   └─ Qwen Read-Only Handoff Freeze Certified
      next: 54A_QWEN_READ_ONLY_HANDOFF_EXPORT_SUMMARY_STUB

✅ 54A_QWEN_READ_ONLY_HANDOFF_EXPORT_SUMMARY_STUB

✅ 54B_QWEN_READ_ONLY_HANDOFF_EXPORT_SUMMARY_ROLLUP_CERTIFICATION
      next: 54C_HANDOFF_BUNDLE_REFRESH

✅ 54C_HANDOFF_BUNDLE_REFRESH
   └─ Qwen Read-Only Handoff Export Summary Certified
      next: 55A_QWEN_READ_ONLY_ARCHITECTURE_STATE_MACHINE_STUB

✅ 55A_QWEN_READ_ONLY_ARCHITECTURE_STATE_MACHINE_STUB

✅ 55B_QWEN_READ_ONLY_ARCHITECTURE_STATE_MACHINE_ROLLUP_CERTIFICATION
      next: 55C_HANDOFF_BUNDLE_REFRESH

✅ 55C_HANDOFF_BUNDLE_REFRESH
      next: 56A_QWEN_READ_ONLY_ARCHITECTURE_POLICY_MAP_STUB

✅ 56A_QWEN_READ_ONLY_ARCHITECTURE_POLICY_MAP_STUB

✅ 56B_QWEN_READ_ONLY_ARCHITECTURE_POLICY_MAP_ROLLUP_CERTIFICATION
      next: 56C_HANDOFF_BUNDLE_REFRESH

✅ 56C_HANDOFF_BUNDLE_REFRESH
      next: 57A_QWEN_READ_ONLY_POLICY_BOUNDARY_MATRIX_STUB

✅ 57A_QWEN_READ_ONLY_POLICY_BOUNDARY_MATRIX_STUB

✅ 57B_QWEN_READ_ONLY_POLICY_BOUNDARY_MATRIX_ROLLUP_CERTIFICATION
      next: 57C_HANDOFF_BUNDLE_REFRESH

✅ 57C_HANDOFF_BUNDLE_REFRESH
      next: 58A_QWEN_READ_ONLY_FINAL_CONTEXT_PACKAGE_STUB

✅ 58A_QWEN_READ_ONLY_FINAL_CONTEXT_PACKAGE_STUB

✅ 58B_QWEN_READ_ONLY_FINAL_CONTEXT_PACKAGE_ROLLUP_CERTIFICATION
      next: 58C_HANDOFF_BUNDLE_REFRESH

✅ 58C_HANDOFF_BUNDLE_REFRESH
      next: 59A_QWEN_READ_ONLY_FINAL_HANDOFF_CERTIFICATION_STUB

✅ 59A_QWEN_READ_ONLY_FINAL_HANDOFF_CERTIFICATION_STUB

✅ 59B_QWEN_READ_ONLY_FINAL_HANDOFF_CERTIFICATION_ROLLUP_CERTIFICATION
      next: 59C_HANDOFF_BUNDLE_REFRESH

✅ 59C_HANDOFF_BUNDLE_REFRESH
      next: 60A_QWEN_READ_ONLY_TERMINAL_FREEZE_STUB

✅ 60A_QWEN_READ_ONLY_TERMINAL_FREEZE_STUB

✅ 60B_QWEN_READ_ONLY_TERMINAL_FREEZE_ROLLUP_CERTIFICATION
      next: 60C_HANDOFF_BUNDLE_REFRESH

✅ 60C_HANDOFF_BUNDLE_REFRESH
      next: HANDOFF_TO_NEW_CHAT_OR_ARCHIVE_ONLY

✅ 61A_ARCHIVE_OR_NEW_CHAT_HANDOFF_SUMMARY

• candidate_sandbox_result_example_latest

• candidate_20260706_144431_8a545b3c_mock_metrics

• candidate_20260706_144431_8a545b3c_mock_scorecard

• candidate_20260706_144431_8a545b3c_sandbox_result_stub

• candidate_20260706_144431_8a545b3c_sandbox_stub

• candidate_20260706_145350_816903d1_mock_metrics

• candidate_20260706_145350_816903d1_mock_scorecard

• candidate_20260706_145350_816903d1_sandbox_result_stub

• candidate_20260706_145350_816903d1_sandbox_stub

• candidate_20260706_150540_4fc7b8ab_mock_metrics

• candidate_20260706_150540_4fc7b8ab_mock_scorecard

• candidate_20260706_150540_4fc7b8ab_sandbox_result_stub

• candidate_20260706_150540_4fc7b8ab_sandbox_stub

• candidate_20260706_151330_9f852272_mock_metrics

• candidate_20260706_151330_9f852272_mock_scorecard

• candidate_20260706_151330_9f852272_sandbox_result_stub

• candidate_20260706_151330_9f852272_sandbox_stub

• candidate_20260706_152354_e2129e4e_mock_metrics

• candidate_20260706_152354_e2129e4e_mock_scorecard

• candidate_20260706_152354_e2129e4e_sandbox_result_stub

• candidate_20260706_152354_e2129e4e_sandbox_stub

• candidate_20260706_152930_73031c40_mock_metrics

• candidate_20260706_152930_73031c40_mock_scorecard

• candidate_20260706_152930_73031c40_sandbox_result_stub

• candidate_20260706_152930_73031c40_sandbox_stub

```


# Future Roadmap

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


# Developer Rulebook

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


# Glossary

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


# Traceability Index

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

Certified count: 110
Uncertified / historical count: 43

---

# 3. [Reference] Architecture Atlas

Source: `handoff/project_bible/architecture_atlas/ARCHITECTURE_ATLAS.md`



# Architecture Atlas Overview

Generated: 2026-07-07T03:10:44.678181+00:00
Controller: 63B_ARCHITECTURE_ATLAS_GENERATOR
Mode: READ ONLY ATLAS COMPILER

This atlas explains NeuroVest topology, ownership, flow, and certification history using existing repository and handoff evidence only.


# Expanded Node Map

```text
NEUROVEST SYSTEM NODE MAP

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

```


# Dependency Graph

```text
HIGH-LEVEL DEPENDENCY GRAPH

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

```


# Runtime State Machine

```text
QWEN READ-ONLY STATE MACHINE

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

```


# Stack Ownership

## auth

Files detected: 4

Owns:
- stack-specific files detected by topology scan

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `backend/app/stacks/auth_identity/__init__.py`
- `backend/app/stacks/auth_identity/base.py`
- `backend/app/stacks/auth_identity/validator.py`
- `backend/app/stacks/auth_identity/gate.py`

## backend_uncategorized

Files detected: 27

Owns:
- stack-specific files detected by topology scan

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `backend/__init__.py`
- `backend/requirements.txt`
- `backend/app/main.py`
- `backend/app/__init__.py`
- `backend/scripts/backup_db.sh`
- `backend/app/schemas/__init__.py`
- `backend/app/schemas/dashboard.py`
- `backend/app/test/test_neuro_repo_companion.py`
- `backend/app/test/test_trading_pipeline.py`
- `backend/app/api/graph_ws.py`
- `backend/app/services/__init__.py`
- `backend/app/analysis/architecture.py`

## chat

Files detected: 43

Owns:
- chat runtime, memory, prompts, Qwen/Ollama-facing chat layer

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `.aider.chat.history.md`
- `scripts/phase20f_floating_chat_widget_certification.py`
- `scripts/phase26f_chat_ui_state_cleanup_metadata_rendering_certification.py`
- `scripts/phase26d_frontend_chat_response_normalizer_certification.py`
- `scripts/phase26f_chat_ui_state_cleanup_metadata_rendering.py`
- `scripts/phase21cd_chat_ux_persistent_cache.py`
- `scripts/phase21_fix_chat_service_generator.py`
- `scripts/phase26a_chat_intent_regex_ollama_router.py`
- `scripts/phase26e_chat_metadata_chips_typing_enter_certification.py`
- `scripts/phase20_floating_chat_widget_service_chain.py`
- `scripts/phase21cd_chat_ux_persistent_cache_certification.py`
- `scripts/phase26b_wire_ollama_into_chat_runtime.py`

## execution

Files detected: 19

Owns:
- paper broker, ledger, fills, commissions, sandbox runtime

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `scripts/phase28d_candidate_sandbox_execution_contract_certification.py`
- `scripts/phase28d_candidate_sandbox_execution_contract.py`
- `scripts/phase26c_chat_safety_prompt_live_execution_guard_certification.py`
- `backend/app/stacks/execution/__init__.py`
- `backend/app/stacks/execution/sandbox_runtime.py`
- `backend/app/stacks/execution/commission_engine.py`
- `backend/app/stacks/execution/sandbox.py`
- `backend/app/stacks/execution/regime_modes.py`
- `backend/app/stacks/execution/pnl_engine.py`
- `backend/app/stacks/execution/executor.py`
- `backend/app/stacks/execution/trade_ledger.py`
- `backend/app/stacks/execution/regime_simulator.py`

## frontend

Files detected: 28

Owns:
- stack-specific files detected by topology scan

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `frontend/next-env.d.ts`
- `frontend/package-lock.json`
- `frontend/CLAUDE.md`
- `frontend/next.config.ts`
- `frontend/eslint.config.mjs`
- `frontend/tsconfig.json`
- `frontend/postcss.config.mjs`
- `frontend/README.md`
- `frontend/.gitignore`
- `frontend/package.json`
- `frontend/AGENTS.md`
- `frontend/app/globals.css`

## journal

Files detected: 4

Owns:
- stack-specific files detected by topology scan

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `backend/app/stacks/journal_ledger/ledger.py`
- `backend/app/stacks/journal_ledger/__init__.py`
- `backend/app/stacks/journal_ledger/record.py`
- `backend/app/stacks/journal_ledger/base.py`

## learning

Files detected: 9

Owns:
- replay research, Monte Carlo, probability, evaluator logic

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `backend/app/stacks/learning_research/strategy_evaluator.py`
- `backend/app/stacks/learning_research/__init__.py`
- `backend/app/stacks/learning_research/monte_carlo_mix.py`
- `backend/app/stacks/learning_research/monte_carlo.py`
- `backend/app/stacks/learning_research/research_loader.py`
- `backend/app/stacks/learning_research/probability_engine.py`
- `backend/app/stacks/learning_research/research_runtime.py`
- `backend/app/stacks/learning_research/base.py`
- `backend/app/stacks/learning_research/backtest_engine.py`

## market_data

Files detected: 15

Owns:
- provider routing, bars, price, sessions, market data service

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `scripts/phase29e_historical_replay_market_data_provider_contract_certification.py`
- `scripts/phase29e_historical_replay_market_data_provider_contract.py`
- `backend/app/stacks/market_data/yfinance_ingestor.py`
- `backend/app/stacks/market_data/provider_registry.py`
- `backend/app/stacks/market_data/__init__.py`
- `backend/app/stacks/market_data/feed.py`
- `backend/app/stacks/market_data/market_data_service.py`
- `backend/app/stacks/market_data/bars.py`
- `backend/app/stacks/market_data/market_session.py`
- `backend/app/stacks/market_data/provider_router.py`
- `backend/app/stacks/market_data/price.py`
- `backend/app/stacks/market_data/yfinance_historical_bars_adapter.py`

## notification

Files detected: 2

Owns:
- stack-specific files detected by topology scan

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `backend/app/stacks/notification/__init__.py`
- `backend/app/stacks/notification/base.py`

## portfolio

Files detected: 19

Owns:
- allocation, accounting, positions, dashboard data

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `scripts/phase13f_portfolio_positions_service_chain_certification.py`
- `scripts/phase13e_portfolio_service_chain_graph_export.py`
- `scripts/phase13_portfolio_positions_service_chain.py`
- `scripts/phase13g_portfolio_chain_dashboard_certification.py`
- `scripts/phase13g_add_portfolio_chain_to_dashboard.py`
- `frontend/services/portfolioService.ts`
- `frontend/app/api/v1/portfolio/positions/route.ts`
- `backend/app/stacks/portfolio/portfolio_service.py`
- `backend/app/stacks/portfolio/allocator.py`
- `backend/app/stacks/portfolio/__init__.py`
- `backend/app/stacks/portfolio/accounting.py`
- `backend/app/stacks/portfolio/portfolio_runtime.py`

## research

Files detected: 2

Owns:
- stack-specific files detected by topology scan

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `scripts/phase1_repo_research_market_bootstrap.py`
- `runtime/research_db/research_seed.json`

## risk

Files detected: 22

Owns:
- drawdown, exposure, loss streak, kill switch, risk service

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `scripts/phase15_risk_gate_service_chain.py`
- `scripts/phase15g_add_risk_chain_to_dashboard.py`
- `scripts/phase38b_risk_gate_validation_stub.py`
- `scripts/phase15e_risk_service_chain_graph_export.py`
- `scripts/phase38c_risk_gate_pipeline_rollup_certification.py`
- `scripts/phase15g_risk_chain_dashboard_certification.py`
- `scripts/phase15f_risk_gate_service_chain_certification.py`
- `scripts/phase38a_risk_gate_contract_stub.py`
- `frontend/services/riskService.ts`
- `frontend/app/api/v1/risk/gate/[symbol]/route.ts`
- `backend/app/stacks/risk/loss_streak_guard.py`
- `backend/app/stacks/risk/__init__.py`

## runtime_artifacts

Files detected: 103

Owns:
- stack-specific files detected by topology scan

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `runtime/market_warehouse/symbol_registry.json`
- `runtime/handoff_snapshot/live_graph_validate_latest.json`
- `runtime/handoff_snapshot/file_manifest_latest.txt`
- `runtime/handoff_snapshot/simulate_trade_guard_latest.json`
- `runtime/handoff_snapshot/topology_tree_latest.txt`
- `runtime/handoff_snapshot/neurovest_training_handoff_bundle_latest.json`
- `runtime/certifications/phase11_live_market_price_api_bridge_certification_latest.json`
- `runtime/certifications/phase22b_live_graph_visualization_certification_latest.json`
- `runtime/certifications/phase30f_yfinance_historical_bars_adapter_wire_preview_certification_latest.json`
- `runtime/certifications/phase17_dashboard_route_map_certification_latest.json`
- `runtime/certifications/phase30b_yfinance_provider_selection_snapshot_latest.json`
- `runtime/certifications/phase10d_runtime_static_dependency_diff_certification_latest.json`

## snaptrade

Files detected: 7

Owns:
- stack-specific files detected by topology scan

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `backend/app/snaptrade/executions/config.py`
- `backend/app/snaptrade/executions/execution_layer.py`
- `backend/app/stacks/snaptrade/__init__.py`
- `backend/app/stacks/snaptrade/execution.py`
- `backend/app/stacks/snaptrade/adapter.py`
- `backend/app/stacks/snaptrade/broker.py`
- `backend/app/stacks/snaptrade/base.py`

## strategy

Files detected: 247

Owns:
- strategy contracts, decisions, indicators, signal rules

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `scripts/phase36a_strategy_rule_enablement_gate_contract_stub.py`
- `scripts/phase27a_strategy_proposal_capture_certification.py`
- `scripts/phase27b_strategy_candidate_review_index.py`
- `scripts/phase35e_strategy_sandbox_wiregraph_certification.py`
- `scripts/phase14e_strategy_service_chain_graph_export.py`
- `scripts/phase27b_strategy_candidate_review_index_certification.py`
- `scripts/phase14f_strategy_decision_service_chain_certification.py`
- `scripts/phase14g_strategy_chain_dashboard_certification.py`
- `scripts/phase14g_add_strategy_chain_to_dashboard.py`
- `scripts/phase27a_strategy_proposal_capture.py`
- `scripts/phase14_strategy_decision_service_chain.py`
- `frontend/services/strategyService.ts`

## unknown

Files detected: 269

Owns:
- stack-specific files detected by topology scan

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `OUTPUT`
- `ARCHITECTURE_REPAIR_PLAN.json`
- `TOPOLOGY_NORMALIZED_STATE.json`
- `ARCH_GOVERNANCE.md`
- `fix_phase9_self_fingerprint.sh`
- `TOPOLOGY_STATE.json`
- `topology_wire_graph.png`
- `neurovest_repo_context.md`
- `Directory Structure`
- `ORPHAN_RESOLUTION_PLAN.json`
- `topology_wire_graph_canonical.png`
- `.env.example`

## wolfden

Files detected: 7

Owns:
- stack-specific files detected by topology scan

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `backend/app/stacks/wolfden_ai/memory.py`
- `backend/app/stacks/wolfden_ai/__init__.py`
- `backend/app/stacks/wolfden_ai/agent_router.py`
- `backend/app/stacks/wolfden_ai/orchestrator.py`
- `backend/app/stacks/wolfden_ai/routing.py`
- `backend/app/stacks/wolfden_ai/runtime.py`
- `backend/app/stacks/wolfden_ai/base.py`


# Layer Ownership

## L0_external_adapter

External providers and adapters only.
Files detected: 52

- `scripts/phase30g_yfinance_historical_bars_adapter_wire.py`
- `scripts/phase30a_yfinance_historical_bars_provider_probe_certification.py`
- `scripts/phase2_yfinance_market_warehouse.py`
- `scripts/phase30a_yfinance_historical_bars_provider_probe.py`
- `scripts/phase30e_yfinance_historical_bars_adapter_shape_validation.py`
- `scripts/phase30b_yfinance_provider_selection_snapshot.py`
- `scripts/phase30f_yfinance_historical_bars_adapter_wire_preview_certification.py`
- `scripts/phase30d_yfinance_historical_bars_adapter_stub_certification.py`
- `scripts/phase30f_yfinance_historical_bars_adapter_wire_preview.py`
- `scripts/phase29g_historical_replay_provider_readiness_snapshot.py`
- `scripts/phase30g_yfinance_historical_bars_adapter_wire_certification.py`
- `scripts/phase29f_historical_replay_provider_adapter_stub.py`
- `scripts/phase29e_historical_replay_market_data_provider_contract_certification.py`
- `scripts/phase29f_historical_replay_provider_adapter_stub_certification.py`
- `scripts/phase29e_historical_replay_market_data_provider_contract.py`

## L1_security_auth_safety

Auth, gates, guards, firewalls, locked safety contracts.
Files detected: 68

- `scripts/phase52b_qwen_read_only_final_guardrail_summary_rollup_certification.py`
- `scripts/phase36a_strategy_rule_enablement_gate_contract_stub.py`
- `scripts/phase39b_master_sandbox_gate_wiregraph_rollup_certification.py`
- `scripts/phase36b_enablement_gate_validation_stub.py`
- `scripts/phase45a_qwen_read_only_architecture_summary_gate_stub.py`
- `scripts/phase15_risk_gate_service_chain.py`
- `scripts/phase37a_trade_simulation_enablement_gate_contract_stub.py`
- `scripts/phase39a_master_sandbox_gate_wiregraph_refresh.py`
- `scripts/phase15g_add_risk_chain_to_dashboard.py`
- `scripts/phase37b_trade_simulation_enablement_gate_validation_stub.py`
- `scripts/phase38b_risk_gate_validation_stub.py`
- `scripts/phase15e_risk_service_chain_graph_export.py`
- `scripts/phase38c_risk_gate_pipeline_rollup_certification.py`
- `scripts/phase15g_risk_chain_dashboard_certification.py`
- `scripts/phase45b_qwen_read_only_architecture_summary_gate_rollup_certification.py`

## L2_domain

Pure business/domain logic and contracts.
Files detected: 243

- `domain_subsystem_graph.png`
- `domain_runtime_overlay_graph.png`
- `scripts/phase35a_exit_signal_rule_contract_stub.py`
- `scripts/phase27a_strategy_proposal_capture_certification.py`
- `scripts/phase29b_historical_replay_input_contract_certification.py`
- `scripts/phase31f_replay_metrics_contract.py`
- `scripts/phase43b_qwen_context_response_contract_rollup_certification.py`
- `scripts/phase33d_entry_exit_signal_contract_stub.py`
- `scripts/phase27b_strategy_candidate_review_index.py`
- `scripts/phase35c_exit_signal_generator_disabled_stub.py`
- `scripts/phase35d_exit_signal_pipeline_rollup_certification.py`
- `scripts/phase34b_entry_signal_rule_validation_stub.py`
- `scripts/phase10_domain_subsystem_visualization.py`
- `scripts/phase35e_strategy_sandbox_wiregraph_certification.py`
- `scripts/phase34d_entry_signal_pipeline_rollup_certification.py`

## L3_service_facade

Stable services coordinating domain/adapters.
Files detected: 36

- `SERVICE_RELOCATION_PLAN_RECONCILED.json`
- `SERVICE_RELOCATION_PLAN.json`
- `architecture_backup/dashboard_service.py`
- `scripts/phase13f_portfolio_positions_service_chain_certification.py`
- `scripts/phase12g_service_chain_repair.py`
- `scripts/phase21_fix_chat_service_generator.py`
- `scripts/phase12_service_layer_alignment.py`
- `scripts/phase12g_service_chain_dashboard_certification.py`
- `scripts/phase12f_service_chain_certification.py`
- `scripts/phase13e_portfolio_service_chain_graph_export.py`
- `scripts/phase20_floating_chat_widget_service_chain.py`
- `scripts/phase13_portfolio_positions_service_chain.py`
- `scripts/apply_service_relocation_v1.py`
- `scripts/phase12g_add_service_chain_to_dashboard.py`
- `scripts/service_stack_relocator_v1.py`

## L4_runtime_orchestration

Controllers, schedulers, runtime orchestration.
Files detected: 112

- `scripts/phase10d_runtime_static_dependency_diff_certification.py`
- `scripts/phase40b_sandbox_runtime_dependency_trace_rollup_certification.py`
- `scripts/phase40a_sandbox_runtime_dependency_trace_stub.py`
- `scripts/phase10c_runtime_flow_overlay_export.py`
- `scripts/phase10e_classify_runtime_static_diff_edges.py`
- `scripts/phase10c_runtime_flow_overlay_certification.py`
- `scripts/phase26b_wire_ollama_into_chat_runtime.py`
- `scripts/phase10d_runtime_static_dependency_diff.py`
- `scripts/phase62a_master_architecture_handoff_controller.py`
- `backend/app/core/runtime_firewall_v1.py`
- `backend/app/stacks/portfolio/portfolio_runtime.py`
- `backend/app/stacks/execution/sandbox_runtime.py`
- `backend/app/stacks/wolfden_ai/orchestrator.py`
- `backend/app/stacks/wolfden_ai/runtime.py`
- `backend/app/stacks/chat_public/chat_runtime.py`

## L5_api_presentation

API routes and presentation only.
Files detected: 20

- `scripts/phase11c_frontend_polling_api_cleanup.py`
- `scripts/phase26a_chat_intent_regex_ollama_router.py`
- `scripts/phase11d_next_api_proxy_live_price.py`
- `scripts/phase11_live_market_price_api_bridge_certification.py`
- `scripts/phase11_live_market_price_api_bridge.py`
- `scripts/phase19b_endpoint_activation_probe_repair.py`
- `scripts/phase11d_next_api_proxy_live_price_certification.py`
- `scripts/phase19c_endpoint_activation_certification.py`
- `scripts/phase17_dashboard_route_map_frontend_card_verification.py`
- `scripts/phase16_api_route_separation_certification.py`
- `scripts/phase17_dashboard_route_map_certification.py`
- `scripts/phase11c_frontend_polling_api_cleanup_certification.py`
- `frontend/app/api/v1/chat/route.ts`
- `frontend/app/api/v1/graph/live/route.ts`
- `frontend/app/api/v1/market/live-price/[symbol]/route.ts`

## L6_frontend

Next.js UI and client services.
Files detected: 104

- `cursor.AppImage`
- `scripts/phase23a_frontend_request_normalizer_certification.py`
- `scripts/phase26d_frontend_chat_response_normalizer_certification.py`
- `scripts/phase18_real_positions_panel_component.py`
- `scripts/phase23a_frontend_request_normalizer.py`
- `scripts/phase24a_frontend_observability_dashboard.py`
- `scripts/phase9b_component_overlay_export.py`
- `scripts/phase11f_frontend_type_lint_repair.py`
- `scripts/phase26d_frontend_chat_response_normalizer.py`
- `scripts/phase11e_frontend_build_type_certification.py`
- `scripts/phase11b_frontend_live_price_card_certification.py`
- `scripts/phase11f_frontend_type_lint_repair_certification.py`
- `scripts/phase11b_frontend_live_price_card.py`
- `scripts/phase24a_frontend_observability_dashboard_certification.py`
- `frontend/next-env.d.ts`

## L7_tests

Tests, fixtures, probes, validation.
Files detected: 4

- `neuro_cli_file_inspection.json`
- `pytest.ini`
- `scripts/phase41a_safe_read_only_architecture_inspector_stub.py`
- `scripts/phase41b_safe_read_only_architecture_inspector_rollup_certification.py`

## UNCLASSIFIED

Needs future classification; do not assume ownership.
Files detected: 188

- `OUTPUT`
- `ARCHITECTURE_REPAIR_PLAN.json`
- `TOPOLOGY_NORMALIZED_STATE.json`
- `ARCH_GOVERNANCE.md`
- `fix_phase9_self_fingerprint.sh`
- `TOPOLOGY_STATE.json`
- `topology_wire_graph.png`
- `neurovest_repo_context.md`
- `Directory Structure`
- `ORPHAN_RESOLUTION_PLAN.json`
- `topology_wire_graph_canonical.png`
- `.env.example`
- `generate_wire_graph.py`
- `neuro_health.sh`
- `.aider.input.history`


# Condensed Certification Timeline

## Foundation / Provider / Candidate Prep

• **candidate_sandbox_result_schema_v1**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_sandbox_result_schema_v1.json`

✅ **3M_GRAPH_CERTIFICATION**
   - evidence: `runtime/certifications/phase3m_graph_certification_latest.json`

✅ **4G_REPO_MEMORY_CERTIFICATION**
   - evidence: `runtime/certifications/phase4g_repo_memory_certification_latest.json`

✅ **5C_REPO_MEMORY_CERTIFICATION_V2**
   - evidence: `runtime/certifications/phase5c_repo_memory_certification_v2_latest.json`

✅ **6B_DEPENDENCY_VALIDATION_CERTIFICATION**
   - evidence: `runtime/certifications/phase6b_dependency_validation_certification_latest.json`

✅ **6D_DEPENDENCY_GRAPH_CERTIFICATION**
   - evidence: `runtime/certifications/phase6d_dependency_graph_certification_latest.json`

✅ **7G_GRAPH_VISUALIZATION_CERTIFICATION**
   - evidence: `runtime/certifications/phase7g_graph_visualization_certification_latest.json`

✅ **8C_NEURO_CLI_HOTSPOTS_CERTIFICATION**
   - evidence: `runtime/certifications/phase8c_neuro_cli_hotspots_certification_latest.json`

⚠️ **9E_CANONICAL_GRAPH_CERTIFICATION**
   - evidence: `runtime/certifications/phase9e_canonical_graph_certification_latest.json`

✅ **9M_CANONICAL_GRAPH_CERTIFICATION_V2**
   - evidence: `runtime/certifications/phase9m_canonical_graph_certification_v2_latest.json`

✅ **10C_RUNTIME_FLOW_OVERLAY_CERTIFICATION**
   - evidence: `runtime/certifications/phase10c_runtime_flow_overlay_certification_latest.json`

✅ **10D_RUNTIME_STATIC_DEPENDENCY_DIFF_CERTIFICATION**
   - evidence: `runtime/certifications/phase10d_runtime_static_dependency_diff_certification_latest.json`

✅ **10E_DIFF_CLASSIFICATION_CERTIFICATION**
   - evidence: `runtime/certifications/phase10e_diff_classification_certification_latest.json`

✅ **10F_ARCHITECTURE_DRIFT_WATCH_CERTIFICATION**
   - evidence: `runtime/certifications/phase10f_architecture_drift_watch_certification_latest.json`

✅ **10G_ARCHITECTURE_DRIFT_DASHBOARD_CERTIFICATION**
   - evidence: `runtime/certifications/phase10g_architecture_drift_dashboard_certification_latest.json`

✅ **10H_ARCHITECTURE_DASHBOARD_COMMAND_CERTIFICATION**
   - evidence: `runtime/certifications/phase10h_architecture_dashboard_command_certification_latest.json`

✅ **10_DOMAIN_SUBSYSTEM_VISUALIZATION_CERTIFICATION**
   - evidence: `runtime/certifications/phase10_domain_subsystem_visualization_certification_latest.json`

⚠️ **11B_FRONTEND_LIVE_PRICE_CARD_CERTIFICATION**
   - evidence: `runtime/certifications/phase11b_frontend_live_price_card_certification_latest.json`

⚠️ **11C_FRONTEND_POLLING_API_CLEANUP_CERTIFICATION**
   - evidence: `runtime/certifications/phase11c_frontend_polling_api_cleanup_certification_latest.json`

✅ **11D_NEXT_API_PROXY_LIVE_PRICE_CERTIFICATION**
   - evidence: `runtime/certifications/phase11d_next_api_proxy_live_price_certification_latest.json`

⚠️ **11E_FRONTEND_BUILD_TYPE_CERTIFICATION**
   - evidence: `runtime/certifications/phase11e_frontend_build_type_certification_latest.json`

✅ **11F_FRONTEND_TYPE_LINT_REPAIR_CERTIFICATION**
   - evidence: `runtime/certifications/phase11f_frontend_type_lint_repair_certification_latest.json`

✅ **11G_LIVE_MARKET_DASHBOARD_EXPANSION_CERTIFICATION**
   - evidence: `runtime/certifications/phase11g_live_market_dashboard_expansion_certification_latest.json`

✅ **11_LIVE_MARKET_PRICE_API_BRIDGE_CERTIFICATION**
   - evidence: `runtime/certifications/phase11_live_market_price_api_bridge_certification_latest.json`

⚠️ **12F_SERVICE_CHAIN_CERTIFICATION**
   - evidence: `runtime/certifications/phase12f_service_chain_certification_latest.json`

✅ **12G_SERVICE_CHAIN_DASHBOARD_CERTIFICATION**
   - evidence: `runtime/certifications/phase12g_service_chain_dashboard_certification_latest.json`

⚠️ **13F_PORTFOLIO_POSITIONS_SERVICE_CHAIN_CERTIFICATION**
   - evidence: `runtime/certifications/phase13f_portfolio_positions_service_chain_certification_latest.json`

✅ **13G_PORTFOLIO_CHAIN_DASHBOARD_CERTIFICATION**
   - evidence: `runtime/certifications/phase13g_portfolio_chain_dashboard_certification_latest.json`

⚠️ **14F_STRATEGY_DECISION_SERVICE_CHAIN_CERTIFICATION**
   - evidence: `runtime/certifications/phase14f_strategy_decision_service_chain_certification_latest.json`

✅ **14G_STRATEGY_CHAIN_DASHBOARD_CERTIFICATION**
   - evidence: `runtime/certifications/phase14g_strategy_chain_dashboard_certification_latest.json`

⚠️ **15F_RISK_GATE_SERVICE_CHAIN_CERTIFICATION**
   - evidence: `runtime/certifications/phase15f_risk_gate_service_chain_certification_latest.json`

✅ **15G_RISK_CHAIN_DASHBOARD_CERTIFICATION**
   - evidence: `runtime/certifications/phase15g_risk_chain_dashboard_certification_latest.json`

⚠️ **16_API_ROUTE_SEPARATION_CERTIFICATION**
   - evidence: `runtime/certifications/phase16_api_route_separation_certification_latest.json`

✅ **17_DASHBOARD_ROUTE_MAP_CERTIFICATION**
   - evidence: `runtime/certifications/phase17_dashboard_route_map_certification_latest.json`

✅ **18_REAL_POSITIONS_PANEL_CERTIFICATION**
   - evidence: `runtime/certifications/phase18_real_positions_panel_certification_latest.json`

⚠️ **19C_ENDPOINT_ACTIVATION_CERTIFICATION**
   - evidence: `runtime/certifications/phase19c_endpoint_activation_certification_latest.json`

✅ **19_DASHBOARD_VISUAL_LAYOUT_CERTIFICATION**
   - evidence: `runtime/certifications/phase19_dashboard_visual_layout_certification_latest.json`

⚠️ **20F_FLOATING_CHAT_WIDGET_CERTIFICATION**
   - evidence: `runtime/certifications/phase20f_floating_chat_widget_certification_latest.json`

⚠️ **21AB_CHAT_CACHE_HISTORY_CERTIFICATION**
   - evidence: `runtime/certifications/phase21ab_chat_cache_history_certification_latest.json`

⚠️ **21CD_CHAT_UX_PERSISTENT_CACHE_CERTIFICATION**
   - evidence: `runtime/certifications/phase21cd_chat_ux_persistent_cache_certification_latest.json`

⚠️ **22B_LIVE_GRAPH_VISUALIZATION_CERTIFICATION**
   - evidence: `runtime/certifications/phase22b_live_graph_visualization_certification_latest.json`

⚠️ **22_LIVE_GRAPH_TAB_CERTIFICATION**
   - evidence: `runtime/certifications/phase22_live_graph_tab_certification_latest.json`

⚠️ **23A_FRONTEND_REQUEST_NORMALIZER_CERTIFICATION**
   - evidence: `runtime/certifications/phase23a_frontend_request_normalizer_certification_latest.json`

⚠️ **23B_POLLING_GOVERNOR_CERTIFICATION**
   - evidence: `runtime/certifications/phase23b_polling_governor_certification_latest.json`

⚠️ **24A_FRONTEND_OBSERVABILITY_DASHBOARD_CERTIFICATION**
   - evidence: `runtime/certifications/phase24a_frontend_observability_dashboard_certification_latest.json`

⚠️ **24B_PERSIST_OBSERVABILITY_BACKEND_HEALTH_CERTIFICATION**
   - evidence: `runtime/certifications/phase24b_persist_observability_backend_health_certification_latest.json`

⚠️ **24C_OBSERVABILITY_EVENT_TIMELINE_CERTIFICATION**
   - evidence: `runtime/certifications/phase24c_observability_event_timeline_certification_latest.json`

✅ **24D_OBSERVABILITY_LOCK_HANDOFF_SNAPSHOT**
   - next: `Phase 25A — Dashboard Tab Shell / Layout Navigation`
   - evidence: `runtime/certifications/phase24d_observability_lock_handoff_snapshot_latest.json`

✅ **25A_DASHBOARD_TAB_SHELL_LAYOUT_NAVIGATION_CERTIFICATION**
   - evidence: `runtime/certifications/phase25a_dashboard_tab_shell_layout_navigation_certification_latest.json`

✅ **25B_TAB_LAYOUT_POLISH_CHAT_PANEL_CERTIFICATION**
   - evidence: `runtime/certifications/phase25b_tab_layout_polish_chat_panel_certification_latest.json`

✅ **25C_SPLIT_DASHBOARD_PANELS_INTO_TAB_WORKSPACES_CERTIFICATION**
   - evidence: `runtime/certifications/phase25c_split_dashboard_panels_into_tab_workspaces_certification_latest.json`

✅ **26C_CHAT_SAFETY_PROMPT_LIVE_EXECUTION_GUARD_CERTIFICATION**
   - evidence: `runtime/certifications/phase26c_chat_safety_prompt_live_execution_guard_certification_latest.json`

⚠️ **26D_FRONTEND_CHAT_RESPONSE_NORMALIZER_CERTIFICATION**
   - evidence: `runtime/certifications/phase26d_frontend_chat_response_normalizer_certification_latest.json`

✅ **26E_CHAT_METADATA_CHIPS_TYPING_ENTER_CERTIFICATION**
   - evidence: `runtime/certifications/phase26e_chat_metadata_chips_typing_enter_certification_latest.json`

⚠️ **26F_CHAT_UI_STATE_CLEANUP_METADATA_RENDERING_CERTIFICATION**
   - evidence: `runtime/certifications/phase26f_chat_ui_state_cleanup_metadata_rendering_certification_latest.json`

⚠️ **27A_STRATEGY_PROPOSAL_CAPTURE_CERTIFICATION**
   - evidence: `runtime/certifications/phase27a_strategy_proposal_capture_certification_latest.json`

⚠️ **27B_STRATEGY_CANDIDATE_REVIEW_INDEX_CERTIFICATION**
   - evidence: `runtime/certifications/phase27b_strategy_candidate_review_index_certification_latest.json`

• **27C_CANDIDATE_SANDBOX_DRY_RUN_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/sandbox_dry_run_index_latest.json`

⚠️ **27C_CANDIDATE_SANDBOX_DRY_RUN_STUB_CERTIFICATION**
   - evidence: `runtime/certifications/phase27c_candidate_sandbox_dry_run_stub_certification_latest.json`

⚠️ **27D_CANDIDATE_SANDBOX_RESULT_SCHEMA_CERTIFICATION**
   - evidence: `runtime/certifications/phase27d_candidate_sandbox_result_schema_certification_latest.json`

• **27E_CANDIDATE_SANDBOX_RESULT_STUB_GENERATOR**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_sandbox_result_stub_index_latest.json`

⚠️ **27E_CANDIDATE_SANDBOX_RESULT_STUB_GENERATOR_CERTIFICATION**
   - evidence: `runtime/certifications/phase27e_candidate_sandbox_result_stub_generator_certification_latest.json`

✅ **27F_CANDIDATE_SANDBOX_READINESS_LOCK_SNAPSHOT**
   - next: `Phase 28A — Candidate Sandbox Simulation Harness Stub`
   - evidence: `runtime/certifications/phase27f_candidate_sandbox_readiness_lock_snapshot_latest.json`

• **28A_CANDIDATE_SANDBOX_SIMULATION_HARNESS_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/simulation_harness_stub_latest.json`

✅ **28A_CANDIDATE_SANDBOX_SIMULATION_HARNESS_STUB_CERTIFICATION**
   - evidence: `runtime/certifications/phase28a_candidate_sandbox_simulation_harness_stub_certification_latest.json`

• **28B_CANDIDATE_SANDBOX_MOCK_METRICS_GENERATOR**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_sandbox_mock_metrics_index_latest.json`

✅ **28B_CANDIDATE_SANDBOX_MOCK_METRICS_GENERATOR_CERTIFICATION**
   - evidence: `runtime/certifications/phase28b_candidate_sandbox_mock_metrics_generator_certification_latest.json`

• **28C_CANDIDATE_SANDBOX_MOCK_SCORECARD**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_sandbox_mock_scorecard_latest.json`

✅ **28C_CANDIDATE_SANDBOX_MOCK_SCORECARD_CERTIFICATION**
   - evidence: `runtime/certifications/phase28c_candidate_sandbox_mock_scorecard_certification_latest.json`

• **28D_CANDIDATE_SANDBOX_EXECUTION_CONTRACT**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_sandbox_execution_contract_v1.json`

✅ **28D_CANDIDATE_SANDBOX_EXECUTION_CONTRACT_CERTIFICATION**
   - evidence: `runtime/certifications/phase28d_candidate_sandbox_execution_contract_certification_latest.json`

• **29A_HISTORICAL_REPLAY_ENGINE_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/historical_replay_engine_stub_latest.json`

✅ **29A_HISTORICAL_REPLAY_ENGINE_STUB_CERTIFICATION**
   - evidence: `runtime/certifications/phase29a_historical_replay_engine_stub_certification_latest.json`

• **29B_HISTORICAL_REPLAY_INPUT_CONTRACT**
   - evidence: `runtime/strategy_candidate_sandbox/historical_replay_input_contract_v1.json`

✅ **29B_HISTORICAL_REPLAY_INPUT_CONTRACT_CERTIFICATION**
   - evidence: `runtime/certifications/phase29b_historical_replay_input_contract_certification_latest.json`

• **29C_HISTORICAL_REPLAY_VALIDATION_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/historical_replay_validation_stub_latest.json`

✅ **29C_HISTORICAL_REPLAY_VALIDATION_STUB_CERTIFICATION**
   - evidence: `runtime/certifications/phase29c_historical_replay_validation_stub_certification_latest.json`

✅ **29D_HISTORICAL_REPLAY_READINESS_SNAPSHOT**
   - next: `Phase 29E — Historical Replay Market Data Provider Contract`
   - evidence: `runtime/certifications/phase29d_historical_replay_readiness_snapshot_latest.json`

• **29E_HISTORICAL_REPLAY_MARKET_DATA_PROVIDER_CONTRACT**
   - evidence: `runtime/strategy_candidate_sandbox/historical_replay_market_data_provider_contract_v1.json`

✅ **29E_HISTORICAL_REPLAY_MARKET_DATA_PROVIDER_CONTRACT_CERTIFICATION**
   - evidence: `runtime/certifications/phase29e_historical_replay_market_data_provider_contract_certification_latest.json`

• **29F_HISTORICAL_REPLAY_PROVIDER_ADAPTER_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/historical_replay_provider_adapter_stub_latest.json`

✅ **29F_HISTORICAL_REPLAY_PROVIDER_ADAPTER_STUB_CERTIFICATION**
   - evidence: `runtime/certifications/phase29f_historical_replay_provider_adapter_stub_certification_latest.json`

✅ **29G_HISTORICAL_REPLAY_PROVIDER_READINESS_SNAPSHOT**
   - next: `Phase 30A — Historical Replay Market Data Provider Probe`
   - evidence: `runtime/certifications/phase29g_historical_replay_provider_readiness_snapshot_latest.json`

• **30A_YFINANCE_HISTORICAL_BARS_PROVIDER_PROBE**
   - evidence: `runtime/strategy_candidate_sandbox/yfinance_historical_bars_provider_probe_latest.json`

✅ **30A_YFINANCE_HISTORICAL_BARS_PROVIDER_PROBE_CERTIFICATION**
   - evidence: `runtime/certifications/phase30a_yfinance_historical_bars_provider_probe_certification_latest.json`

✅ **30B_YFINANCE_PROVIDER_SELECTION_SNAPSHOT**
   - next: `Phase 30C — Historical Bars Contract`
   - evidence: `runtime/certifications/phase30b_yfinance_provider_selection_snapshot_latest.json`

• **30C_HISTORICAL_BARS_CONTRACT**
   - evidence: `runtime/strategy_candidate_sandbox/historical_bars_contract_v1.json`

✅ **30C_HISTORICAL_BARS_CONTRACT_CERTIFICATION**
   - evidence: `runtime/certifications/phase30c_historical_bars_contract_certification_latest.json`

• **30D_YFINANCE_HISTORICAL_BARS_ADAPTER_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_stub_latest.json`

✅ **30D_YFINANCE_HISTORICAL_BARS_ADAPTER_STUB_CERTIFICATION**
   - evidence: `runtime/certifications/phase30d_yfinance_historical_bars_adapter_stub_certification_latest.json`

• **30E_YFINANCE_HISTORICAL_BARS_ADAPTER_SHAPE_VALIDATION**
   - evidence: `runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_shape_validation_latest.json`

✅ **30E_YFINANCE_HISTORICAL_BARS_ADAPTER_SHAPE_VALIDATION_CERTIFICATION**
   - evidence: `runtime/certifications/phase30e_yfinance_historical_bars_adapter_shape_validation_certification_latest.json`

• **30F_YFINANCE_HISTORICAL_BARS_ADAPTER_WIRE_PREVIEW**
   - evidence: `runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_wire_preview_latest.json`

✅ **30F_YFINANCE_HISTORICAL_BARS_ADAPTER_WIRE_PREVIEW_CERTIFICATION**
   - evidence: `runtime/certifications/phase30f_yfinance_historical_bars_adapter_wire_preview_certification_latest.json`

• **30G_YFINANCE_HISTORICAL_BARS_ADAPTER_WIRE**
   - evidence: `runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_wire_latest.json`

✅ **30G_YFINANCE_HISTORICAL_BARS_ADAPTER_WIRE_CERTIFICATION**
   - evidence: `runtime/certifications/phase30g_yfinance_historical_bars_adapter_wire_certification_latest.json`

## Historical Replay + Metrics

✅ **31A_HISTORICAL_BARS_FETCH_VALIDATION**
   - evidence: `runtime/strategy_candidate_sandbox/31A_historical_bars_fetch_validation_latest.json`

✅ **31B_HISTORICAL_BARS_MULTI_SYMBOL_VALIDATION**
   - evidence: `runtime/strategy_candidate_sandbox/31B_historical_bars_multi_symbol_validation_latest.json`

✅ **31C_HISTORICAL_REPLAY_EXECUTOR_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/31C_historical_replay_executor_stub_latest.json`

✅ **31D_HISTORICAL_REPLAY_BAR_ITERATOR**
   - evidence: `runtime/strategy_candidate_sandbox/31D_historical_replay_bar_iterator_latest.json`

✅ **31E_FIRST_SINGLE_CANDIDATE_REPLAY_DRY_RUN**
   - evidence: `runtime/strategy_candidate_sandbox/31E_first_single_candidate_replay_dry_run_latest.json`

✅ **31F_REPLAY_METRICS_CONTRACT**
   - evidence: `runtime/strategy_candidate_sandbox/31F_replay_metrics_contract_latest.json`

✅ **32A_REAL_METRICS_GENERATION**
   - evidence: `runtime/strategy_candidate_sandbox/32A_real_metrics_generation_latest.json`

✅ **32B_CANDIDATE_SCORECARD_FROM_REPLAY_METRICS**
   - evidence: `runtime/strategy_candidate_sandbox/32B_candidate_scorecard_from_replay_metrics_latest.json`

✅ **32C_MANUAL_PROMOTION_GATE_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/32C_manual_promotion_gate_stub_latest.json`

✅ **32D_PIPELINE_ROLLUP_CERTIFICATION**
   - evidence: `runtime/strategy_candidate_sandbox/32D_pipeline_rollup_certification_latest.json`

✅ **32E_HANDOFF_BUNDLE_REFRESH**
   - Early Training Infrastructure + Bar-Only Replay Metrics Pipeline Complete
   - next: `33A_TRADE_SIMULATION_CONTRACT_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/32E_handoff_bundle_refresh_latest.json`

## Trade Simulation Contracts + Entry/Exit Disabled

✅ **33A_TRADE_SIMULATION_CONTRACT_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/33A_trade_simulation_contract_stub_latest.json`

✅ **33B_TRADE_EVENT_VALIDATION_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/33B_trade_event_validation_stub_latest.json`

✅ **33C_TRADE_SIMULATION_DRY_RUN_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/33C_trade_simulation_dry_run_stub_latest.json`

✅ **33D_ENTRY_EXIT_SIGNAL_CONTRACT_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/33D_entry_exit_signal_contract_stub_latest.json`

✅ **33E_HOLD_SIGNAL_GENERATOR_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/33E_hold_signal_generator_stub_latest.json`

✅ **33F_ENTRY_EXIT_DECISION_ENGINE_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/33F_entry_exit_decision_engine_stub_latest.json`

✅ **33G_HOLD_DECISION_TO_HOLD_EVENT_BRIDGE**
   - evidence: `runtime/strategy_candidate_sandbox/33G_hold_decision_to_hold_event_bridge_latest.json`

✅ **33H_TRADE_SIMULATION_PIPELINE_ROLLUP_CERTIFICATION**
   - next: `33I_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/33H_trade_simulation_pipeline_rollup_certification_latest.json`

✅ **33I_HANDOFF_BUNDLE_REFRESH**
   - Early Training Infrastructure + Bar-Only Metrics + Hold-Only Trade Simulation Runway Complete
   - next: `34A_ENTRY_SIGNAL_RULE_CONTRACT_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/33I_handoff_bundle_refresh_latest.json`

✅ **34A_ENTRY_SIGNAL_RULE_CONTRACT_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/34A_entry_signal_rule_contract_stub_latest.json`

✅ **34B_ENTRY_SIGNAL_RULE_VALIDATION_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/34B_entry_signal_rule_validation_stub_latest.json`

✅ **34C_ENTRY_SIGNAL_GENERATOR_DISABLED_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/34C_entry_signal_generator_disabled_stub_latest.json`

✅ **34D_ENTRY_SIGNAL_PIPELINE_ROLLUP_CERTIFICATION**
   - next: `34E_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/34D_entry_signal_pipeline_rollup_certification_latest.json`

✅ **34E_HANDOFF_BUNDLE_REFRESH**
   - Early Training Infrastructure + Hold-Only Simulation Runway + Disabled Entry Signal Pipeline Complete
   - next: `35A_EXIT_SIGNAL_RULE_CONTRACT_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/34E_handoff_bundle_refresh_latest.json`

✅ **35A_EXIT_SIGNAL_RULE_CONTRACT_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/35A_exit_signal_rule_contract_stub_latest.json`

✅ **35B_EXIT_SIGNAL_RULE_VALIDATION_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/35B_exit_signal_rule_validation_stub_latest.json`

✅ **35C_EXIT_SIGNAL_GENERATOR_DISABLED_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/35C_exit_signal_generator_disabled_stub_latest.json`

✅ **35D_EXIT_SIGNAL_PIPELINE_ROLLUP_CERTIFICATION**
   - next: `35E_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/35D_exit_signal_pipeline_rollup_certification_latest.json`

✅ **35E_STRATEGY_SANDBOX_WIREGRAPH_CERTIFICATION**
   - Strategy sandbox wiregraph certified
   - evidence: `runtime/strategy_candidate_sandbox/35E_strategy_sandbox_wiregraph_latest.json`

✅ **35F_HANDOFF_BUNDLE_REFRESH**
   - Strategy Sandbox Wiregraph Complete With Entry/Exit Generation Disabled
   - next: `36A_STRATEGY_RULE_ENABLEMENT_GATE_CONTRACT_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/35F_handoff_bundle_refresh_latest.json`

## Sandbox Gates + Dependency Trace

✅ **36A_STRATEGY_RULE_ENABLEMENT_GATE_CONTRACT_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/36A_strategy_rule_enablement_gate_contract_stub_latest.json`

✅ **36B_ENABLEMENT_GATE_VALIDATION_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/36B_enablement_gate_validation_stub_latest.json`

✅ **36C_ENABLEMENT_GATE_PIPELINE_ROLLUP_CERTIFICATION**
   - next: `36D_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/36C_enablement_gate_pipeline_rollup_certification_latest.json`

✅ **36D_HANDOFF_BUNDLE_REFRESH**
   - Strategy Rule Enablement Gate Certified (Locked)
   - next: `37A_TRADE_SIMULATION_ENABLEMENT_GATE_CONTRACT_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/36D_handoff_bundle_refresh_latest.json`

✅ **37A_TRADE_SIMULATION_ENABLEMENT_GATE_CONTRACT_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/37A_trade_simulation_enablement_gate_contract_stub_latest.json`

✅ **37B_TRADE_SIMULATION_ENABLEMENT_GATE_VALIDATION_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/37B_trade_simulation_enablement_gate_validation_stub_latest.json`

✅ **37C_TRADE_SIMULATION_ENABLEMENT_GATE_PIPELINE_ROLLUP_CERTIFICATION**
   - next: `37D_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/37C_trade_simulation_enablement_gate_pipeline_rollup_certification_latest.json`

✅ **37D_HANDOFF_BUNDLE_REFRESH**
   - Trade Simulation Enablement Gate Certified Locked
   - next: `38A_RISK_GATE_CONTRACT_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/37D_handoff_bundle_refresh_latest.json`

✅ **38A_RISK_GATE_CONTRACT_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/38A_risk_gate_contract_stub_latest.json`

✅ **38B_RISK_GATE_VALIDATION_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/38B_risk_gate_validation_stub_latest.json`

✅ **38C_RISK_GATE_PIPELINE_ROLLUP_CERTIFICATION**
   - next: `38D_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/38C_risk_gate_pipeline_rollup_certification_latest.json`

✅ **38D_HANDOFF_BUNDLE_REFRESH**
   - Risk Gate Certified Locked
   - next: `39A_MASTER_SANDBOX_GATE_WIREGRAPH_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/38D_handoff_bundle_refresh_latest.json`

✅ **39A_MASTER_SANDBOX_GATE_WIREGRAPH_REFRESH**
   - Master sandbox gate dependency wiregraph refreshed
   - evidence: `runtime/strategy_candidate_sandbox/39A_master_sandbox_gate_wiregraph_latest.json`

✅ **39B_MASTER_SANDBOX_GATE_WIREGRAPH_ROLLUP_CERTIFICATION**
   - next: `39C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/39B_master_sandbox_gate_wiregraph_rollup_certification_latest.json`

✅ **39C_HANDOFF_BUNDLE_REFRESH**
   - Master Sandbox Gate Wiregraph Certified
   - next: `40A_SANDBOX_RUNTIME_DEPENDENCY_TRACE_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/39C_handoff_bundle_refresh_latest.json`

✅ **40A_SANDBOX_RUNTIME_DEPENDENCY_TRACE_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/40A_sandbox_runtime_dependency_trace_stub_latest.json`

✅ **40B_SANDBOX_RUNTIME_DEPENDENCY_TRACE_ROLLUP_CERTIFICATION**
   - next: `40C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/40B_sandbox_runtime_dependency_trace_rollup_certification_latest.json`

✅ **40C_HANDOFF_BUNDLE_REFRESH**
   - Sandbox Runtime Dependency Trace Certified Locked
   - next: `41A_SAFE_READ_ONLY_ARCHITECTURE_INSPECTOR_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/40C_handoff_bundle_refresh_latest.json`

## Qwen Read-Only Context + Response Validation

✅ **41A_SAFE_READ_ONLY_ARCHITECTURE_INSPECTOR_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/41A_safe_read_only_architecture_inspector_stub_latest.json`

✅ **41B_SAFE_READ_ONLY_ARCHITECTURE_INSPECTOR_ROLLUP_CERTIFICATION**
   - next: `41C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/41B_safe_read_only_architecture_inspector_rollup_certification_latest.json`

✅ **41C_HANDOFF_BUNDLE_REFRESH**
   - Read-Only Architecture Inspector Certified
   - next: `42A_QWEN_READ_ONLY_ARCHITECTURE_CONTEXT_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/41C_handoff_bundle_refresh_latest.json`

✅ **42A_QWEN_READ_ONLY_ARCHITECTURE_CONTEXT_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/42A_qwen_read_only_architecture_context_stub_latest.json`

✅ **42B_QWEN_READ_ONLY_ARCHITECTURE_CONTEXT_ROLLUP_CERTIFICATION**
   - next: `42C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/42B_qwen_read_only_architecture_context_rollup_certification_latest.json`

✅ **42C_HANDOFF_BUNDLE_REFRESH**
   - Qwen Read-Only Architecture Context Certified
   - next: `43A_QWEN_CONTEXT_RESPONSE_CONTRACT_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/42C_handoff_bundle_refresh_latest.json`

✅ **43A_QWEN_CONTEXT_RESPONSE_CONTRACT_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/43A_qwen_context_response_contract_stub_latest.json`

✅ **43B_QWEN_CONTEXT_RESPONSE_CONTRACT_ROLLUP_CERTIFICATION**
   - next: `43C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/43B_qwen_context_response_contract_rollup_certification_latest.json`

✅ **43C_HANDOFF_BUNDLE_REFRESH**
   - Qwen Read-Only Response Contract Certified
   - next: `44A_QWEN_READ_ONLY_RESPONSE_SAMPLE_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/43C_handoff_bundle_refresh_latest.json`

✅ **44A_QWEN_READ_ONLY_RESPONSE_SAMPLE_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/44A_qwen_read_only_response_sample_stub_latest.json`

✅ **44B_QWEN_READ_ONLY_RESPONSE_SAMPLE_ROLLUP_CERTIFICATION**
   - next: `44C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/44B_qwen_read_only_response_sample_rollup_certification_latest.json`

✅ **44C_HANDOFF_BUNDLE_REFRESH**
   - Qwen Read-Only Response Sample Certified
   - next: `45A_QWEN_READ_ONLY_ARCHITECTURE_SUMMARY_GATE_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/44C_handoff_bundle_refresh_latest.json`

✅ **45A_QWEN_READ_ONLY_ARCHITECTURE_SUMMARY_GATE_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/45A_qwen_read_only_architecture_summary_gate_stub_latest.json`

✅ **45B_QWEN_READ_ONLY_ARCHITECTURE_SUMMARY_GATE_ROLLUP_CERTIFICATION**
   - next: `45C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/45B_qwen_read_only_architecture_summary_gate_rollup_certification_latest.json`

✅ **45C_HANDOFF_BUNDLE_REFRESH**
   - Qwen Read-Only Architecture Summary Gate Certified
   - next: `46A_QWEN_READ_ONLY_MISSING_CONTEXT_DETECTOR_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/45C_handoff_bundle_refresh_latest.json`

✅ **46A_QWEN_READ_ONLY_MISSING_CONTEXT_DETECTOR_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/46A_qwen_read_only_missing_context_detector_stub_latest.json`

✅ **46B_QWEN_READ_ONLY_MISSING_CONTEXT_DETECTOR_ROLLUP_CERTIFICATION**
   - next: `46C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/46B_qwen_read_only_missing_context_detector_rollup_certification_latest.json`

✅ **46C_HANDOFF_BUNDLE_REFRESH**
   - Qwen Read-Only Missing Context Detector Certified
   - next: `47A_QWEN_READ_ONLY_RECOMMENDATION_FILTER_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/46C_handoff_bundle_refresh_latest.json`

✅ **47A_QWEN_READ_ONLY_RECOMMENDATION_FILTER_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/47A_qwen_read_only_recommendation_filter_stub_latest.json`

✅ **47B_QWEN_READ_ONLY_RECOMMENDATION_FILTER_ROLLUP_CERTIFICATION**
   - next: `47C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/47B_qwen_read_only_recommendation_filter_rollup_certification_latest.json`

✅ **47C_HANDOFF_BUNDLE_REFRESH**
   - Qwen Read-Only Recommendation Filter Certified
   - next: `48A_QWEN_READ_ONLY_RESPONSE_VALIDATOR_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/47C_handoff_bundle_refresh_latest.json`

✅ **48A_QWEN_READ_ONLY_RESPONSE_VALIDATOR_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/48A_qwen_read_only_response_validator_stub_latest.json`

✅ **48B_QWEN_READ_ONLY_RESPONSE_VALIDATOR_ROLLUP_CERTIFICATION**
   - next: `48C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/48B_qwen_read_only_response_validator_rollup_certification_latest.json`

✅ **48C_HANDOFF_BUNDLE_REFRESH**
   - Qwen Read-Only Response Validator Certified
   - next: `49A_QWEN_READ_ONLY_ARCHITECTURE_SESSION_CONTRACT_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/48C_handoff_bundle_refresh_latest.json`

## Qwen Session / Bridge / Loop / State Machine

✅ **49A_QWEN_READ_ONLY_ARCHITECTURE_SESSION_CONTRACT_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/49A_qwen_read_only_architecture_session_contract_stub_latest.json`

✅ **49B_QWEN_READ_ONLY_ARCHITECTURE_SESSION_CONTRACT_ROLLUP_CERTIFICATION**
   - next: `49C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/49B_qwen_read_only_architecture_session_contract_rollup_certification_latest.json`

✅ **49C_HANDOFF_BUNDLE_REFRESH**
   - Qwen Read-Only Architecture Session Contract Certified
   - next: `50A_QWEN_READ_ONLY_SESSION_RESPONSE_BRIDGE_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/49C_handoff_bundle_refresh_latest.json`

✅ **50A_QWEN_READ_ONLY_SESSION_RESPONSE_BRIDGE_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/50A_qwen_read_only_session_response_bridge_stub_latest.json`

✅ **50B_QWEN_READ_ONLY_SESSION_RESPONSE_BRIDGE_ROLLUP_CERTIFICATION**
   - next: `50C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/50B_qwen_read_only_session_response_bridge_rollup_certification_latest.json`

✅ **50C_HANDOFF_BUNDLE_REFRESH**
   - Qwen Read-Only Session Response Bridge Certified
   - next: `51A_QWEN_READ_ONLY_ARCHITECTURE_LOOP_BOUNDARY_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/50C_handoff_bundle_refresh_latest.json`

✅ **51A_QWEN_READ_ONLY_ARCHITECTURE_LOOP_BOUNDARY_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/51A_qwen_read_only_architecture_loop_boundary_stub_latest.json`

✅ **51B_QWEN_READ_ONLY_ARCHITECTURE_LOOP_BOUNDARY_ROLLUP_CERTIFICATION**
   - next: `51C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/51B_qwen_read_only_architecture_loop_boundary_rollup_certification_latest.json`

✅ **51C_HANDOFF_BUNDLE_REFRESH**
   - Qwen Read-Only Architecture Loop Boundary Certified
   - next: `52A_QWEN_READ_ONLY_FINAL_GUARDRAIL_SUMMARY_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/51C_handoff_bundle_refresh_latest.json`

✅ **52A_QWEN_READ_ONLY_FINAL_GUARDRAIL_SUMMARY_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/52A_qwen_read_only_final_guardrail_summary_stub_latest.json`

✅ **52B_QWEN_READ_ONLY_FINAL_GUARDRAIL_SUMMARY_ROLLUP_CERTIFICATION**
   - next: `52C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/52B_qwen_read_only_final_guardrail_summary_rollup_certification_latest.json`

✅ **52C_HANDOFF_BUNDLE_REFRESH**
   - Qwen Read-Only Final Guardrail Summary Certified
   - next: `53A_QWEN_READ_ONLY_HANDOFF_FREEZE_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/52C_handoff_bundle_refresh_latest.json`

✅ **53A_QWEN_READ_ONLY_HANDOFF_FREEZE_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/53A_qwen_read_only_handoff_freeze_stub_latest.json`

✅ **53B_QWEN_READ_ONLY_HANDOFF_FREEZE_ROLLUP_CERTIFICATION**
   - next: `53C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/53B_qwen_read_only_handoff_freeze_rollup_certification_latest.json`

✅ **53C_HANDOFF_BUNDLE_REFRESH**
   - Qwen Read-Only Handoff Freeze Certified
   - next: `54A_QWEN_READ_ONLY_HANDOFF_EXPORT_SUMMARY_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/53C_handoff_bundle_refresh_latest.json`

✅ **54A_QWEN_READ_ONLY_HANDOFF_EXPORT_SUMMARY_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/54A_qwen_read_only_handoff_export_summary_stub_latest.json`

✅ **54B_QWEN_READ_ONLY_HANDOFF_EXPORT_SUMMARY_ROLLUP_CERTIFICATION**
   - next: `54C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/54B_qwen_read_only_handoff_export_summary_rollup_certification_latest.json`

✅ **54C_HANDOFF_BUNDLE_REFRESH**
   - Qwen Read-Only Handoff Export Summary Certified
   - next: `55A_QWEN_READ_ONLY_ARCHITECTURE_STATE_MACHINE_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/54C_handoff_bundle_refresh_latest.json`

✅ **55A_QWEN_READ_ONLY_ARCHITECTURE_STATE_MACHINE_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/55A_qwen_read_only_architecture_state_machine_stub_latest.json`

✅ **55B_QWEN_READ_ONLY_ARCHITECTURE_STATE_MACHINE_ROLLUP_CERTIFICATION**
   - next: `55C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/55B_qwen_read_only_architecture_state_machine_rollup_certification_latest.json`

✅ **55C_HANDOFF_BUNDLE_REFRESH**
   - next: `56A_QWEN_READ_ONLY_ARCHITECTURE_POLICY_MAP_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/55C_handoff_bundle_refresh_latest.json`

## Qwen Policy Matrix + Context Package

✅ **56A_QWEN_READ_ONLY_ARCHITECTURE_POLICY_MAP_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/56A_qwen_read_only_architecture_policy_map_stub_latest.json`

✅ **56B_QWEN_READ_ONLY_ARCHITECTURE_POLICY_MAP_ROLLUP_CERTIFICATION**
   - next: `56C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/56B_qwen_read_only_architecture_policy_map_rollup_certification_latest.json`

✅ **56C_HANDOFF_BUNDLE_REFRESH**
   - next: `57A_QWEN_READ_ONLY_POLICY_BOUNDARY_MATRIX_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/56C_handoff_bundle_refresh_latest.json`

✅ **57A_QWEN_READ_ONLY_POLICY_BOUNDARY_MATRIX_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/57A_qwen_read_only_policy_boundary_matrix_stub_latest.json`

✅ **57B_QWEN_READ_ONLY_POLICY_BOUNDARY_MATRIX_ROLLUP_CERTIFICATION**
   - next: `57C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/57B_qwen_read_only_policy_boundary_matrix_rollup_certification_latest.json`

✅ **57C_HANDOFF_BUNDLE_REFRESH**
   - next: `58A_QWEN_READ_ONLY_FINAL_CONTEXT_PACKAGE_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/57C_handoff_bundle_refresh_latest.json`

✅ **58A_QWEN_READ_ONLY_FINAL_CONTEXT_PACKAGE_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/58A_qwen_read_only_final_context_package_stub_latest.json`

✅ **58B_QWEN_READ_ONLY_FINAL_CONTEXT_PACKAGE_ROLLUP_CERTIFICATION**
   - next: `58C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/58B_qwen_read_only_final_context_package_rollup_certification_latest.json`

✅ **58C_HANDOFF_BUNDLE_REFRESH**
   - next: `59A_QWEN_READ_ONLY_FINAL_HANDOFF_CERTIFICATION_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/58C_handoff_bundle_refresh_latest.json`

## Terminal Freeze + Archive

✅ **59A_QWEN_READ_ONLY_FINAL_HANDOFF_CERTIFICATION_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/59A_qwen_read_only_final_handoff_certification_stub_latest.json`

✅ **59B_QWEN_READ_ONLY_FINAL_HANDOFF_CERTIFICATION_ROLLUP_CERTIFICATION**
   - next: `59C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/59B_qwen_read_only_final_handoff_certification_rollup_certification_latest.json`

✅ **59C_HANDOFF_BUNDLE_REFRESH**
   - next: `60A_QWEN_READ_ONLY_TERMINAL_FREEZE_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/59C_handoff_bundle_refresh_latest.json`

✅ **60A_QWEN_READ_ONLY_TERMINAL_FREEZE_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/60A_qwen_read_only_terminal_freeze_stub_latest.json`

✅ **60B_QWEN_READ_ONLY_TERMINAL_FREEZE_ROLLUP_CERTIFICATION**
   - next: `60C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/60B_qwen_read_only_terminal_freeze_rollup_certification_latest.json`

✅ **60C_HANDOFF_BUNDLE_REFRESH**
   - next: `HANDOFF_TO_NEW_CHAT_OR_ARCHIVE_ONLY`
   - evidence: `runtime/strategy_candidate_sandbox/60C_handoff_bundle_refresh_latest.json`

✅ **61A_ARCHIVE_OR_NEW_CHAT_HANDOFF_SUMMARY**
   - evidence: `runtime/strategy_candidate_sandbox/61A_archive_or_new_chat_handoff_summary_latest.json`

## Other

• **candidate_sandbox_result_example_latest**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_sandbox_result_example_latest.json`

• **candidate_20260706_144431_8a545b3c_mock_metrics**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_144431_8a545b3c_mock_metrics.json`

• **candidate_20260706_144431_8a545b3c_mock_scorecard**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_144431_8a545b3c_mock_scorecard.json`

• **candidate_20260706_144431_8a545b3c_sandbox_result_stub**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_144431_8a545b3c_sandbox_result_stub.json`

• **candidate_20260706_144431_8a545b3c_sandbox_stub**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_144431_8a545b3c_sandbox_stub.json`

• **candidate_20260706_145350_816903d1_mock_metrics**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_145350_816903d1_mock_metrics.json`

• **candidate_20260706_145350_816903d1_mock_scorecard**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_145350_816903d1_mock_scorecard.json`

• **candidate_20260706_145350_816903d1_sandbox_result_stub**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_145350_816903d1_sandbox_result_stub.json`

• **candidate_20260706_145350_816903d1_sandbox_stub**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_145350_816903d1_sandbox_stub.json`

• **candidate_20260706_150540_4fc7b8ab_mock_metrics**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_150540_4fc7b8ab_mock_metrics.json`

• **candidate_20260706_150540_4fc7b8ab_mock_scorecard**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_150540_4fc7b8ab_mock_scorecard.json`

• **candidate_20260706_150540_4fc7b8ab_sandbox_result_stub**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_150540_4fc7b8ab_sandbox_result_stub.json`

• **candidate_20260706_150540_4fc7b8ab_sandbox_stub**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_150540_4fc7b8ab_sandbox_stub.json`

• **candidate_20260706_151330_9f852272_mock_metrics**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_151330_9f852272_mock_metrics.json`

• **candidate_20260706_151330_9f852272_mock_scorecard**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_151330_9f852272_mock_scorecard.json`

• **candidate_20260706_151330_9f852272_sandbox_result_stub**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_151330_9f852272_sandbox_result_stub.json`

• **candidate_20260706_151330_9f852272_sandbox_stub**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_151330_9f852272_sandbox_stub.json`

• **candidate_20260706_152354_e2129e4e_mock_metrics**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_152354_e2129e4e_mock_metrics.json`

• **candidate_20260706_152354_e2129e4e_mock_scorecard**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_152354_e2129e4e_mock_scorecard.json`

• **candidate_20260706_152354_e2129e4e_sandbox_result_stub**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_152354_e2129e4e_sandbox_result_stub.json`

• **candidate_20260706_152354_e2129e4e_sandbox_stub**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_152354_e2129e4e_sandbox_stub.json`

• **candidate_20260706_152930_73031c40_mock_metrics**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_152930_73031c40_mock_metrics.json`

• **candidate_20260706_152930_73031c40_mock_scorecard**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_152930_73031c40_mock_scorecard.json`

• **candidate_20260706_152930_73031c40_sandbox_result_stub**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_152930_73031c40_sandbox_result_stub.json`

• **candidate_20260706_152930_73031c40_sandbox_stub**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_152930_73031c40_sandbox_stub.json`


# Import Dependency Atlas

```json
{
  "chat_public": [
    "chat_public"
  ],
  "execution": [
    "journal_ledger",
    "market_data",
    "portfolio",
    "risk",
    "strategy"
  ],
  "learning_research": [
    "db_model",
    "journal_ledger"
  ],
  "market_data": [
    "db_model",
    "journal_ledger",
    "market_data"
  ],
  "phase_scripts": [
    "market_data",
    "strategy_candidate_sandbox"
  ],
  "portfolio": [
    "execution",
    "journal_ledger",
    "market_data"
  ],
  "risk": [
    "journal_ledger",
    "risk"
  ],
  "root_or_misc": [
    "chat_public",
    "events",
    "execution",
    "journal_ledger",
    "market_data",
    "portfolio",
    "risk",
    "strategy",
    "wolfden_ai"
  ],
  "strategy": [
    "market_data",
    "portfolio",
    "strategy"
  ],
  "strategy_candidate_sandbox": [
    "strategy_candidate_sandbox"
  ],
  "wolfden_ai": [
    "execution",
    "journal_ledger",
    "risk",
    "strategy"
  ]
}
```


# Future Workstream Order

1. LLM orchestration architecture.
2. Permission request model.
3. Sandbox runtime activation plan.
4. Candidate lifecycle hardening.
5. Learning and promotion approval chain.
6. Broker/live execution safety model.

Do not continue the Qwen read-only certification chain. It is terminal-frozen.

---

# 4. [Reference] Master Architecture Handoff

Source: `handoff/MASTER_ARCHITECTURE_HANDOFF.md`

# NeuroVest Master Architecture Handoff

Generated: 2026-07-07T02:55:08.948364+00:00  
Mode: READ ONLY  
Controller: 62A_MASTER_ARCHITECTURE_HANDOFF_CONTROLLER

---

## 1. Executive Summary

NeuroVest is a layered fintech/trading research system being built with strict safety separation.

This handoff was generated by scanning the repository, audit artifacts, runtime artifacts, and certified phase outputs. It is intended to be used as the starting point for a new chat or developer handoff.

The latest confirmed archive checkpoint is:

```text
61A_ARCHIVE_OR_NEW_CHAT_HANDOFF_SUMMARY

The Qwen read-only certification workstream is terminal-frozen. It proves Qwen may act only as a read-only architecture observer/summarizer. It does not create runtime execution, source mutation, learning, promotion, broker execution, live trading, autonomous phase execution, or recursive execution.

2. Repository Statistics
{
  "total_files": 827,
  "total_dirs": 73,
  "python_files": 437,
  "typescript_files": 20,
  "json_files": 296,
  "markdown_files": 29,
  "scripts": 280,
  "tests": 231,
  "largest_files": [
    {
      "file": ".aider.tags.cache.v4/cache.db-wal",
      "bytes": 4124152
    },
    {
      "file": "runtime/graph_history/events.jsonl",
      "bytes": 2423897
    },
    {
      "file": "topology_wire_graph.png",
      "bytes": 1620490
    },
    {
      "file": "runtime/market_warehouse/history/AAPL_history.csv",
      "bytes": 1561584
    },
    {
      "file": "runtime/market_warehouse/history/MSFT_history.csv",
      "bytes": 1284408
    },
    {
      "file": "runtime/market_warehouse/history/TD_TO_history.csv",
      "bytes": 997917
    },
    {
      "file": "runtime/market_warehouse/history/RY_TO_history.csv",
      "bytes": 995607
    },
    {
      "file": "runtime/market_warehouse/history/NVDA_history.csv",
      "bytes": 956580
    },
    {
      "file": "cursor.AppImage",
      "bytes": 690286
    },
    {
      "file": "domain_runtime_overlay_graph.png",
      "bytes": 566611
    },
    {
      "file": "runtime/market_warehouse/history/TSLA_history.csv",
      "bytes": 539919
    },
    {
      "file": "runtime/market_warehouse/history/VFV_TO_history.csv",
      "bytes": 452228
    },
    {
      "file": "runtime/market_warehouse/history/VUN_TO_history.csv",
      "bytes": 426620
    },
    {
      "file": "domain_subsystem_graph.png",
      "bytes": 318287
    },
    {
      "file": "topology_wire_graph_canonical.png",
      "bytes": 308830
    },
    {
      "file": ".aider.chat.history.md",
      "bytes": 294388
    },
    {
      "file": "runtime/repo_memory/repo_index_v2.json",
      "bytes": 250378
    },
    {
      "file": ".aider.tags.cache.v4/cache.db",
      "bytes": 237568
    },
    {
      "file": "frontend/package-lock.json",
      "bytes": 221605
    },
    {
      "file": "neuro_cli_file_inspection.json",
      "bytes": 71718
    },
    {
      "file": "runtime/repo_memory/dependency_graph_v1.json",
      "bytes": 64283
    },
    {
      "file": "runtime/handoff_snapshot/neurovest_training_handoff_bundle_latest.json",
      "bytes": 59780
    },
    {
      "file": "frontend/app/page.tsx",
      "bytes": 35077
    },
    {
      "file": ".aider.input.history",
      "bytes": 33797
    },
    {
      "file": ".aider.tags.cache.v4/cache.db-shm",
      "bytes": 32768
    },
    {
      "file": "runtime/certifications/phase6b_dependency_validation_certification_latest.json",
      "bytes": 32429
    },
    {
      "file": "runtime/repo_memory/component_overlay_v1.json",
      "bytes": 30215
    },
    {
      "file": "runtime/handoff_snapshot/file_manifest_latest.txt",
      "bytes": 28495
    },
    {
      "file": "runtime/repo_memory/repo_index.json",
      "bytes": 27818
    },
    {
      "file": "runtime/handoff_snapshot/topology_tree_latest.txt",
      "bytes": 26518
    }
  ],
  "top_level": {
    "OUTPUT": 1,
    "ARCHITECTURE_REPAIR_PLAN.json": 1,
    "TOPOLOGY_NORMALIZED_STATE.json": 1,
    "ARCH_GOVERNANCE.md": 1,
    "fix_phase9_self_fingerprint.sh": 1,
    "TOPOLOGY_STATE.json": 1,
    "topology_wire_graph.png": 1,
    "neurovest_repo_context.md": 1,
    "Directory Structure": 1,
    "ORPHAN_RESOLUTION_PLAN.json": 1,
    "topology_wire_graph_canonical.png": 1,
    ".env.example": 1,
    "domain_subsystem_graph.png": 1,
    "generate_wire_graph.py": 1,
    "neuro_health.sh": 1,
    "neuro_cli_file_inspection.json": 1,
    ".aider.input.history": 1,
    "FINAL_ARCHITECTURE_STATE.json": 1,
    "system_tree.txt": 1,
    "docker-compose.yml": 1,
    "ARCH_ENFORCEMENT_REPORT.json": 1,
    "spine_mvp_full.sh": 1,
    "pytest.ini": 1,
    ".gitignore": 1,
    "$OUTPUT": 1,
    "SERVICE_RELOCATION_PLAN_RECONCILED.json": 1,
    ".env": 1,
    "domain_runtime_overlay_graph.png": 1,
    ".aider.chat.history.md": 1,
    "cursor.AppImage": 1,
    "neuro": 1,
    "neuro_cli.py": 1,
    "neuro_engineer.py": 1,
    "SERVICE_RELOCATION_PLAN.json": 1,
    "architecture_backup": 1,
    "scripts": 279,
    "backend": 157,
    ".aider.tags.cache.v4": 3,
    "frontend": 36,
    "backups": 1,
    "runtime": 315,
    ".github": 1
  }
}
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

- auth: 4 files
- backend_uncategorized: 27 files
- chat: 43 files
- execution: 19 files
- frontend: 28 files
- journal: 4 files
- learning: 9 files
- market_data: 15 files
- notification: 2 files
- portfolio: 19 files
- research: 2 files
- risk: 22 files
- runtime_artifacts: 103 files
- snaptrade: 7 files
- strategy: 247 files
- unknown: 269 files
- wolfden: 7 files
6. Runtime Node Map
NEUROVEST SYSTEM NODE MAP

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

7. Runtime State Machine
QWEN READ-ONLY STATE MACHINE

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

8. Dependency Graph
HIGH-LEVEL DEPENDENCY GRAPH

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

9. Certification Timeline

Certified artifacts found: 110
Uncertified or historical artifacts found: 43

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

---

# 5. [Reference] Index

Source: `handoff/project_bible/INDEX.md`

# Project Bible Index

- PROJECT_BIBLE.md
- PROJECT_BIBLE.json
- EXECUTIVE_SUMMARY.md
- NODE_MAP.md
- DEPENDENCY_GRAPH.md
- DATA_FLOW.md
- QWEN_READ_ONLY_ARCHITECTURE.md
- DEVELOPER_RULEBOOK.md
- ROADMAP.md
- GLOSSARY.md
- TRACEABILITY_INDEX.md

---

# 6. [Repository Topology] Repository Tree

Source: `handoff/repository_tree.txt`

```text
./
├── .aider.tags.cache.v4/
│   ├── cache.db
│   ├── cache.db-shm
│   └── cache.db-wal
├── .github/
│   └── workflows/
│       └── architecture_ci.yml
├── architecture_backup/
│   └── dashboard_service.py
├── backend/
│   ├── app/
│   │   ├── analysis/
│   │   │   └── architecture.py
│   │   ├── api/
│   │   │   └── graph_ws.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── cognitive_event_bus.py
│   │   │   ├── cognitive_graph_state.py
│   │   │   ├── cognitive_nodes.py
│   │   │   ├── cognitive_types.py
│   │   │   ├── config.py
│   │   │   ├── global_firewall_v1.py
│   │   │   └── runtime_firewall_v1.py
│   │   ├── models/
│   │   ├── routers/
│   │   │   └── __init__.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── dashboard.py
│   │   ├── services/
│   │   │   └── __init__.py
│   │   ├── snaptrade/
│   │   │   └── executions/
│   │   ├── stacks/
│   │   │   ├── auth_identity/
│   │   │   ├── chat_public/
│   │   │   ├── db_model/
│   │   │   ├── events/
│   │   │   ├── execution/
│   │   │   ├── journal_ledger/
│   │   │   ├── learning_research/
│   │   │   ├── market_data/
│   │   │   ├── notification/
│   │   │   ├── portfolio/
│   │   │   ├── risk/
│   │   │   ├── snaptrade/
│   │   │   ├── strategy/
│   │   │   ├── strategy_candidate_sandbox/
│   │   │   ├── wolfden_ai/
│   │   │   ├── __init__.py
│   │   │   └── registry.json
│   │   ├── test/
│   │   │   ├── test_neuro_repo_companion.py
│   │   │   └── test_trading_pipeline.py
│   │   ├── __init__.py
│   │   └── main.py
│   ├── scripts/
│   │   └── backup_db.sh
│   ├── __init__.py
│   └── requirements.txt
├── backups/
│   └── neurovest_backup_20260703_215801.sql.gz
├── frontend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   ├── favicon.ico
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── public/
│   │   ├── file.svg
│   │   ├── globe.svg
│   │   ├── next.svg
│   │   ├── vercel.svg
│   │   └── window.svg
│   ├── services/
│   │   ├── backendHealthService.ts
│   │   ├── chatService.ts
│   │   ├── graphService.ts
│   │   ├── marketService.ts
│   │   ├── observabilityTimelineService.ts
│   │   ├── portfolioService.ts
│   │   ├── requestNormalizer.ts
│   │   ├── requestObservability.ts
│   │   ├── riskService.ts
│   │   └── strategyService.ts
│   ├── .gitignore
│   ├── AGENTS.md
│   ├── CLAUDE.md
│   ├── eslint.config.mjs
│   ├── next-env.d.ts
│   ├── next.config.ts
│   ├── package-lock.json
│   ├── package.json
│   ├── postcss.config.mjs
│   ├── README.md
│   └── tsconfig.json
├── handoff/
├── runtime/
│   ├── certifications/
│   │   ├── phase10_domain_subsystem_visualization_certification_latest.json
│   │   ├── phase10c_runtime_flow_overlay_certification_latest.json
│   │   ├── phase10d_runtime_static_dependency_diff_certification_latest.json
│   │   ├── phase10e_diff_classification_certification_latest.json
│   │   ├── phase10f_architecture_drift_watch_certification_latest.json
│   │   ├── phase10g_architecture_drift_dashboard_certification_latest.json
│   │   ├── phase10h_architecture_dashboard_command_certification_latest.json
│   │   ├── phase11_live_market_price_api_bridge_certification_latest.json
│   │   ├── phase11b_frontend_live_price_card_certification_latest.json
│   │   ├── phase11c_frontend_polling_api_cleanup_certification_latest.json
│   │   ├── phase11d_next_api_proxy_live_price_certification_latest.json
│   │   ├── phase11e_frontend_build_type_certification_latest.json
│   │   ├── phase11f_frontend_type_lint_repair_certification_latest.json
│   │   ├── phase11g_live_market_dashboard_expansion_certification_latest.json
│   │   ├── phase12f_service_chain_certification_latest.json
│   │   ├── phase12g_service_chain_dashboard_certification_latest.json
│   │   ├── phase13f_portfolio_positions_service_chain_certification_latest.json
│   │   ├── phase13g_portfolio_chain_dashboard_certification_latest.json
│   │   ├── phase14f_strategy_decision_service_chain_certification_latest.json
│   │   ├── phase14g_strategy_chain_dashboard_certification_latest.json
│   │   ├── phase15f_risk_gate_service_chain_certification_latest.json
│   │   ├── phase15g_risk_chain_dashboard_certification_latest.json
│   │   ├── phase16_api_route_separation_certification_latest.json
│   │   ├── phase17_dashboard_route_map_certification_latest.json
│   │   ├── phase18_real_positions_panel_certification_latest.json
│   │   ├── phase19_dashboard_visual_layout_certification_latest.json
│   │   ├── phase19c_endpoint_activation_certification_latest.json
│   │   ├── phase20f_floating_chat_widget_certification_latest.json
│   │   ├── phase21ab_chat_cache_history_certification_latest.json
│   │   ├── phase21cd_chat_ux_persistent_cache_certification_latest.json
│   │   ├── phase22_live_graph_tab_certification_latest.json
│   │   ├── phase22b_live_graph_visualization_certification_latest.json
│   │   ├── phase23a_frontend_request_normalizer_certification_latest.json
│   │   ├── phase23b_polling_governor_certification_latest.json
│   │   ├── phase24a_frontend_observability_dashboard_certification_latest.json
│   │   ├── phase24b_persist_observability_backend_health_certification_latest.json
│   │   ├── phase24c_observability_event_timeline_certification_latest.json
│   │   ├── phase24d_observability_lock_handoff_snapshot_latest.json
│   │   ├── phase25a_dashboard_tab_shell_layout_navigation_certification_latest.json
│   │   ├── phase25b_tab_layout_polish_chat_panel_certification_latest.json
│   │   ├── phase25c_split_dashboard_panels_into_tab_workspaces_certification_latest.json
│   │   ├── phase26c_chat_safety_prompt_live_execution_guard_certification_latest.json
│   │   ├── phase26d_frontend_chat_response_normalizer_certification_latest.json
│   │   ├── phase26e_chat_metadata_chips_typing_enter_certification_latest.json
│   │   ├── phase26f_chat_ui_state_cleanup_metadata_rendering_certification_latest.json
│   │   ├── phase27a_strategy_proposal_capture_certification_latest.json
│   │   ├── phase27b_strategy_candidate_review_index_certification_latest.json
│   │   ├── phase27c_candidate_sandbox_dry_run_stub_certification_latest.json
│   │   ├── phase27d_candidate_sandbox_result_schema_certification_latest.json
│   │   ├── phase27e_candidate_sandbox_result_stub_generator_certification_latest.json
│   │   ├── phase27f_candidate_sandbox_readiness_lock_snapshot_latest.json
│   │   ├── phase28a_candidate_sandbox_simulation_harness_stub_certification_latest.json
│   │   ├── phase28b_candidate_sandbox_mock_metrics_generator_certification_latest.json
│   │   ├── phase28c_candidate_sandbox_mock_scorecard_certification_latest.json
│   │   ├── phase28d_candidate_sandbox_execution_contract_certification_latest.json
│   │   ├── phase29a_historical_replay_engine_stub_certification_latest.json
│   │   ├── phase29b_historical_replay_input_contract_certification_latest.json
│   │   ├── phase29c_historical_replay_validation_stub_certification_latest.json
│   │   ├── phase29d_historical_replay_readiness_snapshot_latest.json
│   │   ├── phase29e_historical_replay_market_data_provider_contract_certification_latest.json
│   │   ├── phase29f_historical_replay_provider_adapter_stub_certification_latest.json
│   │   ├── phase29g_historical_replay_provider_readiness_snapshot_latest.json
│   │   ├── phase30a_yfinance_historical_bars_provider_probe_certification_latest.json
│   │   ├── phase30b_yfinance_provider_selection_snapshot_latest.json
│   │   ├── phase30c_historical_bars_contract_certification_latest.json
│   │   ├── phase30d_yfinance_historical_bars_adapter_stub_certification_latest.json
│   │   ├── phase30e_yfinance_historical_bars_adapter_shape_validation_certification_latest.json
│   │   ├── phase30f_yfinance_historical_bars_adapter_wire_preview_certification_latest.json
│   │   ├── phase30g_yfinance_historical_bars_adapter_wire_certification_latest.json
│   │   ├── phase3m_graph_certification_latest.json
│   │   ├── phase4g_repo_memory_certification_latest.json
│   │   ├── phase5c_repo_memory_certification_v2_latest.json
│   │   ├── phase6b_dependency_validation_certification_latest.json
│   │   ├── phase6d_dependency_graph_certification_latest.json
│   │   ├── phase7g_graph_visualization_certification_latest.json
│   │   ├── phase8c_neuro_cli_hotspots_certification_latest.json
│   │   ├── phase9e_canonical_graph_certification_latest.json
│   │   └── phase9m_canonical_graph_certification_v2_latest.json
│   ├── graph_history/
│   │   ├── current_snapshot.json
│   │   └── events.jsonl
│   ├── handoff_snapshot/
│   │   ├── file_manifest_latest.txt
│   │   ├── live_graph_validate_latest.json
│   │   ├── neurovest_training_handoff_bundle_latest.json
│   │   ├── simulate_trade_guard_latest.json
│   │   └── topology_tree_latest.txt
│   ├── market_warehouse/
│   │   ├── history/
│   │   │   ├── AAPL_history.csv
│   │   │   ├── MSFT_history.csv
│   │   │   ├── NVDA_history.csv
│   │   │   ├── RY_TO_history.csv
│   │   │   ├── TD_TO_history.csv
│   │   │   ├── TSLA_history.csv
│   │   │   ├── VFV_TO_history.csv
│   │   │   └── VUN_TO_history.csv
│   │   ├── live/
│   │   │   ├── AAPL_live.json
│   │   │   ├── MSFT_live.json
│   │   │   ├── NVDA_live.json
│   │   │   ├── RY_TO_live.json
│   │   │   ├── TD_TO_live.json
│   │   │   ├── TSLA_live.json
│   │   │   ├── VFV_TO_live.json
│   │   │   └── VUN_TO_live.json
│   │   └── symbol_registry.json
│   ├── repo_memory/
│   │   ├── architecture_drift_dashboard_v1.json
│   │   ├── architecture_drift_dashboard_v1.txt
│   │   ├── canonical_layer_graph_v1.json
│   │   ├── chat_service_chain_graph_v1.json
│   │   ├── component_overlay_v1.json
│   │   ├── dashboard_route_map_v1.json
│   │   ├── dependency_graph_v1.json
│   │   ├── dependency_topology_overlay_v1.json
│   │   ├── domain_subsystem_graph_v1.json
│   │   ├── phase4c_loose_root_duplicate_quarantine_plan_latest.json
│   │   ├── phase4d_root_shadow_diff_report_latest.json
│   │   ├── phase4d_root_shadow_diff_report_latest.txt
│   │   ├── phase4e_quarantine_root_shadows_latest.json
│   │   ├── portfolio_service_chain_graph_v1.json
│   │   ├── repo_index.json
│   │   ├── repo_index_v2.json
│   │   ├── risk_service_chain_graph_v1.json
│   │   ├── runtime_flow_overlay_v1.json
│   │   ├── runtime_static_dependency_diff_v1.json
│   │   ├── runtime_static_diff_classification_v1.json
│   │   ├── service_chain_graph_v1.json
│   │   ├── stack_layer_sankey_v1.json
│   │   └── strategy_service_chain_graph_v1.json
│   ├── research_db/
│   │   └── research_seed.json
│   ├── strategy_candidate_sandbox/
│   │   ├── 31A_historical_bars_fetch_validation_latest.json
│   │   ├── 31B_historical_bars_multi_symbol_validation_latest.json
│   │   ├── 31C_historical_replay_executor_stub_latest.json
│   │   ├── 31D_historical_replay_bar_iterator_latest.json
│   │   ├── 31E_first_single_candidate_replay_dry_run_latest.json
│   │   ├── 31F_replay_metrics_contract_latest.json
│   │   ├── 32A_real_metrics_generation_latest.json
│   │   ├── 32B_candidate_scorecard_from_replay_metrics_latest.json
│   │   ├── 32C_manual_promotion_gate_stub_latest.json
│   │   ├── 32D_pipeline_rollup_certification_latest.json
│   │   ├── 32E_handoff_bundle_refresh_latest.json
│   │   ├── 33A_trade_simulation_contract_stub_latest.json
│   │   ├── 33B_trade_event_validation_stub_latest.json
│   │   ├── 33C_trade_simulation_dry_run_stub_latest.json
│   │   ├── 33D_entry_exit_signal_contract_stub_latest.json
│   │   ├── 33E_hold_signal_generator_stub_latest.json
│   │   ├── 33F_entry_exit_decision_engine_stub_latest.json
│   │   ├── 33G_hold_decision_to_hold_event_bridge_latest.json
│   │   ├── 33H_trade_simulation_pipeline_rollup_certification_latest.json
│   │   ├── 33I_handoff_bundle_refresh_latest.json
│   │   ├── 34A_entry_signal_rule_contract_stub_latest.json
│   │   ├── 34B_entry_signal_rule_validation_stub_latest.json
│   │   ├── 34C_entry_signal_generator_disabled_stub_latest.json
│   │   ├── 34D_entry_signal_pipeline_rollup_certification_latest.json
│   │   ├── 34E_handoff_bundle_refresh_latest.json
│   │   ├── 35A_exit_signal_rule_contract_stub_latest.json
│   │   ├── 35B_exit_signal_rule_validation_stub_latest.json
│   │   ├── 35C_exit_signal_generator_disabled_stub_latest.json
│   │   ├── 35D_exit_signal_pipeline_rollup_certification_latest.json
│   │   ├── 35E_strategy_sandbox_wiregraph_latest.json
│   │   ├── 35E_strategy_sandbox_wiregraph_latest.mmd
│   │   ├── 35F_handoff_bundle_refresh_latest.json
│   │   ├── 36A_strategy_rule_enablement_gate_contract_stub_latest.json
│   │   ├── 36B_enablement_gate_validation_stub_latest.json
│   │   ├── 36C_enablement_gate_pipeline_rollup_certification_latest.json
│   │   ├── 36D_handoff_bundle_refresh_latest.json
│   │   ├── 37A_trade_simulation_enablement_gate_contract_stub_latest.json
│   │   ├── 37B_trade_simulation_enablement_gate_validation_stub_latest.json
│   │   ├── 37C_trade_simulation_enablement_gate_pipeline_rollup_certification_latest.json
│   │   ├── 37D_handoff_bundle_refresh_latest.json
│   │   ├── 38A_risk_gate_contract_stub_latest.json
│   │   ├── 38B_risk_gate_validation_stub_latest.json
│   │   ├── 38C_risk_gate_pipeline_rollup_certification_latest.json
│   │   ├── 38D_handoff_bundle_refresh_latest.json
│   │   ├── 39A_master_sandbox_gate_wiregraph_latest.json
│   │   ├── 39A_master_sandbox_gate_wiregraph_latest.mmd
│   │   ├── 39B_master_sandbox_gate_wiregraph_rollup_certification_latest.json
│   │   ├── 39C_handoff_bundle_refresh_latest.json
│   │   ├── 40A_sandbox_runtime_dependency_trace_stub_latest.json
│   │   ├── 40B_sandbox_runtime_dependency_trace_rollup_certification_latest.json
│   │   ├── 40C_handoff_bundle_refresh_latest.json
│   │   ├── 41A_safe_read_only_architecture_inspector_stub_latest.json
│   │   ├── 41B_safe_read_only_architecture_inspector_rollup_certification_latest.json
│   │   ├── 41C_handoff_bundle_refresh_latest.json
│   │   ├── 42A_qwen_read_only_architecture_context_stub_latest.json
│   │   ├── 42B_qwen_read_only_architecture_context_rollup_certification_latest.json
│   │   ├── 42C_handoff_bundle_refresh_latest.json
│   │   ├── 43A_qwen_context_response_contract_stub_latest.json
│   │   ├── 43B_qwen_context_response_contract_rollup_certification_latest.json
│   │   ├── 43C_handoff_bundle_refresh_latest.json
│   │   ├── 44A_qwen_read_only_response_sample_stub_latest.json
│   │   ├── 44B_qwen_read_only_response_sample_rollup_certification_latest.json
│   │   ├── 44C_handoff_bundle_refresh_latest.json
│   │   ├── 45A_qwen_read_only_architecture_summary_gate_stub_latest.json
│   │   ├── 45B_qwen_read_only_architecture_summary_gate_rollup_certification_latest.json
│   │   ├── 45C_handoff_bundle_refresh_latest.json
│   │   ├── 46A_qwen_read_only_missing_context_detector_stub_latest.json
│   │   ├── 46B_qwen_read_only_missing_context_detector_rollup_certification_latest.json
│   │   ├── 46C_handoff_bundle_refresh_latest.json
│   │   ├── 47A_qwen_read_only_recommendation_filter_stub_latest.json
│   │   ├── 47B_qwen_read_only_recommendation_filter_rollup_certification_latest.json
│   │   ├── 47C_handoff_bundle_refresh_latest.json
│   │   ├── 48A_qwen_read_only_response_validator_stub_latest.json
│   │   ├── 48B_qwen_read_only_response_validator_rollup_certification_latest.json
│   │   ├── 48C_handoff_bundle_refresh_latest.json
│   │   ├── 49A_qwen_read_only_architecture_session_contract_stub_latest.json
│   │   ├── 49B_qwen_read_only_architecture_session_contract_rollup_certification_latest.json
│   │   ├── 49C_handoff_bundle_refresh_latest.json
│   │   ├── 50A_qwen_read_only_session_response_bridge_stub_latest.json
│   │   ├── 50B_qwen_read_only_session_response_bridge_rollup_certification_latest.json
│   │   ├── 50C_handoff_bundle_refresh_latest.json
│   │   ├── 51A_qwen_read_only_architecture_loop_boundary_stub_latest.json
│   │   ├── 51B_qwen_read_only_architecture_loop_boundary_rollup_certification_latest.json
│   │   ├── 51C_handoff_bundle_refresh_latest.json
│   │   ├── 52A_qwen_read_only_final_guardrail_summary_stub_latest.json
│   │   ├── 52B_qwen_read_only_final_guardrail_summary_rollup_certification_latest.json
│   │   ├── 52C_handoff_bundle_refresh_latest.json
│   │   ├── 53A_qwen_read_only_handoff_freeze_stub_latest.json
│   │   ├── 53B_qwen_read_only_handoff_freeze_rollup_certification_latest.json
│   │   ├── 53C_handoff_bundle_refresh_latest.json
│   │   ├── 54A_qwen_read_only_handoff_export_summary_stub_latest.json
│   │   ├── 54B_qwen_read_only_handoff_export_summary_rollup_certification_latest.json
│   │   ├── 54C_handoff_bundle_refresh_latest.json
│   │   ├── 55A_qwen_read_only_architecture_state_machine_stub_latest.json
│   │   ├── 55B_qwen_read_only_architecture_state_machine_rollup_certification_latest.json
│   │   ├── 55C_handoff_bundle_refresh_latest.json
│   │   ├── 56A_qwen_read_only_architecture_policy_map_stub_latest.json
│   │   ├── 56B_qwen_read_only_architecture_policy_map_rollup_certification_latest.json
│   │   ├── 56C_handoff_bundle_refresh_latest.json
│   │   ├── 57A_qwen_read_only_policy_boundary_matrix_stub_latest.json
│   │   ├── 57B_qwen_read_only_policy_boundary_matrix_rollup_certification_latest.json
│   │   ├── 57C_handoff_bundle_refresh_latest.json
│   │   ├── 58A_qwen_read_only_final_context_package_stub_latest.json
│   │   ├── 58B_qwen_read_only_final_context_package_rollup_certification_latest.json
│   │   ├── 58C_handoff_bundle_refresh_latest.json
│   │   ├── 59A_qwen_read_only_final_handoff_certification_stub_latest.json
│   │   ├── 59B_qwen_read_only_final_handoff_certification_rollup_certification_latest.json
│   │   ├── 59C_handoff_bundle_refresh_latest.json
│   │   ├── 60A_qwen_read_only_terminal_freeze_stub_latest.json
│   │   ├── 60B_qwen_read_only_terminal_freeze_rollup_certification_latest.json
│   │   ├── 60C_handoff_bundle_refresh_latest.json
│   │   ├── 61A_archive_or_new_chat_handoff_summary_latest.json
│   │   ├── candidate_20260706_144431_8a545b3c_mock_metrics.json
│   │   ├── candidate_20260706_144431_8a545b3c_mock_scorecard.json
│   │   ├── candidate_20260706_144431_8a545b3c_sandbox_result_stub.json
│   │   ├── candidate_20260706_144431_8a545b3c_sandbox_stub.json
│   │   ├── candidate_20260706_145350_816903d1_mock_metrics.json
│   │   ├── candidate_20260706_145350_816903d1_mock_scorecard.json
│   │   ├── candidate_20260706_145350_816903d1_sandbox_result_stub.json
│   │   ├── candidate_20260706_145350_816903d1_sandbox_stub.json
│   │   ├── candidate_20260706_150540_4fc7b8ab_mock_metrics.json
│   │   ├── candidate_20260706_150540_4fc7b8ab_mock_scorecard.json
│   │   ├── candidate_20260706_150540_4fc7b8ab_sandbox_result_stub.json
│   │   ├── candidate_20260706_150540_4fc7b8ab_sandbox_stub.json
│   │   ├── candidate_20260706_151330_9f852272_mock_metrics.json
│   │   ├── candidate_20260706_151330_9f852272_mock_scorecard.json
│   │   ├── candidate_20260706_151330_9f852272_sandbox_result_stub.json
│   │   ├── candidate_20260706_151330_9f852272_sandbox_stub.json
│   │   ├── candidate_20260706_152354_e2129e4e_mock_metrics.json
│   │   ├── candidate_20260706_152354_e2129e4e_mock_scorecard.json
│   │   ├── candidate_20260706_152354_e2129e4e_sandbox_result_stub.json
│   │   ├── candidate_20260706_152354_e2129e4e_sandbox_stub.json
│   │   ├── candidate_20260706_152930_73031c40_mock_metrics.json
│   │   ├── candidate_20260706_152930_73031c40_mock_scorecard.json
│   │   ├── candidate_20260706_152930_73031c40_sandbox_result_stub.json
│   │   ├── candidate_20260706_152930_73031c40_sandbox_stub.json
│   │   ├── candidate_sandbox_execution_contract_v1.json
│   │   ├── candidate_sandbox_execution_contract_v1.txt
│   │   ├── candidate_sandbox_mock_metrics_index_latest.json
│   │   ├── candidate_sandbox_mock_metrics_index_latest.txt
│   │   ├── candidate_sandbox_mock_scorecard_latest.json
│   │   ├── candidate_sandbox_mock_scorecard_latest.txt
│   │   ├── candidate_sandbox_result_example_latest.json
│   │   ├── candidate_sandbox_result_schema_v1.json
│   │   ├── candidate_sandbox_result_stub_index_latest.json
│   │   ├── candidate_sandbox_result_stub_index_latest.txt
│   │   ├── historical_bars_contract_v1.json
│   │   ├── historical_bars_contract_v1.txt
│   │   ├── historical_replay_engine_stub_latest.json
│   │   ├── historical_replay_engine_stub_latest.txt
│   │   ├── historical_replay_input_contract_v1.json
│   │   ├── historical_replay_input_contract_v1.txt
│   │   ├── historical_replay_market_data_provider_contract_v1.json
│   │   ├── historical_replay_market_data_provider_contract_v1.txt
│   │   ├── historical_replay_provider_adapter_stub_latest.json
│   │   ├── historical_replay_provider_adapter_stub_latest.txt
│   │   ├── historical_replay_validation_stub_latest.json
│   │   ├── historical_replay_validation_stub_latest.txt
│   │   ├── sandbox_dry_run_index_latest.json
│   │   ├── sandbox_dry_run_index_latest.txt
│   │   ├── simulation_harness_stub_latest.json
│   │   ├── simulation_harness_stub_latest.txt
│   │   ├── yfinance_historical_bars_adapter_shape_validation_latest.json
│   │   ├── yfinance_historical_bars_adapter_shape_validation_latest.txt
│   │   ├── yfinance_historical_bars_adapter_stub_latest.json
│   │   ├── yfinance_historical_bars_adapter_stub_latest.txt
│   │   ├── yfinance_historical_bars_adapter_wire_latest.json
│   │   ├── yfinance_historical_bars_adapter_wire_preview_latest.json
│   │   ├── yfinance_historical_bars_adapter_wire_preview_latest.txt
│   │   ├── yfinance_historical_bars_provider_probe_latest.json
│   │   └── yfinance_historical_bars_provider_probe_latest.txt
│   └── strategy_candidates/
│       ├── candidate_20260706_144431_8a545b3c.json
│       ├── candidate_20260706_145350_816903d1.json
│       ├── candidate_20260706_150540_4fc7b8ab.json
│       ├── candidate_20260706_151330_9f852272.json
│       ├── candidate_20260706_152354_e2129e4e.json
│       ├── candidate_20260706_152930_73031c40.json
│       ├── candidate_20260706_171550_aca89979.json
│       ├── candidate_20260706_171803_7979fee4.json
│       ├── candidate_20260706_171835_2412645f.json
│       ├── candidate_20260706_190850_245c152e.json
│       ├── candidate_20260706_190919_18dff139.json
│       ├── candidate_20260706_190955_47174fc4.json
│       ├── candidate_20260706_201713_2d8f8e9e.json
│       ├── candidate_20260706_201808_d90bd687.json
│       ├── candidate_20260706_221600_b8f7600a.json
│       ├── candidate_20260706_234404_20bfeb59.json
│       ├── review_index_latest.json
│       └── review_index_latest.txt
├── scripts/
│   ├── ci/
│   │   └── architecture_ci_guard_v1.py
│   ├── apply_service_relocation_v1.py
│   ├── architecture_enforcement_v1.py
│   ├── architecture_normalization_engine_v1.py
│   ├── orphan_finalizer_v1.py
│   ├── orphan_resolution_engine_v1.py
│   ├── phase10_domain_subsystem_visualization.py
│   ├── phase10_domain_subsystem_visualization_certification.py
│   ├── phase10c_domain_runtime_overlay_visualization.py
│   ├── phase10c_runtime_flow_overlay_certification.py
│   ├── phase10c_runtime_flow_overlay_export.py
│   ├── phase10d_runtime_static_dependency_diff.py
│   ├── phase10d_runtime_static_dependency_diff_certification.py
│   ├── phase10e_classify_runtime_static_diff_edges.py
│   ├── phase10e_diff_classification_certification.py
│   ├── phase10f_architecture_drift_watch_certification.py
│   ├── phase10g_architecture_drift_dashboard_certification.py
│   ├── phase10g_architecture_drift_dashboard_summary.py
│   ├── phase10h_architecture_dashboard_command_certification.py
│   ├── phase11_live_market_price_api_bridge.py
│   ├── phase11_live_market_price_api_bridge_certification.py
│   ├── phase11b_frontend_live_price_card.py
│   ├── phase11b_frontend_live_price_card_certification.py
│   ├── phase11c_frontend_polling_api_cleanup.py
│   ├── phase11c_frontend_polling_api_cleanup_certification.py
│   ├── phase11d_next_api_proxy_live_price.py
│   ├── phase11d_next_api_proxy_live_price_certification.py
│   ├── phase11e_frontend_build_type_certification.py
│   ├── phase11f_frontend_type_lint_repair.py
│   ├── phase11f_frontend_type_lint_repair_certification.py
│   ├── phase11g_live_market_dashboard_expansion.py
│   ├── phase11g_live_market_dashboard_expansion_certification.py
│   ├── phase12_service_layer_alignment.py
│   ├── phase12e_service_chain_graph_export.py
│   ├── phase12f_service_chain_certification.py
│   ├── phase12g_add_service_chain_to_dashboard.py
│   ├── phase12g_service_chain_dashboard_certification.py
│   ├── phase12g_service_chain_repair.py
│   ├── phase13_portfolio_positions_service_chain.py
│   ├── phase13e_portfolio_service_chain_graph_export.py
│   ├── phase13f_portfolio_positions_service_chain_certification.py
│   ├── phase13g_add_portfolio_chain_to_dashboard.py
│   ├── phase13g_portfolio_chain_dashboard_certification.py
│   ├── phase14_strategy_decision_service_chain.py
│   ├── phase14e_strategy_service_chain_graph_export.py
│   ├── phase14f_strategy_decision_service_chain_certification.py
│   ├── phase14g_add_strategy_chain_to_dashboard.py
│   ├── phase14g_strategy_chain_dashboard_certification.py
│   ├── phase15_risk_gate_service_chain.py
│   ├── phase15e_risk_service_chain_graph_export.py
│   ├── phase15f_risk_gate_service_chain_certification.py
│   ├── phase15g_add_risk_chain_to_dashboard.py
│   ├── phase15g_risk_chain_dashboard_certification.py
│   ├── phase16_api_route_separation_certification.py
│   ├── phase17_dashboard_route_map_certification.py
│   ├── phase17_dashboard_route_map_frontend_card_verification.py
│   ├── phase18_real_positions_panel_certification.py
│   ├── phase18_real_positions_panel_component.py
│   ├── phase19_dashboard_visual_layout_certification.py
│   ├── phase19_dashboard_visual_layout_hardening.py
│   ├── phase19b_endpoint_activation_probe_repair.py
│   ├── phase19c_endpoint_activation_certification.py
│   ├── phase1_repo_research_market_bootstrap.py
│   ├── phase20_floating_chat_widget_service_chain.py
│   ├── phase20e_chat_service_chain_graph_export.py
│   ├── phase20f_floating_chat_widget_certification.py
│   ├── phase21_fix_chat_service_generator.py
│   ├── phase21ab_chat_cache_history.py
│   ├── phase21ab_chat_cache_history_certification.py
│   ├── phase21cd_chat_ux_persistent_cache.py
│   ├── phase21cd_chat_ux_persistent_cache_certification.py
│   ├── phase22_live_graph_tab.py
│   ├── phase22_live_graph_tab_certification.py
│   ├── phase22b_live_graph_visualization.py
│   ├── phase22b_live_graph_visualization_certification.py
│   ├── phase23a_frontend_request_normalizer.py
│   ├── phase23a_frontend_request_normalizer_certification.py
│   ├── phase23b_polling_governor_certification.py
│   ├── phase24a_frontend_observability_dashboard.py
│   ├── phase24a_frontend_observability_dashboard_certification.py
│   ├── phase24b_persist_observability_backend_health.py
│   ├── phase24b_persist_observability_backend_health_certification.py
│   ├── phase24c_observability_event_timeline.py
│   ├── phase24c_observability_event_timeline_certification.py
│   ├── phase24d_observability_lock_handoff_snapshot.py
│   ├── phase25a_dashboard_tab_shell_layout_navigation.py
│   ├── phase25a_dashboard_tab_shell_layout_navigation_certification.py
│   ├── phase25b_tab_layout_polish_chat_panel.py
│   ├── phase25b_tab_layout_polish_chat_panel_certification.py
│   ├── phase25c_split_dashboard_panels_into_tab_workspaces.py
│   ├── phase25c_split_dashboard_panels_into_tab_workspaces_certification.py
│   ├── phase26a_chat_intent_regex_ollama_router.py
│   ├── phase26b_wire_ollama_into_chat_runtime.py
│   ├── phase26c_chat_safety_prompt_live_execution_guard_certification.py
│   ├── phase26d_frontend_chat_response_normalizer.py
│   ├── phase26d_frontend_chat_response_normalizer_certification.py
│   ├── phase26e_chat_metadata_chips_typing_enter.py
│   ├── phase26e_chat_metadata_chips_typing_enter_certification.py
│   ├── phase26f_chat_ui_state_cleanup_metadata_rendering.py
│   ├── phase26f_chat_ui_state_cleanup_metadata_rendering_certification.py
│   ├── phase27a_strategy_proposal_capture.py
│   ├── phase27a_strategy_proposal_capture_certification.py
│   ├── phase27b_strategy_candidate_review_index.py
│   ├── phase27b_strategy_candidate_review_index_certification.py
│   ├── phase27c_candidate_sandbox_dry_run_stub.py
│   ├── phase27c_candidate_sandbox_dry_run_stub_certification.py
│   ├── phase27d_candidate_sandbox_result_schema.py
│   ├── phase27d_candidate_sandbox_result_schema_certification.py
│   ├── phase27e_candidate_sandbox_result_stub_generator.py
│   ├── phase27e_candidate_sandbox_result_stub_generator_certification.py
│   ├── phase27f_candidate_sandbox_readiness_lock_snapshot.py
│   ├── phase28a_candidate_sandbox_simulation_harness_stub.py
│   ├── phase28a_candidate_sandbox_simulation_harness_stub_certification.py
│   ├── phase28b_candidate_sandbox_mock_metrics_generator.py
│   ├── phase28b_candidate_sandbox_mock_metrics_generator_certification.py
│   ├── phase28c_candidate_sandbox_mock_scorecard.py
│   ├── phase28c_candidate_sandbox_mock_scorecard_certification.py
│   ├── phase28d_candidate_sandbox_execution_contract.py
│   ├── phase28d_candidate_sandbox_execution_contract_certification.py
│   ├── phase29a_historical_replay_engine_stub.py
│   ├── phase29a_historical_replay_engine_stub_certification.py
│   ├── phase29b_historical_replay_input_contract.py
│   ├── phase29b_historical_replay_input_contract_certification.py
│   ├── phase29c_historical_replay_validation_stub.py
│   ├── phase29c_historical_replay_validation_stub_certification.py
│   ├── phase29d_historical_replay_readiness_snapshot.py
│   ├── phase29e_historical_replay_market_data_provider_contract.py
│   ├── phase29e_historical_replay_market_data_provider_contract_certification.py
│   ├── phase29f_historical_replay_provider_adapter_stub.py
│   ├── phase29f_historical_replay_provider_adapter_stub_certification.py
│   ├── phase29g_historical_replay_provider_readiness_snapshot.py
│   ├── phase2_yfinance_market_warehouse.py
│   ├── phase30a_yfinance_historical_bars_provider_probe.py
│   ├── phase30a_yfinance_historical_bars_provider_probe_certification.py
│   ├── phase30b_yfinance_provider_selection_snapshot.py
│   ├── phase30c_historical_bars_contract.py
│   ├── phase30c_historical_bars_contract_certification.py
│   ├── phase30d_yfinance_historical_bars_adapter_stub.py
│   ├── phase30d_yfinance_historical_bars_adapter_stub_certification.py
│   ├── phase30e_yfinance_historical_bars_adapter_shape_validation.py
│   ├── phase30e_yfinance_historical_bars_adapter_shape_validation_certification.py
│   ├── phase30f_yfinance_historical_bars_adapter_wire_preview.py
│   ├── phase30f_yfinance_historical_bars_adapter_wire_preview_certification.py
│   ├── phase30g_yfinance_historical_bars_adapter_wire.py
│   ├── phase30g_yfinance_historical_bars_adapter_wire_certification.py
│   ├── phase31a_historical_bars_fetch_validation.py
│   ├── phase31b_historical_bars_multi_symbol_validation.py
│   ├── phase31c_historical_replay_executor_stub.py
│   ├── phase31d_historical_replay_bar_iterator.py
│   ├── phase31e_first_single_candidate_replay_dry_run.py
│   ├── phase31f_replay_metrics_contract.py
│   ├── phase32a_real_metrics_generation.py
│   ├── phase32b_candidate_scorecard_from_replay_metrics.py
│   ├── phase32c_manual_promotion_gate_stub.py
│   ├── phase32d_pipeline_rollup_certification.py
│   ├── phase32e_handoff_bundle_refresh.py
│   ├── phase33a_trade_simulation_contract_stub.py
│   ├── phase33b_trade_event_validation_stub.py
│   ├── phase33c_trade_simulation_dry_run_stub.py
│   ├── phase33d_entry_exit_signal_contract_stub.py
│   ├── phase33e_hold_signal_generator_stub.py
│   ├── phase33f_entry_exit_decision_engine_stub.py
│   ├── phase33g_hold_decision_to_hold_event_bridge.py
│   ├── phase33h_trade_simulation_pipeline_rollup_certification.py
│   ├── phase33i_handoff_bundle_refresh.py
│   ├── phase34a_entry_signal_rule_contract_stub.py
│   ├── phase34b_entry_signal_rule_validation_stub.py
│   ├── phase34c_entry_signal_generator_disabled_stub.py
│   ├── phase34d_entry_signal_pipeline_rollup_certification.py
│   ├── phase34e_handoff_bundle_refresh.py
│   ├── phase35a_exit_signal_rule_contract_stub.py
│   ├── phase35b_exit_signal_rule_validation_stub.py
│   ├── phase35c_exit_signal_generator_disabled_stub.py
│   ├── phase35d_exit_signal_pipeline_rollup_certification.py
│   ├── phase35e_strategy_sandbox_wiregraph_certification.py
│   ├── phase35f_handoff_bundle_refresh.py
│   ├── phase36a_strategy_rule_enablement_gate_contract_stub.py
│   ├── phase36b_enablement_gate_validation_stub.py
│   ├── phase36c_enablement_gate_pipeline_rollup_certification.py
│   ├── phase36d_handoff_bundle_refresh.py
│   ├── phase37a_trade_simulation_enablement_gate_contract_stub.py
│   ├── phase37b_trade_simulation_enablement_gate_validation_stub.py
│   ├── phase37c_trade_simulation_enablement_gate_pipeline_rollup_certification.py
│   ├── phase37d_handoff_bundle_refresh.py
│   ├── phase38a_risk_gate_contract_stub.py
│   ├── phase38b_risk_gate_validation_stub.py
│   ├── phase38c_risk_gate_pipeline_rollup_certification.py
│   ├── phase38d_handoff_bundle_refresh.py
│   ├── phase39a_master_sandbox_gate_wiregraph_refresh.py
│   ├── phase39b_master_sandbox_gate_wiregraph_rollup_certification.py
│   ├── phase39c_handoff_bundle_refresh.py
│   ├── phase3m_graph_certification.py
│   ├── phase40a_sandbox_runtime_dependency_trace_stub.py
│   ├── phase40b_sandbox_runtime_dependency_trace_rollup_certification.py
│   ├── phase40c_handoff_bundle_refresh.py
│   ├── phase41a_safe_read_only_architecture_inspector_stub.py
│   ├── phase41b_safe_read_only_architecture_inspector_rollup_certification.py
│   ├── phase41c_handoff_bundle_refresh.py
│   ├── phase42a_qwen_read_only_architecture_context_stub.py
│   ├── phase42b_qwen_read_only_architecture_context_rollup_certification.py
│   ├── phase42c_handoff_bundle_refresh.py
│   ├── phase43a_qwen_context_response_contract_stub.py
│   ├── phase43b_qwen_context_response_contract_rollup_certification.py
│   ├── phase43c_handoff_bundle_refresh.py
│   ├── phase44a_qwen_read_only_response_sample_stub.py
│   ├── phase44b_qwen_read_only_response_sample_rollup_certification.py
│   ├── phase44c_handoff_bundle_refresh.py
│   ├── phase45a_qwen_read_only_architecture_summary_gate_stub.py
│   ├── phase45b_qwen_read_only_architecture_summary_gate_rollup_certification.py
│   ├── phase45c_handoff_bundle_refresh.py
│   ├── phase46a_qwen_read_only_missing_context_detector_stub.py
│   ├── phase46b_qwen_read_only_missing_context_detector_rollup_certification.py
│   ├── phase46c_handoff_bundle_refresh.py
│   ├── phase47a_qwen_read_only_recommendation_filter_stub.py
│   ├── phase47b_qwen_read_only_recommendation_filter_rollup_certification.py
│   ├── phase47c_handoff_bundle_refresh.py
│   ├── phase48a_qwen_read_only_response_validator_stub.py
│   ├── phase48b_qwen_read_only_response_validator_rollup_certification.py
│   ├── phase48c_handoff_bundle_refresh.py
│   ├── phase49a_qwen_read_only_architecture_session_contract_stub.py
│   ├── phase49b_qwen_read_only_architecture_session_contract_rollup_certification.py
│   ├── phase49c_handoff_bundle_refresh.py
│   ├── phase4_repo_memory_indexer_v2.py
│   ├── phase4c_loose_root_duplicate_quarantine_plan.py
│   ├── phase4d_root_shadow_diff_report.py
│   ├── phase4e_quarantine_root_shadows.py
│   ├── phase4g_repo_memory_certification.py
│   ├── phase50a_qwen_read_only_session_response_bridge_stub.py
│   ├── phase50b_qwen_read_only_session_response_bridge_rollup_certification.py
│   ├── phase50c_handoff_bundle_refresh.py
│   ├── phase51a_qwen_read_only_architecture_loop_boundary_stub.py
│   ├── phase51b_qwen_read_only_architecture_loop_boundary_rollup_certification.py
│   ├── phase51c_handoff_bundle_refresh.py
│   ├── phase52a_qwen_read_only_final_guardrail_summary_stub.py
│   ├── phase52b_qwen_read_only_final_guardrail_summary_rollup_certification.py
│   ├── phase52c_handoff_bundle_refresh.py
│   ├── phase53a_qwen_read_only_handoff_freeze_stub.py
│   ├── phase53b_qwen_read_only_handoff_freeze_rollup_certification.py
│   ├── phase53c_handoff_bundle_refresh.py
│   ├── phase54a_qwen_read_only_handoff_export_summary_stub.py
│   ├── phase54b_qwen_read_only_handoff_export_summary_rollup_certification.py
│   ├── phase54c_handoff_bundle_refresh.py
│   ├── phase55a_qwen_read_only_architecture_state_machine_stub.py
│   ├── phase55b_qwen_read_only_architecture_state_machine_rollup_certification.py
│   ├── phase55c_handoff_bundle_refresh.py
│   ├── phase56a_qwen_read_only_architecture_policy_map_stub.py
│   ├── phase56b_qwen_read_only_architecture_policy_map_rollup_certification.py
│   ├── phase56c_handoff_bundle_refresh.py
│   ├── phase57a_qwen_read_only_policy_boundary_matrix_stub.py
│   ├── phase57b_qwen_read_only_policy_boundary_matrix_rollup_certification.py
│   ├── phase57c_handoff_bundle_refresh.py
│   ├── phase58a_qwen_read_only_final_context_package_stub.py
│   ├── phase58b_qwen_read_only_final_context_package_rollup_certification.py
│   ├── phase58c_handoff_bundle_refresh.py
│   ├── phase59a_qwen_read_only_final_handoff_certification_stub.py
│   ├── phase59b_qwen_read_only_final_handoff_certification_rollup_certification.py
│   ├── phase59c_handoff_bundle_refresh.py
│   ├── phase5c_repo_memory_certification_v2.py
│   ├── phase60a_qwen_read_only_terminal_freeze_stub.py
│   ├── phase60b_qwen_read_only_terminal_freeze_rollup_certification.py
│   ├── phase60c_handoff_bundle_refresh.py
│   ├── phase61a_archive_or_new_chat_handoff_summary.py
│   ├── phase62a_master_architecture_handoff_controller.py
│   ├── phase6b_dependency_validation_certification.py
│   ├── phase6c_dependency_graph_export.py
│   ├── phase6d_dependency_graph_certification.py
│   ├── phase7a_dependency_topology_overlay_export.py
│   ├── phase7g_graph_visualization_certification.py
│   ├── phase8c_neuro_cli_hotspots_certification.py
│   ├── phase9a_canonical_layer_graph_export.py
│   ├── phase9b_component_overlay_export.py
│   ├── phase9c_generate_layer_colored_wire_graph.py
│   ├── phase9e_canonical_graph_certification.py
│   ├── phase9k_domain_subsystem_graph_export.py
│   ├── phase9l_stack_layer_sankey_export.py
│   ├── phase9m_canonical_graph_certification_v2.py
│   ├── reconcile_repo_state_v1.py
│   ├── service_stack_relocator_v1.py
│   └── topology_state_lock_v1.py
├── $OUTPUT
├── .aider.chat.history.md
├── .aider.input.history
├── .env
├── .env.example
├── .gitignore
├── ARCH_ENFORCEMENT_REPORT.json
├── ARCH_GOVERNANCE.md
├── ARCHITECTURE_REPAIR_PLAN.json
├── cursor.AppImage
├── Directory Structure
├── docker-compose.yml
├── domain_runtime_overlay_graph.png
├── domain_subsystem_graph.png
├── FINAL_ARCHITECTURE_STATE.json
├── fix_phase9_self_fingerprint.sh
├── generate_wire_graph.py
├── neuro
├── neuro_cli.py
├── neuro_cli_file_inspection.json
├── neuro_engineer.py
├── neuro_health.sh
├── neurovest_repo_context.md
├── ORPHAN_RESOLUTION_PLAN.json
├── OUTPUT
├── pytest.ini
├── SERVICE_RELOCATION_PLAN.json
├── SERVICE_RELOCATION_PLAN_RECONCILED.json
├── spine_mvp_full.sh
├── system_tree.txt
├── TOPOLOGY_NORMALIZED_STATE.json
├── TOPOLOGY_STATE.json
├── topology_wire_graph.png
└── topology_wire_graph_canonical.png
```

---

# 7. [Repository Topology] Backend Tree

Source: `handoff/backend_tree.txt`

```text
backend/
├── app/
│   ├── analysis/
│   │   └── architecture.py
│   ├── api/
│   │   └── graph_ws.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── cognitive_event_bus.py
│   │   ├── cognitive_graph_state.py
│   │   ├── cognitive_nodes.py
│   │   ├── cognitive_types.py
│   │   ├── config.py
│   │   ├── global_firewall_v1.py
│   │   └── runtime_firewall_v1.py
│   ├── models/
│   ├── routers/
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── dashboard.py
│   ├── services/
│   │   └── __init__.py
│   ├── snaptrade/
│   │   └── executions/
│   │       ├── config.py
│   │       └── execution_layer.py
│   ├── stacks/
│   │   ├── auth_identity/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── gate.py
│   │   │   └── validator.py
│   │   ├── chat_public/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── chat_api.py
│   │   │   ├── chat_intent_regex.py
│   │   │   ├── chat_memory.py
│   │   │   ├── chat_runtime.py
│   │   │   ├── chat_service.py
│   │   │   ├── chat_system_prompt.py
│   │   │   ├── context_loader.py
│   │   │   ├── conversation_store.py
│   │   │   ├── ollama_chat_client.py
│   │   │   ├── strategy_proposal_capture.py
│   │   │   └── time_context.py
│   │   ├── db_model/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   └── market_schema.py
│   │   ├── events/
│   │   │   └── broker.py
│   │   ├── execution/
│   │   │   ├── __init__.py
│   │   │   ├── accounting_engine.py
│   │   │   ├── base.py
│   │   │   ├── broker.py
│   │   │   ├── commission_engine.py
│   │   │   ├── executor.py
│   │   │   ├── fill_engine.py
│   │   │   ├── paper_broker.py
│   │   │   ├── pnl_engine.py
│   │   │   ├── regime_modes.py
│   │   │   ├── regime_simulator.py
│   │   │   ├── sandbox.py
│   │   │   ├── sandbox_runtime.py
│   │   │   └── trade_ledger.py
│   │   ├── journal_ledger/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── ledger.py
│   │   │   └── record.py
│   │   ├── learning_research/
│   │   │   ├── dataset/
│   │   │   │   ├── finance/
│   │   │   │   └── papers/
│   │   │   ├── __init__.py
│   │   │   ├── backtest_engine.py
│   │   │   ├── base.py
│   │   │   ├── monte_carlo.py
│   │   │   ├── monte_carlo_mix.py
│   │   │   ├── probability_engine.py
│   │   │   ├── research_loader.py
│   │   │   ├── research_runtime.py
│   │   │   └── strategy_evaluator.py
│   │   ├── market_data/
│   │   │   ├── __init__.py
│   │   │   ├── bars.py
│   │   │   ├── base.py
│   │   │   ├── feed.py
│   │   │   ├── market_data_service.py
│   │   │   ├── market_session.py
│   │   │   ├── price.py
│   │   │   ├── provider_cache.py
│   │   │   ├── provider_registry.py
│   │   │   ├── provider_router.py
│   │   │   ├── yfinance_historical_bars_adapter.py
│   │   │   └── yfinance_ingestor.py
│   │   ├── notification/
│   │   │   ├── __init__.py
│   │   │   └── base.py
│   │   ├── portfolio/
│   │   │   ├── __init__.py
│   │   │   ├── accounting.py
│   │   │   ├── allocator.py
│   │   │   ├── base.py
│   │   │   ├── dashboard_service.py
│   │   │   ├── portfolio_runtime.py
│   │   │   ├── portfolio_service.py
│   │   │   ├── rebalance.py
│   │   │   └── reconciliation.py
│   │   ├── risk/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── drawdown_guard.py
│   │   │   ├── exposure.py
│   │   │   ├── kill_switch.py
│   │   │   ├── limits.py
│   │   │   ├── loss_streak_guard.py
│   │   │   ├── risk_runtime_service.py
│   │   │   └── risk_service.py
│   │   ├── snaptrade/
│   │   │   ├── __init__.py
│   │   │   ├── adapter.py
│   │   │   ├── base.py
│   │   │   ├── broker.py
│   │   │   └── execution.py
│   │   ├── strategy/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── candidate_registry.py
│   │   │   ├── engine.py
│   │   │   ├── evolution_engine.py
│   │   │   ├── llm_strategy_engine.py
│   │   │   ├── selector.py
│   │   │   ├── signal.py
│   │   │   ├── strategy_registry.py
│   │   │   ├── strategy_runtime.py
│   │   │   └── strategy_service.py
│   │   ├── strategy_candidate_sandbox/
│   │   │   ├── candidate_scorecard_from_replay_metrics.py
│   │   │   ├── entry_exit_decision_engine_stub.py
│   │   │   ├── entry_exit_signal_contract.py
│   │   │   ├── entry_signal_generator_disabled_stub.py
│   │   │   ├── entry_signal_rule_contract.py
│   │   │   ├── entry_signal_rule_validator.py
│   │   │   ├── exit_signal_generator_disabled_stub.py
│   │   │   ├── exit_signal_rule_contract.py
│   │   │   ├── exit_signal_rule_validator.py
│   │   │   ├── historical_replay_bar_iterator.py
│   │   │   ├── historical_replay_executor.py
│   │   │   ├── hold_decision_to_hold_event_bridge.py
│   │   │   ├── hold_signal_generator_stub.py
│   │   │   ├── manual_promotion_gate.py
│   │   │   ├── qwen_context_response_contract.py
│   │   │   ├── qwen_read_only_architecture_context.py
│   │   │   ├── qwen_read_only_architecture_summary_gate.py
│   │   │   ├── replay_metrics_contract.py
│   │   │   ├── replay_metrics_generator.py
│   │   │   ├── risk_gate_contract.py
│   │   │   ├── risk_gate_validator.py
│   │   │   ├── safe_read_only_architecture_inspector.py
│   │   │   ├── strategy_rule_enablement_gate_contract.py
│   │   │   ├── strategy_rule_enablement_gate_validator.py
│   │   │   ├── trade_event_validator.py
│   │   │   ├── trade_simulation_contract.py
│   │   │   ├── trade_simulation_dry_run_stub.py
│   │   │   ├── trade_simulation_enablement_gate_contract.py
│   │   │   └── trade_simulation_enablement_gate_validator.py
│   │   ├── wolfden_ai/
│   │   │   ├── repo_memory/
│   │   │   │   └── index/
│   │   │   ├── __init__.py
│   │   │   ├── agent_router.py
│   │   │   ├── base.py
│   │   │   ├── memory.py
│   │   │   ├── orchestrator.py
│   │   │   ├── routing.py
│   │   │   └── runtime.py
│   │   ├── __init__.py
│   │   └── registry.json
│   ├── test/
│   │   ├── test_neuro_repo_companion.py
│   │   └── test_trading_pipeline.py
│   ├── __init__.py
│   └── main.py
├── scripts/
│   └── backup_db.sh
├── __init__.py
└── requirements.txt
```

---

# 8. [Repository Topology] Frontend Tree

Source: `handoff/frontend_tree.txt`

```text
frontend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── chat/
│   │       │   └── route.ts
│   │       ├── graph/
│   │       │   └── live/
│   │       │       └── route.ts
│   │       ├── market/
│   │       │   └── live-price/
│   │       │       └── [symbol]/
│   │       │           └── route.ts
│   │       ├── portfolio/
│   │       │   └── positions/
│   │       │       └── route.ts
│   │       ├── risk/
│   │       │   └── gate/
│   │       │       └── [symbol]/
│   │       │           └── route.ts
│   │       └── strategy/
│   │           └── decision/
│   │               └── [symbol]/
│   │                   └── route.ts
│   ├── favicon.ico
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx
├── public/
│   ├── file.svg
│   ├── globe.svg
│   ├── next.svg
│   ├── vercel.svg
│   └── window.svg
├── services/
│   ├── backendHealthService.ts
│   ├── chatService.ts
│   ├── graphService.ts
│   ├── marketService.ts
│   ├── observabilityTimelineService.ts
│   ├── portfolioService.ts
│   ├── requestNormalizer.ts
│   ├── requestObservability.ts
│   ├── riskService.ts
│   └── strategyService.ts
├── .gitignore
├── AGENTS.md
├── CLAUDE.md
├── eslint.config.mjs
├── next-env.d.ts
├── next.config.ts
├── package-lock.json
├── package.json
├── postcss.config.mjs
├── README.md
└── tsconfig.json
```

---

# 9. [Repository Topology] Runtime Tree

Source: `handoff/runtime_tree.txt`

```text
runtime/
├── certifications/
│   ├── phase10_domain_subsystem_visualization_certification_latest.json
│   ├── phase10c_runtime_flow_overlay_certification_latest.json
│   ├── phase10d_runtime_static_dependency_diff_certification_latest.json
│   ├── phase10e_diff_classification_certification_latest.json
│   ├── phase10f_architecture_drift_watch_certification_latest.json
│   ├── phase10g_architecture_drift_dashboard_certification_latest.json
│   ├── phase10h_architecture_dashboard_command_certification_latest.json
│   ├── phase11_live_market_price_api_bridge_certification_latest.json
│   ├── phase11b_frontend_live_price_card_certification_latest.json
│   ├── phase11c_frontend_polling_api_cleanup_certification_latest.json
│   ├── phase11d_next_api_proxy_live_price_certification_latest.json
│   ├── phase11e_frontend_build_type_certification_latest.json
│   ├── phase11f_frontend_type_lint_repair_certification_latest.json
│   ├── phase11g_live_market_dashboard_expansion_certification_latest.json
│   ├── phase12f_service_chain_certification_latest.json
│   ├── phase12g_service_chain_dashboard_certification_latest.json
│   ├── phase13f_portfolio_positions_service_chain_certification_latest.json
│   ├── phase13g_portfolio_chain_dashboard_certification_latest.json
│   ├── phase14f_strategy_decision_service_chain_certification_latest.json
│   ├── phase14g_strategy_chain_dashboard_certification_latest.json
│   ├── phase15f_risk_gate_service_chain_certification_latest.json
│   ├── phase15g_risk_chain_dashboard_certification_latest.json
│   ├── phase16_api_route_separation_certification_latest.json
│   ├── phase17_dashboard_route_map_certification_latest.json
│   ├── phase18_real_positions_panel_certification_latest.json
│   ├── phase19_dashboard_visual_layout_certification_latest.json
│   ├── phase19c_endpoint_activation_certification_latest.json
│   ├── phase20f_floating_chat_widget_certification_latest.json
│   ├── phase21ab_chat_cache_history_certification_latest.json
│   ├── phase21cd_chat_ux_persistent_cache_certification_latest.json
│   ├── phase22_live_graph_tab_certification_latest.json
│   ├── phase22b_live_graph_visualization_certification_latest.json
│   ├── phase23a_frontend_request_normalizer_certification_latest.json
│   ├── phase23b_polling_governor_certification_latest.json
│   ├── phase24a_frontend_observability_dashboard_certification_latest.json
│   ├── phase24b_persist_observability_backend_health_certification_latest.json
│   ├── phase24c_observability_event_timeline_certification_latest.json
│   ├── phase24d_observability_lock_handoff_snapshot_latest.json
│   ├── phase25a_dashboard_tab_shell_layout_navigation_certification_latest.json
│   ├── phase25b_tab_layout_polish_chat_panel_certification_latest.json
│   ├── phase25c_split_dashboard_panels_into_tab_workspaces_certification_latest.json
│   ├── phase26c_chat_safety_prompt_live_execution_guard_certification_latest.json
│   ├── phase26d_frontend_chat_response_normalizer_certification_latest.json
│   ├── phase26e_chat_metadata_chips_typing_enter_certification_latest.json
│   ├── phase26f_chat_ui_state_cleanup_metadata_rendering_certification_latest.json
│   ├── phase27a_strategy_proposal_capture_certification_latest.json
│   ├── phase27b_strategy_candidate_review_index_certification_latest.json
│   ├── phase27c_candidate_sandbox_dry_run_stub_certification_latest.json
│   ├── phase27d_candidate_sandbox_result_schema_certification_latest.json
│   ├── phase27e_candidate_sandbox_result_stub_generator_certification_latest.json
│   ├── phase27f_candidate_sandbox_readiness_lock_snapshot_latest.json
│   ├── phase28a_candidate_sandbox_simulation_harness_stub_certification_latest.json
│   ├── phase28b_candidate_sandbox_mock_metrics_generator_certification_latest.json
│   ├── phase28c_candidate_sandbox_mock_scorecard_certification_latest.json
│   ├── phase28d_candidate_sandbox_execution_contract_certification_latest.json
│   ├── phase29a_historical_replay_engine_stub_certification_latest.json
│   ├── phase29b_historical_replay_input_contract_certification_latest.json
│   ├── phase29c_historical_replay_validation_stub_certification_latest.json
│   ├── phase29d_historical_replay_readiness_snapshot_latest.json
│   ├── phase29e_historical_replay_market_data_provider_contract_certification_latest.json
│   ├── phase29f_historical_replay_provider_adapter_stub_certification_latest.json
│   ├── phase29g_historical_replay_provider_readiness_snapshot_latest.json
│   ├── phase30a_yfinance_historical_bars_provider_probe_certification_latest.json
│   ├── phase30b_yfinance_provider_selection_snapshot_latest.json
│   ├── phase30c_historical_bars_contract_certification_latest.json
│   ├── phase30d_yfinance_historical_bars_adapter_stub_certification_latest.json
│   ├── phase30e_yfinance_historical_bars_adapter_shape_validation_certification_latest.json
│   ├── phase30f_yfinance_historical_bars_adapter_wire_preview_certification_latest.json
│   ├── phase30g_yfinance_historical_bars_adapter_wire_certification_latest.json
│   ├── phase3m_graph_certification_latest.json
│   ├── phase4g_repo_memory_certification_latest.json
│   ├── phase5c_repo_memory_certification_v2_latest.json
│   ├── phase6b_dependency_validation_certification_latest.json
│   ├── phase6d_dependency_graph_certification_latest.json
│   ├── phase7g_graph_visualization_certification_latest.json
│   ├── phase8c_neuro_cli_hotspots_certification_latest.json
│   ├── phase9e_canonical_graph_certification_latest.json
│   └── phase9m_canonical_graph_certification_v2_latest.json
├── graph_history/
│   ├── current_snapshot.json
│   └── events.jsonl
├── handoff_snapshot/
│   ├── file_manifest_latest.txt
│   ├── live_graph_validate_latest.json
│   ├── neurovest_training_handoff_bundle_latest.json
│   ├── simulate_trade_guard_latest.json
│   └── topology_tree_latest.txt
├── market_warehouse/
│   ├── history/
│   │   ├── AAPL_history.csv
│   │   ├── MSFT_history.csv
│   │   ├── NVDA_history.csv
│   │   ├── RY_TO_history.csv
│   │   ├── TD_TO_history.csv
│   │   ├── TSLA_history.csv
│   │   ├── VFV_TO_history.csv
│   │   └── VUN_TO_history.csv
│   ├── live/
│   │   ├── AAPL_live.json
│   │   ├── MSFT_live.json
│   │   ├── NVDA_live.json
│   │   ├── RY_TO_live.json
│   │   ├── TD_TO_live.json
│   │   ├── TSLA_live.json
│   │   ├── VFV_TO_live.json
│   │   └── VUN_TO_live.json
│   └── symbol_registry.json
├── repo_memory/
│   ├── architecture_drift_dashboard_v1.json
│   ├── architecture_drift_dashboard_v1.txt
│   ├── canonical_layer_graph_v1.json
│   ├── chat_service_chain_graph_v1.json
│   ├── component_overlay_v1.json
│   ├── dashboard_route_map_v1.json
│   ├── dependency_graph_v1.json
│   ├── dependency_topology_overlay_v1.json
│   ├── domain_subsystem_graph_v1.json
│   ├── phase4c_loose_root_duplicate_quarantine_plan_latest.json
│   ├── phase4d_root_shadow_diff_report_latest.json
│   ├── phase4d_root_shadow_diff_report_latest.txt
│   ├── phase4e_quarantine_root_shadows_latest.json
│   ├── portfolio_service_chain_graph_v1.json
│   ├── repo_index.json
│   ├── repo_index_v2.json
│   ├── risk_service_chain_graph_v1.json
│   ├── runtime_flow_overlay_v1.json
│   ├── runtime_static_dependency_diff_v1.json
│   ├── runtime_static_diff_classification_v1.json
│   ├── service_chain_graph_v1.json
│   ├── stack_layer_sankey_v1.json
│   └── strategy_service_chain_graph_v1.json
├── research_db/
│   └── research_seed.json
├── strategy_candidate_sandbox/
│   ├── 31A_historical_bars_fetch_validation_latest.json
│   ├── 31B_historical_bars_multi_symbol_validation_latest.json
│   ├── 31C_historical_replay_executor_stub_latest.json
│   ├── 31D_historical_replay_bar_iterator_latest.json
│   ├── 31E_first_single_candidate_replay_dry_run_latest.json
│   ├── 31F_replay_metrics_contract_latest.json
│   ├── 32A_real_metrics_generation_latest.json
│   ├── 32B_candidate_scorecard_from_replay_metrics_latest.json
│   ├── 32C_manual_promotion_gate_stub_latest.json
│   ├── 32D_pipeline_rollup_certification_latest.json
│   ├── 32E_handoff_bundle_refresh_latest.json
│   ├── 33A_trade_simulation_contract_stub_latest.json
│   ├── 33B_trade_event_validation_stub_latest.json
│   ├── 33C_trade_simulation_dry_run_stub_latest.json
│   ├── 33D_entry_exit_signal_contract_stub_latest.json
│   ├── 33E_hold_signal_generator_stub_latest.json
│   ├── 33F_entry_exit_decision_engine_stub_latest.json
│   ├── 33G_hold_decision_to_hold_event_bridge_latest.json
│   ├── 33H_trade_simulation_pipeline_rollup_certification_latest.json
│   ├── 33I_handoff_bundle_refresh_latest.json
│   ├── 34A_entry_signal_rule_contract_stub_latest.json
│   ├── 34B_entry_signal_rule_validation_stub_latest.json
│   ├── 34C_entry_signal_generator_disabled_stub_latest.json
│   ├── 34D_entry_signal_pipeline_rollup_certification_latest.json
│   ├── 34E_handoff_bundle_refresh_latest.json
│   ├── 35A_exit_signal_rule_contract_stub_latest.json
│   ├── 35B_exit_signal_rule_validation_stub_latest.json
│   ├── 35C_exit_signal_generator_disabled_stub_latest.json
│   ├── 35D_exit_signal_pipeline_rollup_certification_latest.json
│   ├── 35E_strategy_sandbox_wiregraph_latest.json
│   ├── 35E_strategy_sandbox_wiregraph_latest.mmd
│   ├── 35F_handoff_bundle_refresh_latest.json
│   ├── 36A_strategy_rule_enablement_gate_contract_stub_latest.json
│   ├── 36B_enablement_gate_validation_stub_latest.json
│   ├── 36C_enablement_gate_pipeline_rollup_certification_latest.json
│   ├── 36D_handoff_bundle_refresh_latest.json
│   ├── 37A_trade_simulation_enablement_gate_contract_stub_latest.json
│   ├── 37B_trade_simulation_enablement_gate_validation_stub_latest.json
│   ├── 37C_trade_simulation_enablement_gate_pipeline_rollup_certification_latest.json
│   ├── 37D_handoff_bundle_refresh_latest.json
│   ├── 38A_risk_gate_contract_stub_latest.json
│   ├── 38B_risk_gate_validation_stub_latest.json
│   ├── 38C_risk_gate_pipeline_rollup_certification_latest.json
│   ├── 38D_handoff_bundle_refresh_latest.json
│   ├── 39A_master_sandbox_gate_wiregraph_latest.json
│   ├── 39A_master_sandbox_gate_wiregraph_latest.mmd
│   ├── 39B_master_sandbox_gate_wiregraph_rollup_certification_latest.json
│   ├── 39C_handoff_bundle_refresh_latest.json
│   ├── 40A_sandbox_runtime_dependency_trace_stub_latest.json
│   ├── 40B_sandbox_runtime_dependency_trace_rollup_certification_latest.json
│   ├── 40C_handoff_bundle_refresh_latest.json
│   ├── 41A_safe_read_only_architecture_inspector_stub_latest.json
│   ├── 41B_safe_read_only_architecture_inspector_rollup_certification_latest.json
│   ├── 41C_handoff_bundle_refresh_latest.json
│   ├── 42A_qwen_read_only_architecture_context_stub_latest.json
│   ├── 42B_qwen_read_only_architecture_context_rollup_certification_latest.json
│   ├── 42C_handoff_bundle_refresh_latest.json
│   ├── 43A_qwen_context_response_contract_stub_latest.json
│   ├── 43B_qwen_context_response_contract_rollup_certification_latest.json
│   ├── 43C_handoff_bundle_refresh_latest.json
│   ├── 44A_qwen_read_only_response_sample_stub_latest.json
│   ├── 44B_qwen_read_only_response_sample_rollup_certification_latest.json
│   ├── 44C_handoff_bundle_refresh_latest.json
│   ├── 45A_qwen_read_only_architecture_summary_gate_stub_latest.json
│   ├── 45B_qwen_read_only_architecture_summary_gate_rollup_certification_latest.json
│   ├── 45C_handoff_bundle_refresh_latest.json
│   ├── 46A_qwen_read_only_missing_context_detector_stub_latest.json
│   ├── 46B_qwen_read_only_missing_context_detector_rollup_certification_latest.json
│   ├── 46C_handoff_bundle_refresh_latest.json
│   ├── 47A_qwen_read_only_recommendation_filter_stub_latest.json
│   ├── 47B_qwen_read_only_recommendation_filter_rollup_certification_latest.json
│   ├── 47C_handoff_bundle_refresh_latest.json
│   ├── 48A_qwen_read_only_response_validator_stub_latest.json
│   ├── 48B_qwen_read_only_response_validator_rollup_certification_latest.json
│   ├── 48C_handoff_bundle_refresh_latest.json
│   ├── 49A_qwen_read_only_architecture_session_contract_stub_latest.json
│   ├── 49B_qwen_read_only_architecture_session_contract_rollup_certification_latest.json
│   ├── 49C_handoff_bundle_refresh_latest.json
│   ├── 50A_qwen_read_only_session_response_bridge_stub_latest.json
│   ├── 50B_qwen_read_only_session_response_bridge_rollup_certification_latest.json
│   ├── 50C_handoff_bundle_refresh_latest.json
│   ├── 51A_qwen_read_only_architecture_loop_boundary_stub_latest.json
│   ├── 51B_qwen_read_only_architecture_loop_boundary_rollup_certification_latest.json
│   ├── 51C_handoff_bundle_refresh_latest.json
│   ├── 52A_qwen_read_only_final_guardrail_summary_stub_latest.json
│   ├── 52B_qwen_read_only_final_guardrail_summary_rollup_certification_latest.json
│   ├── 52C_handoff_bundle_refresh_latest.json
│   ├── 53A_qwen_read_only_handoff_freeze_stub_latest.json
│   ├── 53B_qwen_read_only_handoff_freeze_rollup_certification_latest.json
│   ├── 53C_handoff_bundle_refresh_latest.json
│   ├── 54A_qwen_read_only_handoff_export_summary_stub_latest.json
│   ├── 54B_qwen_read_only_handoff_export_summary_rollup_certification_latest.json
│   ├── 54C_handoff_bundle_refresh_latest.json
│   ├── 55A_qwen_read_only_architecture_state_machine_stub_latest.json
│   ├── 55B_qwen_read_only_architecture_state_machine_rollup_certification_latest.json
│   ├── 55C_handoff_bundle_refresh_latest.json
│   ├── 56A_qwen_read_only_architecture_policy_map_stub_latest.json
│   ├── 56B_qwen_read_only_architecture_policy_map_rollup_certification_latest.json
│   ├── 56C_handoff_bundle_refresh_latest.json
│   ├── 57A_qwen_read_only_policy_boundary_matrix_stub_latest.json
│   ├── 57B_qwen_read_only_policy_boundary_matrix_rollup_certification_latest.json
│   ├── 57C_handoff_bundle_refresh_latest.json
│   ├── 58A_qwen_read_only_final_context_package_stub_latest.json
│   ├── 58B_qwen_read_only_final_context_package_rollup_certification_latest.json
│   ├── 58C_handoff_bundle_refresh_latest.json
│   ├── 59A_qwen_read_only_final_handoff_certification_stub_latest.json
│   ├── 59B_qwen_read_only_final_handoff_certification_rollup_certification_latest.json
│   ├── 59C_handoff_bundle_refresh_latest.json
│   ├── 60A_qwen_read_only_terminal_freeze_stub_latest.json
│   ├── 60B_qwen_read_only_terminal_freeze_rollup_certification_latest.json
│   ├── 60C_handoff_bundle_refresh_latest.json
│   ├── 61A_archive_or_new_chat_handoff_summary_latest.json
│   ├── candidate_20260706_144431_8a545b3c_mock_metrics.json
│   ├── candidate_20260706_144431_8a545b3c_mock_scorecard.json
│   ├── candidate_20260706_144431_8a545b3c_sandbox_result_stub.json
│   ├── candidate_20260706_144431_8a545b3c_sandbox_stub.json
│   ├── candidate_20260706_145350_816903d1_mock_metrics.json
│   ├── candidate_20260706_145350_816903d1_mock_scorecard.json
│   ├── candidate_20260706_145350_816903d1_sandbox_result_stub.json
│   ├── candidate_20260706_145350_816903d1_sandbox_stub.json
│   ├── candidate_20260706_150540_4fc7b8ab_mock_metrics.json
│   ├── candidate_20260706_150540_4fc7b8ab_mock_scorecard.json
│   ├── candidate_20260706_150540_4fc7b8ab_sandbox_result_stub.json
│   ├── candidate_20260706_150540_4fc7b8ab_sandbox_stub.json
│   ├── candidate_20260706_151330_9f852272_mock_metrics.json
│   ├── candidate_20260706_151330_9f852272_mock_scorecard.json
│   ├── candidate_20260706_151330_9f852272_sandbox_result_stub.json
│   ├── candidate_20260706_151330_9f852272_sandbox_stub.json
│   ├── candidate_20260706_152354_e2129e4e_mock_metrics.json
│   ├── candidate_20260706_152354_e2129e4e_mock_scorecard.json
│   ├── candidate_20260706_152354_e2129e4e_sandbox_result_stub.json
│   ├── candidate_20260706_152354_e2129e4e_sandbox_stub.json
│   ├── candidate_20260706_152930_73031c40_mock_metrics.json
│   ├── candidate_20260706_152930_73031c40_mock_scorecard.json
│   ├── candidate_20260706_152930_73031c40_sandbox_result_stub.json
│   ├── candidate_20260706_152930_73031c40_sandbox_stub.json
│   ├── candidate_sandbox_execution_contract_v1.json
│   ├── candidate_sandbox_execution_contract_v1.txt
│   ├── candidate_sandbox_mock_metrics_index_latest.json
│   ├── candidate_sandbox_mock_metrics_index_latest.txt
│   ├── candidate_sandbox_mock_scorecard_latest.json
│   ├── candidate_sandbox_mock_scorecard_latest.txt
│   ├── candidate_sandbox_result_example_latest.json
│   ├── candidate_sandbox_result_schema_v1.json
│   ├── candidate_sandbox_result_stub_index_latest.json
│   ├── candidate_sandbox_result_stub_index_latest.txt
│   ├── historical_bars_contract_v1.json
│   ├── historical_bars_contract_v1.txt
│   ├── historical_replay_engine_stub_latest.json
│   ├── historical_replay_engine_stub_latest.txt
│   ├── historical_replay_input_contract_v1.json
│   ├── historical_replay_input_contract_v1.txt
│   ├── historical_replay_market_data_provider_contract_v1.json
│   ├── historical_replay_market_data_provider_contract_v1.txt
│   ├── historical_replay_provider_adapter_stub_latest.json
│   ├── historical_replay_provider_adapter_stub_latest.txt
│   ├── historical_replay_validation_stub_latest.json
│   ├── historical_replay_validation_stub_latest.txt
│   ├── sandbox_dry_run_index_latest.json
│   ├── sandbox_dry_run_index_latest.txt
│   ├── simulation_harness_stub_latest.json
│   ├── simulation_harness_stub_latest.txt
│   ├── yfinance_historical_bars_adapter_shape_validation_latest.json
│   ├── yfinance_historical_bars_adapter_shape_validation_latest.txt
│   ├── yfinance_historical_bars_adapter_stub_latest.json
│   ├── yfinance_historical_bars_adapter_stub_latest.txt
│   ├── yfinance_historical_bars_adapter_wire_latest.json
│   ├── yfinance_historical_bars_adapter_wire_preview_latest.json
│   ├── yfinance_historical_bars_adapter_wire_preview_latest.txt
│   ├── yfinance_historical_bars_provider_probe_latest.json
│   └── yfinance_historical_bars_provider_probe_latest.txt
└── strategy_candidates/
    ├── candidate_20260706_144431_8a545b3c.json
    ├── candidate_20260706_145350_816903d1.json
    ├── candidate_20260706_150540_4fc7b8ab.json
    ├── candidate_20260706_151330_9f852272.json
    ├── candidate_20260706_152354_e2129e4e.json
    ├── candidate_20260706_152930_73031c40.json
    ├── candidate_20260706_171550_aca89979.json
    ├── candidate_20260706_171803_7979fee4.json
    ├── candidate_20260706_171835_2412645f.json
    ├── candidate_20260706_190850_245c152e.json
    ├── candidate_20260706_190919_18dff139.json
    ├── candidate_20260706_190955_47174fc4.json
    ├── candidate_20260706_201713_2d8f8e9e.json
    ├── candidate_20260706_201808_d90bd687.json
    ├── candidate_20260706_221600_b8f7600a.json
    ├── candidate_20260706_234404_20bfeb59.json
    ├── review_index_latest.json
    └── review_index_latest.txt
```

---

# 10. [Repository Topology] Audit Tree

Source: `handoff/audit_tree.txt`

```text
audit MISSING
```

---

# 11. [Layer Architecture] Canonical Layer Map

Source: `handoff/canonical_layer_map.txt`

```text
{
  "L0_external_adapter": {
    "file_count": 52,
    "sample_files": [
      "scripts/phase30g_yfinance_historical_bars_adapter_wire.py",
      "scripts/phase30a_yfinance_historical_bars_provider_probe_certification.py",
      "scripts/phase2_yfinance_market_warehouse.py",
      "scripts/phase30a_yfinance_historical_bars_provider_probe.py",
      "scripts/phase30e_yfinance_historical_bars_adapter_shape_validation.py",
      "scripts/phase30b_yfinance_provider_selection_snapshot.py",
      "scripts/phase30f_yfinance_historical_bars_adapter_wire_preview_certification.py",
      "scripts/phase30d_yfinance_historical_bars_adapter_stub_certification.py",
      "scripts/phase30f_yfinance_historical_bars_adapter_wire_preview.py",
      "scripts/phase29g_historical_replay_provider_readiness_snapshot.py",
      "scripts/phase30g_yfinance_historical_bars_adapter_wire_certification.py",
      "scripts/phase29f_historical_replay_provider_adapter_stub.py",
      "scripts/phase29e_historical_replay_market_data_provider_contract_certification.py",
      "scripts/phase29f_historical_replay_provider_adapter_stub_certification.py",
      "scripts/phase29e_historical_replay_market_data_provider_contract.py",
      "scripts/phase30d_yfinance_historical_bars_adapter_stub.py",
      "scripts/phase30e_yfinance_historical_bars_adapter_shape_validation_certification.py",
      "backend/app/snaptrade/executions/config.py",
      "backend/app/snaptrade/executions/execution_layer.py",
      "backend/app/stacks/chat_public/ollama_chat_client.py",
      "backend/app/stacks/market_data/yfinance_ingestor.py",
      "backend/app/stacks/market_data/provider_registry.py",
      "backend/app/stacks/market_data/provider_router.py",
      "backend/app/stacks/market_data/yfinance_historical_bars_adapter.py",
      "backend/app/stacks/market_data/provider_cache.py",
      "backend/app/stacks/snaptrade/__init__.py",
      "backend/app/stacks/snaptrade/execution.py",
      "backend/app/stacks/snaptrade/adapter.py",
      "backend/app/stacks/snaptrade/broker.py",
      "backend/app/stacks/snaptrade/base.py",
      "runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_stub_latest.json",
      "runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_shape_validation_latest.txt",
      "runtime/strategy_candidate_sandbox/historical_replay_market_data_provider_contract_v1.txt",
      "runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_stub_latest.txt",
      "runtime/strategy_candidate_sandbox/historical_replay_market_data_provider_contract_v1.json",
      "runtime/strategy_candidate_sandbox/historical_replay_provider_adapter_stub_latest.json",
      "runtime/strategy_candidate_sandbox/yfinance_historical_bars_provider_probe_latest.json",
      "runtime/strategy_candidate_sandbox/yfinance_historical_bars_provider_probe_latest.txt",
      "runtime/strategy_candidate_sandbox/historical_replay_provider_adapter_stub_latest.txt",
      "runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_wire_preview_latest.json",
      "runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_wire_preview_latest.txt",
      "runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_shape_validation_latest.json",
      "runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_wire_latest.json",
      "runtime/certifications/phase30f_yfinance_historical_bars_adapter_wire_preview_certification_latest.json",
      "runtime/certifications/phase30b_yfinance_provider_selection_snapshot_latest.json",
      "runtime/certifications/phase29e_historical_replay_market_data_provider_contract_certification_latest.json",
      "runtime/certifications/phase29g_historical_replay_provider_readiness_snapshot_latest.json",
      "runtime/certifications/phase30a_yfinance_historical_bars_provider_probe_certification_latest.json",
      "runtime/certifications/phase29f_historical_replay_provider_adapter_stub_certification_latest.json",
      "runtime/certifications/phase30g_yfinance_historical_bars_adapter_wire_certification_latest.json"
    ]
  },
  "L1_security_auth_safety": {
    "file_count": 68,
    "sample_files": [
      "scripts/phase52b_qwen_read_only_final_guardrail_summary_rollup_certification.py",
      "scripts/phase36a_strategy_rule_enablement_gate_contract_stub.py",
      "scripts/phase39b_master_sandbox_gate_wiregraph_rollup_certification.py",
      "scripts/phase36b_enablement_gate_validation_stub.py",
      "scripts/phase45a_qwen_read_only_architecture_summary_gate_stub.py",
      "scripts/phase15_risk_gate_service_chain.py",
      "scripts/phase37a_trade_simulation_enablement_gate_contract_stub.py",
      "scripts/phase39a_master_sandbox_gate_wiregraph_refresh.py",
      "scripts/phase15g_add_risk_chain_to_dashboard.py",
      "scripts/phase37b_trade_simulation_enablement_gate_validation_stub.py",
      "scripts/phase38b_risk_gate_validation_stub.py",
      "scripts/phase15e_risk_service_chain_graph_export.py",
      "scripts/phase38c_risk_gate_pipeline_rollup_certification.py",
      "scripts/phase15g_risk_chain_dashboard_certification.py",
      "scripts/phase45b_qwen_read_only_architecture_summary_gate_rollup_certification.py",
      "scripts/phase26c_chat_safety_prompt_live_execution_guard_certification.py",
      "scripts/phase52a_qwen_read_only_final_guardrail_summary_stub.py",
      "scripts/phase15f_risk_gate_service_chain_certification.py",
      "scripts/phase38a_risk_gate_contract_stub.py",
      "scripts/phase36c_enablement_gate_pipeline_rollup_certification.py",
      "scripts/phase32c_manual_promotion_gate_stub.py",
      "scripts/phase37c_trade_simulation_enablement_gate_pipeline_rollup_certification.py",
      "frontend/services/riskService.ts",
      "frontend/app/api/v1/risk/gate/[symbol]/route.ts",
      "backend/app/stacks/auth_identity/__init__.py",
      "backend/app/stacks/auth_identity/base.py",
      "backend/app/stacks/auth_identity/validator.py",
      "backend/app/stacks/auth_identity/gate.py",
      "backend/app/stacks/strategy_candidate_sandbox/strategy_rule_enablement_gate_contract.py",
      "backend/app/stacks/strategy_candidate_sandbox/qwen_read_only_architecture_summary_gate.py",
      "backend/app/stacks/strategy_candidate_sandbox/trade_simulation_enablement_gate_contract.py",
      "backend/app/stacks/strategy_candidate_sandbox/risk_gate_validator.py",
      "backend/app/stacks/strategy_candidate_sandbox/strategy_rule_enablement_gate_validator.py",
      "backend/app/stacks/strategy_candidate_sandbox/manual_promotion_gate.py",
      "backend/app/stacks/strategy_candidate_sandbox/trade_simulation_enablement_gate_validator.py",
      "backend/app/stacks/strategy_candidate_sandbox/risk_gate_contract.py",
      "backend/app/stacks/risk/loss_streak_guard.py",
      "backend/app/stacks/risk/__init__.py",
      "backend/app/stacks/risk/drawdown_guard.py",
      "backend/app/stacks/risk/risk_runtime_service.py",
      "backend/app/stacks/risk/exposure.py",
      "backend/app/stacks/risk/kill_switch.py",
      "backend/app/stacks/risk/limits.py",
      "backend/app/stacks/risk/base.py",
      "backend/app/stacks/risk/risk_service.py",
      "runtime/strategy_candidate_sandbox/39B_master_sandbox_gate_wiregraph_rollup_certification_latest.json",
      "runtime/strategy_candidate_sandbox/45B_qwen_read_only_architecture_summary_gate_rollup_certification_latest.json",
      "runtime/strategy_candidate_sandbox/45A_qwen_read_only_architecture_summary_gate_stub_latest.json",
      "runtime/strategy_candidate_sandbox/36C_enablement_gate_pipeline_rollup_certification_latest.json",
      "runtime/strategy_candidate_sandbox/39A_master_sandbox_gate_wiregraph_latest.mmd"
    ]
  },
  "L2_domain": {
    "file_count": 243,
    "sample_files": [
      "domain_subsystem_graph.png",
      "domain_runtime_overlay_graph.png",
      "scripts/phase35a_exit_signal_rule_contract_stub.py",
      "scripts/phase27a_strategy_proposal_capture_certification.py",
      "scripts/phase29b_historical_replay_input_contract_certification.py",
      "scripts/phase31f_replay_metrics_contract.py",
      "scripts/phase43b_qwen_context_response_contract_rollup_certification.py",
      "scripts/phase33d_entry_exit_signal_contract_stub.py",
      "scripts/phase27b_strategy_candidate_review_index.py",
      "scripts/phase35c_exit_signal_generator_disabled_stub.py",
      "scripts/phase35d_exit_signal_pipeline_rollup_certification.py",
      "scripts/phase34b_entry_signal_rule_validation_stub.py",
      "scripts/phase10_domain_subsystem_visualization.py",
      "scripts/phase35e_strategy_sandbox_wiregraph_certification.py",
      "scripts/phase34d_entry_signal_pipeline_rollup_certification.py",
      "scripts/phase14e_strategy_service_chain_graph_export.py",
      "scripts/phase49a_qwen_read_only_architecture_session_contract_stub.py",
      "scripts/phase27b_strategy_candidate_review_index_certification.py",
      "scripts/phase14f_strategy_decision_service_chain_certification.py",
      "scripts/phase14g_strategy_chain_dashboard_certification.py",
      "scripts/phase14g_add_strategy_chain_to_dashboard.py",
      "scripts/phase33e_hold_signal_generator_stub.py",
      "scripts/phase34c_entry_signal_generator_disabled_stub.py",
      "scripts/phase43a_qwen_context_response_contract_stub.py",
      "scripts/phase29b_historical_replay_input_contract.py",
      "scripts/phase30c_historical_bars_contract.py",
      "scripts/phase28d_candidate_sandbox_execution_contract_certification.py",
      "scripts/phase10c_domain_runtime_overlay_visualization.py",
      "scripts/phase27a_strategy_proposal_capture.py",
      "scripts/phase28d_candidate_sandbox_execution_contract.py",
      "scripts/phase30c_historical_bars_contract_certification.py",
      "scripts/phase35b_exit_signal_rule_validation_stub.py",
      "scripts/phase14_strategy_decision_service_chain.py",
      "scripts/phase49b_qwen_read_only_architecture_session_contract_rollup_certification.py",
      "scripts/phase33a_trade_simulation_contract_stub.py",
      "scripts/phase10_domain_subsystem_visualization_certification.py",
      "scripts/phase34a_entry_signal_rule_contract_stub.py",
      "scripts/phase9k_domain_subsystem_graph_export.py",
      "frontend/services/strategyService.ts",
      "frontend/app/api/v1/strategy/decision/[symbol]/route.ts",
      "backend/app/stacks/strategy/strategy_registry.py",
      "backend/app/stacks/strategy/strategy_service.py",
      "backend/app/stacks/strategy/strategy_runtime.py",
      "backend/app/stacks/strategy/__init__.py",
      "backend/app/stacks/strategy/selector.py",
      "backend/app/stacks/strategy/signal.py",
      "backend/app/stacks/strategy/engine.py",
      "backend/app/stacks/strategy/evolution_engine.py",
      "backend/app/stacks/strategy/llm_strategy_engine.py",
      "backend/app/stacks/strategy/candidate_registry.py"
    ]
  },
  "L3_service_facade": {
    "file_count": 36,
    "sample_files": [
      "SERVICE_RELOCATION_PLAN_RECONCILED.json",
      "SERVICE_RELOCATION_PLAN.json",
      "architecture_backup/dashboard_service.py",
      "scripts/phase13f_portfolio_positions_service_chain_certification.py",
      "scripts/phase12g_service_chain_repair.py",
      "scripts/phase21_fix_chat_service_generator.py",
      "scripts/phase12_service_layer_alignment.py",
      "scripts/phase12g_service_chain_dashboard_certification.py",
      "scripts/phase12f_service_chain_certification.py",
      "scripts/phase13e_portfolio_service_chain_graph_export.py",
      "scripts/phase20_floating_chat_widget_service_chain.py",
      "scripts/phase13_portfolio_positions_service_chain.py",
      "scripts/apply_service_relocation_v1.py",
      "scripts/phase12g_add_service_chain_to_dashboard.py",
      "scripts/service_stack_relocator_v1.py",
      "scripts/phase12e_service_chain_graph_export.py",
      "scripts/phase20e_chat_service_chain_graph_export.py",
      "frontend/services/observabilityTimelineService.ts",
      "frontend/services/graphService.ts",
      "frontend/services/marketService.ts",
      "frontend/services/requestNormalizer.ts",
      "frontend/services/chatService.ts",
      "frontend/services/requestObservability.ts",
      "frontend/services/backendHealthService.ts",
      "frontend/services/portfolioService.ts",
      "backend/app/services/__init__.py",
      "backend/app/stacks/portfolio/portfolio_service.py",
      "backend/app/stacks/portfolio/dashboard_service.py",
      "backend/app/stacks/chat_public/chat_service.py",
      "backend/app/stacks/market_data/market_data_service.py",
      "runtime/certifications/phase12g_service_chain_dashboard_certification_latest.json",
      "runtime/certifications/phase13f_portfolio_positions_service_chain_certification_latest.json",
      "runtime/certifications/phase12f_service_chain_certification_latest.json",
      "runtime/repo_memory/service_chain_graph_v1.json",
      "runtime/repo_memory/chat_service_chain_graph_v1.json",
      "runtime/repo_memory/portfolio_service_chain_graph_v1.json"
    ]
  },
  "L4_runtime_orchestration": {
    "file_count": 112,
    "sample_files": [
      "scripts/phase10d_runtime_static_dependency_diff_certification.py",
      "scripts/phase40b_sandbox_runtime_dependency_trace_rollup_certification.py",
      "scripts/phase40a_sandbox_runtime_dependency_trace_stub.py",
      "scripts/phase10c_runtime_flow_overlay_export.py",
      "scripts/phase10e_classify_runtime_static_diff_edges.py",
      "scripts/phase10c_runtime_flow_overlay_certification.py",
      "scripts/phase26b_wire_ollama_into_chat_runtime.py",
      "scripts/phase10d_runtime_static_dependency_diff.py",
      "scripts/phase62a_master_architecture_handoff_controller.py",
      "backend/app/core/runtime_firewall_v1.py",
      "backend/app/stacks/portfolio/portfolio_runtime.py",
      "backend/app/stacks/execution/sandbox_runtime.py",
      "backend/app/stacks/wolfden_ai/orchestrator.py",
      "backend/app/stacks/wolfden_ai/runtime.py",
      "backend/app/stacks/chat_public/chat_runtime.py",
      "backend/app/stacks/learning_research/research_runtime.py",
      "runtime/market_warehouse/symbol_registry.json",
      "runtime/handoff_snapshot/live_graph_validate_latest.json",
      "runtime/handoff_snapshot/file_manifest_latest.txt",
      "runtime/handoff_snapshot/topology_tree_latest.txt",
      "runtime/handoff_snapshot/neurovest_training_handoff_bundle_latest.json",
      "runtime/certifications/phase11_live_market_price_api_bridge_certification_latest.json",
      "runtime/certifications/phase22b_live_graph_visualization_certification_latest.json",
      "runtime/certifications/phase25b_tab_layout_polish_chat_panel_certification_latest.json",
      "runtime/certifications/phase17_dashboard_route_map_certification_latest.json",
      "runtime/certifications/phase10d_runtime_static_dependency_diff_certification_latest.json",
      "runtime/certifications/phase22_live_graph_tab_certification_latest.json",
      "runtime/certifications/phase28a_candidate_sandbox_simulation_harness_stub_certification_latest.json",
      "runtime/certifications/phase25c_split_dashboard_panels_into_tab_workspaces_certification_latest.json",
      "runtime/certifications/phase19c_endpoint_activation_certification_latest.json",
      "runtime/certifications/phase3m_graph_certification_latest.json",
      "runtime/certifications/phase5c_repo_memory_certification_v2_latest.json",
      "runtime/certifications/phase25a_dashboard_tab_shell_layout_navigation_certification_latest.json",
      "runtime/certifications/phase26e_chat_metadata_chips_typing_enter_certification_latest.json",
      "runtime/certifications/phase27e_candidate_sandbox_result_stub_generator_certification_latest.json",
      "runtime/certifications/phase27f_candidate_sandbox_readiness_lock_snapshot_latest.json",
      "runtime/certifications/phase24b_persist_observability_backend_health_certification_latest.json",
      "runtime/certifications/phase18_real_positions_panel_certification_latest.json",
      "runtime/certifications/phase21ab_chat_cache_history_certification_latest.json",
      "runtime/certifications/phase11f_frontend_type_lint_repair_certification_latest.json",
      "runtime/certifications/phase11c_frontend_polling_api_cleanup_certification_latest.json",
      "runtime/certifications/phase20f_floating_chat_widget_certification_latest.json",
      "runtime/certifications/phase10h_architecture_dashboard_command_certification_latest.json",
      "runtime/certifications/phase6d_dependency_graph_certification_latest.json",
      "runtime/certifications/phase23a_frontend_request_normalizer_certification_latest.json",
      "runtime/certifications/phase26d_frontend_chat_response_normalizer_certification_latest.json",
      "runtime/certifications/phase27d_candidate_sandbox_result_schema_certification_latest.json",
      "runtime/certifications/phase10e_diff_classification_certification_latest.json",
      "runtime/certifications/phase29d_historical_replay_readiness_snapshot_latest.json",
      "runtime/certifications/phase11g_live_market_dashboard_expansion_certification_latest.json"
    ]
  },
  "L5_api_presentation": {
    "file_count": 20,
    "sample_files": [
      "scripts/phase11c_frontend_polling_api_cleanup.py",
      "scripts/phase26a_chat_intent_regex_ollama_router.py",
      "scripts/phase11d_next_api_proxy_live_price.py",
      "scripts/phase11_live_market_price_api_bridge_certification.py",
      "scripts/phase11_live_market_price_api_bridge.py",
      "scripts/phase19b_endpoint_activation_probe_repair.py",
      "scripts/phase11d_next_api_proxy_live_price_certification.py",
      "scripts/phase19c_endpoint_activation_certification.py",
      "scripts/phase17_dashboard_route_map_frontend_card_verification.py",
      "scripts/phase16_api_route_separation_certification.py",
      "scripts/phase17_dashboard_route_map_certification.py",
      "scripts/phase11c_frontend_polling_api_cleanup_certification.py",
      "frontend/app/api/v1/chat/route.ts",
      "frontend/app/api/v1/graph/live/route.ts",
      "frontend/app/api/v1/market/live-price/[symbol]/route.ts",
      "frontend/app/api/v1/portfolio/positions/route.ts",
      "backend/app/api/graph_ws.py",
      "backend/app/routers/__init__.py",
      "backend/app/stacks/wolfden_ai/agent_router.py",
      "backend/app/stacks/chat_public/chat_api.py"
    ]
  },
  "L6_frontend": {
    "file_count": 104,
    "sample_files": [
      "cursor.AppImage",
      "scripts/phase23a_frontend_request_normalizer_certification.py",
      "scripts/phase26d_frontend_chat_response_normalizer_certification.py",
      "scripts/phase18_real_positions_panel_component.py",
      "scripts/phase23a_frontend_request_normalizer.py",
      "scripts/phase24a_frontend_observability_dashboard.py",
      "scripts/phase9b_component_overlay_export.py",
      "scripts/phase11f_frontend_type_lint_repair.py",
      "scripts/phase26d_frontend_chat_response_normalizer.py",
      "scripts/phase11e_frontend_build_type_certification.py",
      "scripts/phase11b_frontend_live_price_card_certification.py",
      "scripts/phase11f_frontend_type_lint_repair_certification.py",
      "scripts/phase11b_frontend_live_price_card.py",
      "scripts/phase24a_frontend_observability_dashboard_certification.py",
      "frontend/next-env.d.ts",
      "frontend/package-lock.json",
      "frontend/CLAUDE.md",
      "frontend/next.config.ts",
      "frontend/eslint.config.mjs",
      "frontend/tsconfig.json",
      "frontend/postcss.config.mjs",
      "frontend/README.md",
      "frontend/.gitignore",
      "frontend/package.json",
      "frontend/AGENTS.md",
      "frontend/app/globals.css",
      "frontend/app/layout.tsx",
      "frontend/app/page.tsx",
      "frontend/app/favicon.ico",
      "frontend/public/window.svg",
      "frontend/public/file.svg",
      "frontend/public/vercel.svg",
      "frontend/public/globe.svg",
      "frontend/public/next.svg",
      "backend/app/main.py",
      "backend/app/__init__.py",
      "backend/app/schemas/__init__.py",
      "backend/app/schemas/dashboard.py",
      "backend/app/test/test_neuro_repo_companion.py",
      "backend/app/test/test_trading_pipeline.py",
      "backend/app/analysis/architecture.py",
      "backend/app/core/cognitive_nodes.py",
      "backend/app/core/__init__.py",
      "backend/app/core/cognitive_types.py",
      "backend/app/core/config.py",
      "backend/app/core/cognitive_graph_state.py",
      "backend/app/core/cognitive_event_bus.py",
      "backend/app/core/global_firewall_v1.py",
      "backend/app/stacks/__init__.py",
      "backend/app/stacks/registry.json"
    ]
  },
  "L7_tests": {
    "file_count": 4,
    "sample_files": [
      "neuro_cli_file_inspection.json",
      "pytest.ini",
      "scripts/phase41a_safe_read_only_architecture_inspector_stub.py",
      "scripts/phase41b_safe_read_only_architecture_inspector_rollup_certification.py"
    ]
  },
  "UNCLASSIFIED": {
    "file_count": 188,
    "sample_files": [
      "OUTPUT",
      "ARCHITECTURE_REPAIR_PLAN.json",
      "TOPOLOGY_NORMALIZED_STATE.json",
      "ARCH_GOVERNANCE.md",
      "fix_phase9_self_fingerprint.sh",
      "TOPOLOGY_STATE.json",
      "topology_wire_graph.png",
      "neurovest_repo_context.md",
      "Directory Structure",
      "ORPHAN_RESOLUTION_PLAN.json",
      "topology_wire_graph_canonical.png",
      ".env.example",
      "generate_wire_graph.py",
      "neuro_health.sh",
      ".aider.input.history",
      "FINAL_ARCHITECTURE_STATE.json",
      "system_tree.txt",
      "docker-compose.yml",
      "ARCH_ENFORCEMENT_REPORT.json",
      "spine_mvp_full.sh",
      ".gitignore",
      "$OUTPUT",
      ".env",
      ".aider.chat.history.md",
      "neuro",
      "neuro_cli.py",
      "neuro_engineer.py",
      "scripts/phase59b_qwen_read_only_final_handoff_certification_rollup_certification.py",
      "scripts/phase22_live_graph_tab_certification.py",
      "scripts/phase20f_floating_chat_widget_certification.py",
      "scripts/phase48c_handoff_bundle_refresh.py",
      "scripts/phase51a_qwen_read_only_architecture_loop_boundary_stub.py",
      "scripts/phase23b_polling_governor_certification.py",
      "scripts/phase29c_historical_replay_validation_stub.py",
      "scripts/phase26f_chat_ui_state_cleanup_metadata_rendering_certification.py",
      "scripts/phase6c_dependency_graph_export.py",
      "scripts/phase25a_dashboard_tab_shell_layout_navigation_certification.py",
      "scripts/phase27d_candidate_sandbox_result_schema_certification.py",
      "scripts/phase10h_architecture_dashboard_command_certification.py",
      "scripts/phase31a_historical_bars_fetch_validation.py",
      "scripts/phase27e_candidate_sandbox_result_stub_generator.py",
      "scripts/phase54a_qwen_read_only_handoff_export_summary_stub.py",
      "scripts/phase26f_chat_ui_state_cleanup_metadata_rendering.py",
      "scripts/phase4g_repo_memory_certification.py",
      "scripts/phase25a_dashboard_tab_shell_layout_navigation.py",
      "scripts/phase21cd_chat_ux_persistent_cache.py",
      "scripts/phase47b_qwen_read_only_recommendation_filter_rollup_certification.py",
      "scripts/phase11g_live_market_dashboard_expansion.py",
      "scripts/phase28b_candidate_sandbox_mock_metrics_generator.py",
      "scripts/phase32a_real_metrics_generation.py"
    ]
  }
}
```

---

# 12. [Layer Architecture] Layer Ownership

Source: `handoff/project_bible/architecture_atlas/LAYER_OWNERSHIP.md`

## L0_external_adapter

External providers and adapters only.
Files detected: 52

- `scripts/phase30g_yfinance_historical_bars_adapter_wire.py`
- `scripts/phase30a_yfinance_historical_bars_provider_probe_certification.py`
- `scripts/phase2_yfinance_market_warehouse.py`
- `scripts/phase30a_yfinance_historical_bars_provider_probe.py`
- `scripts/phase30e_yfinance_historical_bars_adapter_shape_validation.py`
- `scripts/phase30b_yfinance_provider_selection_snapshot.py`
- `scripts/phase30f_yfinance_historical_bars_adapter_wire_preview_certification.py`
- `scripts/phase30d_yfinance_historical_bars_adapter_stub_certification.py`
- `scripts/phase30f_yfinance_historical_bars_adapter_wire_preview.py`
- `scripts/phase29g_historical_replay_provider_readiness_snapshot.py`
- `scripts/phase30g_yfinance_historical_bars_adapter_wire_certification.py`
- `scripts/phase29f_historical_replay_provider_adapter_stub.py`
- `scripts/phase29e_historical_replay_market_data_provider_contract_certification.py`
- `scripts/phase29f_historical_replay_provider_adapter_stub_certification.py`
- `scripts/phase29e_historical_replay_market_data_provider_contract.py`

## L1_security_auth_safety

Auth, gates, guards, firewalls, locked safety contracts.
Files detected: 68

- `scripts/phase52b_qwen_read_only_final_guardrail_summary_rollup_certification.py`
- `scripts/phase36a_strategy_rule_enablement_gate_contract_stub.py`
- `scripts/phase39b_master_sandbox_gate_wiregraph_rollup_certification.py`
- `scripts/phase36b_enablement_gate_validation_stub.py`
- `scripts/phase45a_qwen_read_only_architecture_summary_gate_stub.py`
- `scripts/phase15_risk_gate_service_chain.py`
- `scripts/phase37a_trade_simulation_enablement_gate_contract_stub.py`
- `scripts/phase39a_master_sandbox_gate_wiregraph_refresh.py`
- `scripts/phase15g_add_risk_chain_to_dashboard.py`
- `scripts/phase37b_trade_simulation_enablement_gate_validation_stub.py`
- `scripts/phase38b_risk_gate_validation_stub.py`
- `scripts/phase15e_risk_service_chain_graph_export.py`
- `scripts/phase38c_risk_gate_pipeline_rollup_certification.py`
- `scripts/phase15g_risk_chain_dashboard_certification.py`
- `scripts/phase45b_qwen_read_only_architecture_summary_gate_rollup_certification.py`

## L2_domain

Pure business/domain logic and contracts.
Files detected: 243

- `domain_subsystem_graph.png`
- `domain_runtime_overlay_graph.png`
- `scripts/phase35a_exit_signal_rule_contract_stub.py`
- `scripts/phase27a_strategy_proposal_capture_certification.py`
- `scripts/phase29b_historical_replay_input_contract_certification.py`
- `scripts/phase31f_replay_metrics_contract.py`
- `scripts/phase43b_qwen_context_response_contract_rollup_certification.py`
- `scripts/phase33d_entry_exit_signal_contract_stub.py`
- `scripts/phase27b_strategy_candidate_review_index.py`
- `scripts/phase35c_exit_signal_generator_disabled_stub.py`
- `scripts/phase35d_exit_signal_pipeline_rollup_certification.py`
- `scripts/phase34b_entry_signal_rule_validation_stub.py`
- `scripts/phase10_domain_subsystem_visualization.py`
- `scripts/phase35e_strategy_sandbox_wiregraph_certification.py`
- `scripts/phase34d_entry_signal_pipeline_rollup_certification.py`

## L3_service_facade

Stable services coordinating domain/adapters.
Files detected: 36

- `SERVICE_RELOCATION_PLAN_RECONCILED.json`
- `SERVICE_RELOCATION_PLAN.json`
- `architecture_backup/dashboard_service.py`
- `scripts/phase13f_portfolio_positions_service_chain_certification.py`
- `scripts/phase12g_service_chain_repair.py`
- `scripts/phase21_fix_chat_service_generator.py`
- `scripts/phase12_service_layer_alignment.py`
- `scripts/phase12g_service_chain_dashboard_certification.py`
- `scripts/phase12f_service_chain_certification.py`
- `scripts/phase13e_portfolio_service_chain_graph_export.py`
- `scripts/phase20_floating_chat_widget_service_chain.py`
- `scripts/phase13_portfolio_positions_service_chain.py`
- `scripts/apply_service_relocation_v1.py`
- `scripts/phase12g_add_service_chain_to_dashboard.py`
- `scripts/service_stack_relocator_v1.py`

## L4_runtime_orchestration

Controllers, schedulers, runtime orchestration.
Files detected: 112

- `scripts/phase10d_runtime_static_dependency_diff_certification.py`
- `scripts/phase40b_sandbox_runtime_dependency_trace_rollup_certification.py`
- `scripts/phase40a_sandbox_runtime_dependency_trace_stub.py`
- `scripts/phase10c_runtime_flow_overlay_export.py`
- `scripts/phase10e_classify_runtime_static_diff_edges.py`
- `scripts/phase10c_runtime_flow_overlay_certification.py`
- `scripts/phase26b_wire_ollama_into_chat_runtime.py`
- `scripts/phase10d_runtime_static_dependency_diff.py`
- `scripts/phase62a_master_architecture_handoff_controller.py`
- `backend/app/core/runtime_firewall_v1.py`
- `backend/app/stacks/portfolio/portfolio_runtime.py`
- `backend/app/stacks/execution/sandbox_runtime.py`
- `backend/app/stacks/wolfden_ai/orchestrator.py`
- `backend/app/stacks/wolfden_ai/runtime.py`
- `backend/app/stacks/chat_public/chat_runtime.py`

## L5_api_presentation

API routes and presentation only.
Files detected: 20

- `scripts/phase11c_frontend_polling_api_cleanup.py`
- `scripts/phase26a_chat_intent_regex_ollama_router.py`
- `scripts/phase11d_next_api_proxy_live_price.py`
- `scripts/phase11_live_market_price_api_bridge_certification.py`
- `scripts/phase11_live_market_price_api_bridge.py`
- `scripts/phase19b_endpoint_activation_probe_repair.py`
- `scripts/phase11d_next_api_proxy_live_price_certification.py`
- `scripts/phase19c_endpoint_activation_certification.py`
- `scripts/phase17_dashboard_route_map_frontend_card_verification.py`
- `scripts/phase16_api_route_separation_certification.py`
- `scripts/phase17_dashboard_route_map_certification.py`
- `scripts/phase11c_frontend_polling_api_cleanup_certification.py`
- `frontend/app/api/v1/chat/route.ts`
- `frontend/app/api/v1/graph/live/route.ts`
- `frontend/app/api/v1/market/live-price/[symbol]/route.ts`

## L6_frontend

Next.js UI and client services.
Files detected: 104

- `cursor.AppImage`
- `scripts/phase23a_frontend_request_normalizer_certification.py`
- `scripts/phase26d_frontend_chat_response_normalizer_certification.py`
- `scripts/phase18_real_positions_panel_component.py`
- `scripts/phase23a_frontend_request_normalizer.py`
- `scripts/phase24a_frontend_observability_dashboard.py`
- `scripts/phase9b_component_overlay_export.py`
- `scripts/phase11f_frontend_type_lint_repair.py`
- `scripts/phase26d_frontend_chat_response_normalizer.py`
- `scripts/phase11e_frontend_build_type_certification.py`
- `scripts/phase11b_frontend_live_price_card_certification.py`
- `scripts/phase11f_frontend_type_lint_repair_certification.py`
- `scripts/phase11b_frontend_live_price_card.py`
- `scripts/phase24a_frontend_observability_dashboard_certification.py`
- `frontend/next-env.d.ts`

## L7_tests

Tests, fixtures, probes, validation.
Files detected: 4

- `neuro_cli_file_inspection.json`
- `pytest.ini`
- `scripts/phase41a_safe_read_only_architecture_inspector_stub.py`
- `scripts/phase41b_safe_read_only_architecture_inspector_rollup_certification.py`

## UNCLASSIFIED

Needs future classification; do not assume ownership.
Files detected: 188

- `OUTPUT`
- `ARCHITECTURE_REPAIR_PLAN.json`
- `TOPOLOGY_NORMALIZED_STATE.json`
- `ARCH_GOVERNANCE.md`
- `fix_phase9_self_fingerprint.sh`
- `TOPOLOGY_STATE.json`
- `topology_wire_graph.png`
- `neurovest_repo_context.md`
- `Directory Structure`
- `ORPHAN_RESOLUTION_PLAN.json`
- `topology_wire_graph_canonical.png`
- `.env.example`
- `generate_wire_graph.py`
- `neuro_health.sh`
- `.aider.input.history`

---

# 13. [Stack Architecture] Stack Topology

Source: `handoff/stack_topology.txt`

```text
{
  "auth": {
    "file_count": 4,
    "sample_files": [
      "backend/app/stacks/auth_identity/__init__.py",
      "backend/app/stacks/auth_identity/base.py",
      "backend/app/stacks/auth_identity/validator.py",
      "backend/app/stacks/auth_identity/gate.py"
    ]
  },
  "backend_uncategorized": {
    "file_count": 27,
    "sample_files": [
      "backend/__init__.py",
      "backend/requirements.txt",
      "backend/app/main.py",
      "backend/app/__init__.py",
      "backend/scripts/backup_db.sh",
      "backend/app/schemas/__init__.py",
      "backend/app/schemas/dashboard.py",
      "backend/app/test/test_neuro_repo_companion.py",
      "backend/app/test/test_trading_pipeline.py",
      "backend/app/api/graph_ws.py",
      "backend/app/services/__init__.py",
      "backend/app/analysis/architecture.py",
      "backend/app/core/cognitive_nodes.py",
      "backend/app/core/__init__.py",
      "backend/app/core/cognitive_types.py",
      "backend/app/core/config.py",
      "backend/app/core/cognitive_graph_state.py",
      "backend/app/core/cognitive_event_bus.py",
      "backend/app/core/runtime_firewall_v1.py",
      "backend/app/core/global_firewall_v1.py",
      "backend/app/stacks/__init__.py",
      "backend/app/stacks/registry.json",
      "backend/app/routers/__init__.py",
      "backend/app/stacks/db_model/__init__.py",
      "backend/app/stacks/db_model/market_schema.py",
      "backend/app/stacks/db_model/base.py",
      "backend/app/stacks/events/broker.py"
    ]
  },
  "chat": {
    "file_count": 43,
    "sample_files": [
      ".aider.chat.history.md",
      "scripts/phase20f_floating_chat_widget_certification.py",
      "scripts/phase26f_chat_ui_state_cleanup_metadata_rendering_certification.py",
      "scripts/phase26d_frontend_chat_response_normalizer_certification.py",
      "scripts/phase26f_chat_ui_state_cleanup_metadata_rendering.py",
      "scripts/phase21cd_chat_ux_persistent_cache.py",
      "scripts/phase21_fix_chat_service_generator.py",
      "scripts/phase26a_chat_intent_regex_ollama_router.py",
      "scripts/phase26e_chat_metadata_chips_typing_enter_certification.py",
      "scripts/phase20_floating_chat_widget_service_chain.py",
      "scripts/phase21cd_chat_ux_persistent_cache_certification.py",
      "scripts/phase26b_wire_ollama_into_chat_runtime.py",
      "scripts/phase25b_tab_layout_polish_chat_panel.py",
      "scripts/phase26d_frontend_chat_response_normalizer.py",
      "scripts/phase21ab_chat_cache_history_certification.py",
      "scripts/phase61a_archive_or_new_chat_handoff_summary.py",
      "scripts/phase26e_chat_metadata_chips_typing_enter.py",
      "scripts/phase21ab_chat_cache_history.py",
      "scripts/phase20e_chat_service_chain_graph_export.py",
      "scripts/phase25b_tab_layout_polish_chat_panel_certification.py",
      "frontend/services/chatService.ts",
      "frontend/app/api/v1/chat/route.ts",
      "backend/app/stacks/chat_public/chat_intent_regex.py",
      "backend/app/stacks/chat_public/context_loader.py",
      "backend/app/stacks/chat_public/__init__.py",
      "backend/app/stacks/chat_public/chat_runtime.py",
      "backend/app/stacks/chat_public/chat_system_prompt.py",
      "backend/app/stacks/chat_public/conversation_store.py",
      "backend/app/stacks/chat_public/chat_memory.py",
      "backend/app/stacks/chat_public/ollama_chat_client.py",
      "backend/app/stacks/chat_public/chat_service.py",
      "backend/app/stacks/chat_public/time_context.py",
      "backend/app/stacks/chat_public/strategy_proposal_capture.py",
      "backend/app/stacks/chat_public/base.py",
      "backend/app/stacks/chat_public/chat_api.py",
      "runtime/certifications/phase25b_tab_layout_polish_chat_panel_certification_latest.json",
      "runtime/certifications/phase26e_chat_metadata_chips_typing_enter_certification_latest.json",
      "runtime/certifications/phase21ab_chat_cache_history_certification_latest.json",
      "runtime/certifications/phase20f_floating_chat_widget_certification_latest.json",
      "runtime/certifications/phase26d_frontend_chat_response_normalizer_certification_latest.json"
    ]
  },
  "execution": {
    "file_count": 19,
    "sample_files": [
      "scripts/phase28d_candidate_sandbox_execution_contract_certification.py",
      "scripts/phase28d_candidate_sandbox_execution_contract.py",
      "scripts/phase26c_chat_safety_prompt_live_execution_guard_certification.py",
      "backend/app/stacks/execution/__init__.py",
      "backend/app/stacks/execution/sandbox_runtime.py",
      "backend/app/stacks/execution/commission_engine.py",
      "backend/app/stacks/execution/sandbox.py",
      "backend/app/stacks/execution/regime_modes.py",
      "backend/app/stacks/execution/pnl_engine.py",
      "backend/app/stacks/execution/executor.py",
      "backend/app/stacks/execution/trade_ledger.py",
      "backend/app/stacks/execution/regime_simulator.py",
      "backend/app/stacks/execution/paper_broker.py",
      "backend/app/stacks/execution/broker.py",
      "backend/app/stacks/execution/fill_engine.py",
      "backend/app/stacks/execution/base.py",
      "backend/app/stacks/execution/accounting_engine.py",
      "runtime/certifications/phase26c_chat_safety_prompt_live_execution_guard_certification_latest.json",
      "runtime/certifications/phase28d_candidate_sandbox_execution_contract_certification_latest.json"
    ]
  },
  "frontend": {
    "file_count": 28,
    "sample_files": [
      "frontend/next-env.d.ts",
      "frontend/package-lock.json",
      "frontend/CLAUDE.md",
      "frontend/next.config.ts",
      "frontend/eslint.config.mjs",
      "frontend/tsconfig.json",
      "frontend/postcss.config.mjs",
      "frontend/README.md",
      "frontend/.gitignore",
      "frontend/package.json",
      "frontend/AGENTS.md",
      "frontend/app/globals.css",
      "frontend/app/layout.tsx",
      "frontend/app/page.tsx",
      "frontend/app/favicon.ico",
      "frontend/services/observabilityTimelineService.ts",
      "frontend/services/graphService.ts",
      "frontend/services/marketService.ts",
      "frontend/services/requestNormalizer.ts",
      "frontend/services/requestObservability.ts",
      "frontend/services/backendHealthService.ts",
      "frontend/public/window.svg",
      "frontend/public/file.svg",
      "frontend/public/vercel.svg",
      "frontend/public/globe.svg",
      "frontend/public/next.svg",
      "frontend/app/api/v1/graph/live/route.ts",
      "frontend/app/api/v1/market/live-price/[symbol]/route.ts"
    ]
  },
  "journal": {
    "file_count": 4,
    "sample_files": [
      "backend/app/stacks/journal_ledger/ledger.py",
      "backend/app/stacks/journal_ledger/__init__.py",
      "backend/app/stacks/journal_ledger/record.py",
      "backend/app/stacks/journal_ledger/base.py"
    ]
  },
  "learning": {
    "file_count": 9,
    "sample_files": [
      "backend/app/stacks/learning_research/strategy_evaluator.py",
      "backend/app/stacks/learning_research/__init__.py",
      "backend/app/stacks/learning_research/monte_carlo_mix.py",
      "backend/app/stacks/learning_research/monte_carlo.py",
      "backend/app/stacks/learning_research/research_loader.py",
      "backend/app/stacks/learning_research/probability_engine.py",
      "backend/app/stacks/learning_research/research_runtime.py",
      "backend/app/stacks/learning_research/base.py",
      "backend/app/stacks/learning_research/backtest_engine.py"
    ]
  },
  "market_data": {
    "file_count": 15,
    "sample_files": [
      "scripts/phase29e_historical_replay_market_data_provider_contract_certification.py",
      "scripts/phase29e_historical_replay_market_data_provider_contract.py",
      "backend/app/stacks/market_data/yfinance_ingestor.py",
      "backend/app/stacks/market_data/provider_registry.py",
      "backend/app/stacks/market_data/__init__.py",
      "backend/app/stacks/market_data/feed.py",
      "backend/app/stacks/market_data/market_data_service.py",
      "backend/app/stacks/market_data/bars.py",
      "backend/app/stacks/market_data/market_session.py",
      "backend/app/stacks/market_data/provider_router.py",
      "backend/app/stacks/market_data/price.py",
      "backend/app/stacks/market_data/yfinance_historical_bars_adapter.py",
      "backend/app/stacks/market_data/provider_cache.py",
      "backend/app/stacks/market_data/base.py",
      "runtime/certifications/phase29e_historical_replay_market_data_provider_contract_certification_latest.json"
    ]
  },
  "notification": {
    "file_count": 2,
    "sample_files": [
      "backend/app/stacks/notification/__init__.py",
      "backend/app/stacks/notification/base.py"
    ]
  },
  "portfolio": {
    "file_count": 19,
    "sample_files": [
      "scripts/phase13f_portfolio_positions_service_chain_certification.py",
      "scripts/phase13e_portfolio_service_chain_graph_export.py",
      "scripts/phase13_portfolio_positions_service_chain.py",
      "scripts/phase13g_portfolio_chain_dashboard_certification.py",
      "scripts/phase13g_add_portfolio_chain_to_dashboard.py",
      "frontend/services/portfolioService.ts",
      "frontend/app/api/v1/portfolio/positions/route.ts",
      "backend/app/stacks/portfolio/portfolio_service.py",
      "backend/app/stacks/portfolio/allocator.py",
      "backend/app/stacks/portfolio/__init__.py",
      "backend/app/stacks/portfolio/accounting.py",
      "backend/app/stacks/portfolio/portfolio_runtime.py",
      "backend/app/stacks/portfolio/reconciliation.py",
      "backend/app/stacks/portfolio/dashboard_service.py",
      "backend/app/stacks/portfolio/rebalance.py",
      "backend/app/stacks/portfolio/base.py",
      "runtime/certifications/phase13f_portfolio_positions_service_chain_certification_latest.json",
      "runtime/certifications/phase13g_portfolio_chain_dashboard_certification_latest.json",
      "runtime/repo_memory/portfolio_service_chain_graph_v1.json"
    ]
  },
  "research": {
    "file_count": 2,
    "sample_files": [
      "scripts/phase1_repo_research_market_bootstrap.py",
      "runtime/research_db/research_seed.json"
    ]
  },
  "risk": {
    "file_count": 22,
    "sample_files": [
      "scripts/phase15_risk_gate_service_chain.py",
      "scripts/phase15g_add_risk_chain_to_dashboard.py",
      "scripts/phase38b_risk_gate_validation_stub.py",
      "scripts/phase15e_risk_service_chain_graph_export.py",
      "scripts/phase38c_risk_gate_pipeline_rollup_certification.py",
      "scripts/phase15g_risk_chain_dashboard_certification.py",
      "scripts/phase15f_risk_gate_service_chain_certification.py",
      "scripts/phase38a_risk_gate_contract_stub.py",
      "frontend/services/riskService.ts",
      "frontend/app/api/v1/risk/gate/[symbol]/route.ts",
      "backend/app/stacks/risk/loss_streak_guard.py",
      "backend/app/stacks/risk/__init__.py",
      "backend/app/stacks/risk/drawdown_guard.py",
      "backend/app/stacks/risk/risk_runtime_service.py",
      "backend/app/stacks/risk/exposure.py",
      "backend/app/stacks/risk/kill_switch.py",
      "backend/app/stacks/risk/limits.py",
      "backend/app/stacks/risk/base.py",
      "backend/app/stacks/risk/risk_service.py",
      "runtime/certifications/phase15g_risk_chain_dashboard_certification_latest.json",
      "runtime/certifications/phase15f_risk_gate_service_chain_certification_latest.json",
      "runtime/repo_memory/risk_service_chain_graph_v1.json"
    ]
  },
  "runtime_artifacts": {
    "file_count": 103,
    "sample_files": [
      "runtime/market_warehouse/symbol_registry.json",
      "runtime/handoff_snapshot/live_graph_validate_latest.json",
      "runtime/handoff_snapshot/file_manifest_latest.txt",
      "runtime/handoff_snapshot/simulate_trade_guard_latest.json",
      "runtime/handoff_snapshot/topology_tree_latest.txt",
      "runtime/handoff_snapshot/neurovest_training_handoff_bundle_latest.json",
      "runtime/certifications/phase11_live_market_price_api_bridge_certification_latest.json",
      "runtime/certifications/phase22b_live_graph_visualization_certification_latest.json",
      "runtime/certifications/phase30f_yfinance_historical_bars_adapter_wire_preview_certification_latest.json",
      "runtime/certifications/phase17_dashboard_route_map_certification_latest.json",
      "runtime/certifications/phase30b_yfinance_provider_selection_snapshot_latest.json",
      "runtime/certifications/phase10d_runtime_static_dependency_diff_certification_latest.json",
      "runtime/certifications/phase12g_service_chain_dashboard_certification_latest.json",
      "runtime/certifications/phase22_live_graph_tab_certification_latest.json",
      "runtime/certifications/phase28a_candidate_sandbox_simulation_harness_stub_certification_latest.json",
      "runtime/certifications/phase25c_split_dashboard_panels_into_tab_workspaces_certification_latest.json",
      "runtime/certifications/phase19c_endpoint_activation_certification_latest.json",
      "runtime/certifications/phase3m_graph_certification_latest.json",
      "runtime/certifications/phase5c_repo_memory_certification_v2_latest.json",
      "runtime/certifications/phase25a_dashboard_tab_shell_layout_navigation_certification_latest.json",
      "runtime/certifications/phase27e_candidate_sandbox_result_stub_generator_certification_latest.json",
      "runtime/certifications/phase29g_historical_replay_provider_readiness_snapshot_latest.json",
      "runtime/certifications/phase27f_candidate_sandbox_readiness_lock_snapshot_latest.json",
      "runtime/certifications/phase24b_persist_observability_backend_health_certification_latest.json",
      "runtime/certifications/phase30a_yfinance_historical_bars_provider_probe_certification_latest.json",
      "runtime/certifications/phase18_real_positions_panel_certification_latest.json",
      "runtime/certifications/phase11f_frontend_type_lint_repair_certification_latest.json",
      "runtime/certifications/phase11c_frontend_polling_api_cleanup_certification_latest.json",
      "runtime/certifications/phase10h_architecture_dashboard_command_certification_latest.json",
      "runtime/certifications/phase6d_dependency_graph_certification_latest.json",
      "runtime/certifications/phase23a_frontend_request_normalizer_certification_latest.json",
      "runtime/certifications/phase29f_historical_replay_provider_adapter_stub_certification_latest.json",
      "runtime/certifications/phase27d_candidate_sandbox_result_schema_certification_latest.json",
      "runtime/certifications/phase10e_diff_classification_certification_latest.json",
      "runtime/certifications/phase30g_yfinance_historical_bars_adapter_wire_certification_latest.json",
      "runtime/certifications/phase10_domain_subsystem_visualization_certification_latest.json",
      "runtime/certifications/phase29d_historical_replay_readiness_snapshot_latest.json",
      "runtime/certifications/phase11g_live_market_dashboard_expansion_certification_latest.json",
      "runtime/certifications/phase9e_canonical_graph_certification_latest.json",
      "runtime/certifications/phase24d_observability_lock_handoff_snapshot_latest.json"
    ]
  },
  "snaptrade": {
    "file_count": 7,
    "sample_files": [
      "backend/app/snaptrade/executions/config.py",
      "backend/app/snaptrade/executions/execution_layer.py",
      "backend/app/stacks/snaptrade/__init__.py",
      "backend/app/stacks/snaptrade/execution.py",
      "backend/app/stacks/snaptrade/adapter.py",
      "backend/app/stacks/snaptrade/broker.py",
      "backend/app/stacks/snaptrade/base.py"
    ]
  },
  "strategy": {
    "file_count": 247,
    "sample_files": [
      "scripts/phase36a_strategy_rule_enablement_gate_contract_stub.py",
      "scripts/phase27a_strategy_proposal_capture_certification.py",
      "scripts/phase27b_strategy_candidate_review_index.py",
      "scripts/phase35e_strategy_sandbox_wiregraph_certification.py",
      "scripts/phase14e_strategy_service_chain_graph_export.py",
      "scripts/phase27b_strategy_candidate_review_index_certification.py",
      "scripts/phase14f_strategy_decision_service_chain_certification.py",
      "scripts/phase14g_strategy_chain_dashboard_certification.py",
      "scripts/phase14g_add_strategy_chain_to_dashboard.py",
      "scripts/phase27a_strategy_proposal_capture.py",
      "scripts/phase14_strategy_decision_service_chain.py",
      "frontend/services/strategyService.ts",
      "frontend/app/api/v1/strategy/decision/[symbol]/route.ts",
      "backend/app/stacks/strategy/strategy_registry.py",
      "backend/app/stacks/strategy/strategy_service.py",
      "backend/app/stacks/strategy/strategy_runtime.py",
      "backend/app/stacks/strategy/__init__.py",
      "backend/app/stacks/strategy/selector.py",
      "backend/app/stacks/strategy/signal.py",
      "backend/app/stacks/strategy/engine.py",
      "backend/app/stacks/strategy/evolution_engine.py",
      "backend/app/stacks/strategy/llm_strategy_engine.py",
      "backend/app/stacks/strategy/candidate_registry.py",
      "backend/app/stacks/strategy/base.py",
      "backend/app/stacks/strategy_candidate_sandbox/replay_metrics_generator.py",
      "backend/app/stacks/strategy_candidate_sandbox/hold_signal_generator_stub.py",
      "backend/app/stacks/strategy_candidate_sandbox/qwen_context_response_contract.py",
      "backend/app/stacks/strategy_candidate_sandbox/replay_metrics_contract.py",
      "backend/app/stacks/strategy_candidate_sandbox/strategy_rule_enablement_gate_contract.py",
      "backend/app/stacks/strategy_candidate_sandbox/safe_read_only_architecture_inspector.py",
      "backend/app/stacks/strategy_candidate_sandbox/trade_event_validator.py",
      "backend/app/stacks/strategy_candidate_sandbox/entry_exit_signal_contract.py",
      "backend/app/stacks/strategy_candidate_sandbox/hold_decision_to_hold_event_bridge.py",
      "backend/app/stacks/strategy_candidate_sandbox/entry_signal_rule_contract.py",
      "backend/app/stacks/strategy_candidate_sandbox/exit_signal_rule_contract.py",
      "backend/app/stacks/strategy_candidate_sandbox/qwen_read_only_architecture_summary_gate.py",
      "backend/app/stacks/strategy_candidate_sandbox/trade_simulation_enablement_gate_contract.py",
      "backend/app/stacks/strategy_candidate_sandbox/exit_signal_rule_validator.py",
      "backend/app/stacks/strategy_candidate_sandbox/qwen_read_only_architecture_context.py",
      "backend/app/stacks/strategy_candidate_sandbox/risk_gate_validator.py"
    ]
  },
  "unknown": {
    "file_count": 269,
    "sample_files": [
      "OUTPUT",
      "ARCHITECTURE_REPAIR_PLAN.json",
      "TOPOLOGY_NORMALIZED_STATE.json",
      "ARCH_GOVERNANCE.md",
      "fix_phase9_self_fingerprint.sh",
      "TOPOLOGY_STATE.json",
      "topology_wire_graph.png",
      "neurovest_repo_context.md",
      "Directory Structure",
      "ORPHAN_RESOLUTION_PLAN.json",
      "topology_wire_graph_canonical.png",
      ".env.example",
      "domain_subsystem_graph.png",
      "generate_wire_graph.py",
      "neuro_health.sh",
      "neuro_cli_file_inspection.json",
      ".aider.input.history",
      "FINAL_ARCHITECTURE_STATE.json",
      "system_tree.txt",
      "docker-compose.yml",
      "ARCH_ENFORCEMENT_REPORT.json",
      "spine_mvp_full.sh",
      "pytest.ini",
      ".gitignore",
      "$OUTPUT",
      "SERVICE_RELOCATION_PLAN_RECONCILED.json",
      ".env",
      "domain_runtime_overlay_graph.png",
      "cursor.AppImage",
      "neuro",
      "neuro_cli.py",
      "neuro_engineer.py",
      "SERVICE_RELOCATION_PLAN.json",
      "architecture_backup/dashboard_service.py",
      "scripts/phase59b_qwen_read_only_final_handoff_certification_rollup_certification.py",
      "scripts/phase22_live_graph_tab_certification.py",
      "scripts/phase48c_handoff_bundle_refresh.py",
      "scripts/phase51a_qwen_read_only_architecture_loop_boundary_stub.py",
      "scripts/phase30g_yfinance_historical_bars_adapter_wire.py",
      "scripts/phase10d_runtime_static_dependency_diff_certification.py"
    ]
  },
  "wolfden": {
    "file_count": 7,
    "sample_files": [
      "backend/app/stacks/wolfden_ai/memory.py",
      "backend/app/stacks/wolfden_ai/__init__.py",
      "backend/app/stacks/wolfden_ai/agent_router.py",
      "backend/app/stacks/wolfden_ai/orchestrator.py",
      "backend/app/stacks/wolfden_ai/routing.py",
      "backend/app/stacks/wolfden_ai/runtime.py",
      "backend/app/stacks/wolfden_ai/base.py"
    ]
  }
}
```

---

# 14. [Stack Architecture] Stack Ownership

Source: `handoff/project_bible/architecture_atlas/STACK_OWNERSHIP.md`

## auth

Files detected: 4

Owns:
- stack-specific files detected by topology scan

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `backend/app/stacks/auth_identity/__init__.py`
- `backend/app/stacks/auth_identity/base.py`
- `backend/app/stacks/auth_identity/validator.py`
- `backend/app/stacks/auth_identity/gate.py`

## backend_uncategorized

Files detected: 27

Owns:
- stack-specific files detected by topology scan

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `backend/__init__.py`
- `backend/requirements.txt`
- `backend/app/main.py`
- `backend/app/__init__.py`
- `backend/scripts/backup_db.sh`
- `backend/app/schemas/__init__.py`
- `backend/app/schemas/dashboard.py`
- `backend/app/test/test_neuro_repo_companion.py`
- `backend/app/test/test_trading_pipeline.py`
- `backend/app/api/graph_ws.py`
- `backend/app/services/__init__.py`
- `backend/app/analysis/architecture.py`

## chat

Files detected: 43

Owns:
- chat runtime, memory, prompts, Qwen/Ollama-facing chat layer

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `.aider.chat.history.md`
- `scripts/phase20f_floating_chat_widget_certification.py`
- `scripts/phase26f_chat_ui_state_cleanup_metadata_rendering_certification.py`
- `scripts/phase26d_frontend_chat_response_normalizer_certification.py`
- `scripts/phase26f_chat_ui_state_cleanup_metadata_rendering.py`
- `scripts/phase21cd_chat_ux_persistent_cache.py`
- `scripts/phase21_fix_chat_service_generator.py`
- `scripts/phase26a_chat_intent_regex_ollama_router.py`
- `scripts/phase26e_chat_metadata_chips_typing_enter_certification.py`
- `scripts/phase20_floating_chat_widget_service_chain.py`
- `scripts/phase21cd_chat_ux_persistent_cache_certification.py`
- `scripts/phase26b_wire_ollama_into_chat_runtime.py`

## execution

Files detected: 19

Owns:
- paper broker, ledger, fills, commissions, sandbox runtime

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `scripts/phase28d_candidate_sandbox_execution_contract_certification.py`
- `scripts/phase28d_candidate_sandbox_execution_contract.py`
- `scripts/phase26c_chat_safety_prompt_live_execution_guard_certification.py`
- `backend/app/stacks/execution/__init__.py`
- `backend/app/stacks/execution/sandbox_runtime.py`
- `backend/app/stacks/execution/commission_engine.py`
- `backend/app/stacks/execution/sandbox.py`
- `backend/app/stacks/execution/regime_modes.py`
- `backend/app/stacks/execution/pnl_engine.py`
- `backend/app/stacks/execution/executor.py`
- `backend/app/stacks/execution/trade_ledger.py`
- `backend/app/stacks/execution/regime_simulator.py`

## frontend

Files detected: 28

Owns:
- stack-specific files detected by topology scan

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `frontend/next-env.d.ts`
- `frontend/package-lock.json`
- `frontend/CLAUDE.md`
- `frontend/next.config.ts`
- `frontend/eslint.config.mjs`
- `frontend/tsconfig.json`
- `frontend/postcss.config.mjs`
- `frontend/README.md`
- `frontend/.gitignore`
- `frontend/package.json`
- `frontend/AGENTS.md`
- `frontend/app/globals.css`

## journal

Files detected: 4

Owns:
- stack-specific files detected by topology scan

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `backend/app/stacks/journal_ledger/ledger.py`
- `backend/app/stacks/journal_ledger/__init__.py`
- `backend/app/stacks/journal_ledger/record.py`
- `backend/app/stacks/journal_ledger/base.py`

## learning

Files detected: 9

Owns:
- replay research, Monte Carlo, probability, evaluator logic

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `backend/app/stacks/learning_research/strategy_evaluator.py`
- `backend/app/stacks/learning_research/__init__.py`
- `backend/app/stacks/learning_research/monte_carlo_mix.py`
- `backend/app/stacks/learning_research/monte_carlo.py`
- `backend/app/stacks/learning_research/research_loader.py`
- `backend/app/stacks/learning_research/probability_engine.py`
- `backend/app/stacks/learning_research/research_runtime.py`
- `backend/app/stacks/learning_research/base.py`
- `backend/app/stacks/learning_research/backtest_engine.py`

## market_data

Files detected: 15

Owns:
- provider routing, bars, price, sessions, market data service

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `scripts/phase29e_historical_replay_market_data_provider_contract_certification.py`
- `scripts/phase29e_historical_replay_market_data_provider_contract.py`
- `backend/app/stacks/market_data/yfinance_ingestor.py`
- `backend/app/stacks/market_data/provider_registry.py`
- `backend/app/stacks/market_data/__init__.py`
- `backend/app/stacks/market_data/feed.py`
- `backend/app/stacks/market_data/market_data_service.py`
- `backend/app/stacks/market_data/bars.py`
- `backend/app/stacks/market_data/market_session.py`
- `backend/app/stacks/market_data/provider_router.py`
- `backend/app/stacks/market_data/price.py`
- `backend/app/stacks/market_data/yfinance_historical_bars_adapter.py`

## notification

Files detected: 2

Owns:
- stack-specific files detected by topology scan

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `backend/app/stacks/notification/__init__.py`
- `backend/app/stacks/notification/base.py`

## portfolio

Files detected: 19

Owns:
- allocation, accounting, positions, dashboard data

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `scripts/phase13f_portfolio_positions_service_chain_certification.py`
- `scripts/phase13e_portfolio_service_chain_graph_export.py`
- `scripts/phase13_portfolio_positions_service_chain.py`
- `scripts/phase13g_portfolio_chain_dashboard_certification.py`
- `scripts/phase13g_add_portfolio_chain_to_dashboard.py`
- `frontend/services/portfolioService.ts`
- `frontend/app/api/v1/portfolio/positions/route.ts`
- `backend/app/stacks/portfolio/portfolio_service.py`
- `backend/app/stacks/portfolio/allocator.py`
- `backend/app/stacks/portfolio/__init__.py`
- `backend/app/stacks/portfolio/accounting.py`
- `backend/app/stacks/portfolio/portfolio_runtime.py`

## research

Files detected: 2

Owns:
- stack-specific files detected by topology scan

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `scripts/phase1_repo_research_market_bootstrap.py`
- `runtime/research_db/research_seed.json`

## risk

Files detected: 22

Owns:
- drawdown, exposure, loss streak, kill switch, risk service

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `scripts/phase15_risk_gate_service_chain.py`
- `scripts/phase15g_add_risk_chain_to_dashboard.py`
- `scripts/phase38b_risk_gate_validation_stub.py`
- `scripts/phase15e_risk_service_chain_graph_export.py`
- `scripts/phase38c_risk_gate_pipeline_rollup_certification.py`
- `scripts/phase15g_risk_chain_dashboard_certification.py`
- `scripts/phase15f_risk_gate_service_chain_certification.py`
- `scripts/phase38a_risk_gate_contract_stub.py`
- `frontend/services/riskService.ts`
- `frontend/app/api/v1/risk/gate/[symbol]/route.ts`
- `backend/app/stacks/risk/loss_streak_guard.py`
- `backend/app/stacks/risk/__init__.py`

## runtime_artifacts

Files detected: 103

Owns:
- stack-specific files detected by topology scan

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `runtime/market_warehouse/symbol_registry.json`
- `runtime/handoff_snapshot/live_graph_validate_latest.json`
- `runtime/handoff_snapshot/file_manifest_latest.txt`
- `runtime/handoff_snapshot/simulate_trade_guard_latest.json`
- `runtime/handoff_snapshot/topology_tree_latest.txt`
- `runtime/handoff_snapshot/neurovest_training_handoff_bundle_latest.json`
- `runtime/certifications/phase11_live_market_price_api_bridge_certification_latest.json`
- `runtime/certifications/phase22b_live_graph_visualization_certification_latest.json`
- `runtime/certifications/phase30f_yfinance_historical_bars_adapter_wire_preview_certification_latest.json`
- `runtime/certifications/phase17_dashboard_route_map_certification_latest.json`
- `runtime/certifications/phase30b_yfinance_provider_selection_snapshot_latest.json`
- `runtime/certifications/phase10d_runtime_static_dependency_diff_certification_latest.json`

## snaptrade

Files detected: 7

Owns:
- stack-specific files detected by topology scan

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `backend/app/snaptrade/executions/config.py`
- `backend/app/snaptrade/executions/execution_layer.py`
- `backend/app/stacks/snaptrade/__init__.py`
- `backend/app/stacks/snaptrade/execution.py`
- `backend/app/stacks/snaptrade/adapter.py`
- `backend/app/stacks/snaptrade/broker.py`
- `backend/app/stacks/snaptrade/base.py`

## strategy

Files detected: 247

Owns:
- strategy contracts, decisions, indicators, signal rules

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `scripts/phase36a_strategy_rule_enablement_gate_contract_stub.py`
- `scripts/phase27a_strategy_proposal_capture_certification.py`
- `scripts/phase27b_strategy_candidate_review_index.py`
- `scripts/phase35e_strategy_sandbox_wiregraph_certification.py`
- `scripts/phase14e_strategy_service_chain_graph_export.py`
- `scripts/phase27b_strategy_candidate_review_index_certification.py`
- `scripts/phase14f_strategy_decision_service_chain_certification.py`
- `scripts/phase14g_strategy_chain_dashboard_certification.py`
- `scripts/phase14g_add_strategy_chain_to_dashboard.py`
- `scripts/phase27a_strategy_proposal_capture.py`
- `scripts/phase14_strategy_decision_service_chain.py`
- `frontend/services/strategyService.ts`

## unknown

Files detected: 269

Owns:
- stack-specific files detected by topology scan

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `OUTPUT`
- `ARCHITECTURE_REPAIR_PLAN.json`
- `TOPOLOGY_NORMALIZED_STATE.json`
- `ARCH_GOVERNANCE.md`
- `fix_phase9_self_fingerprint.sh`
- `TOPOLOGY_STATE.json`
- `topology_wire_graph.png`
- `neurovest_repo_context.md`
- `Directory Structure`
- `ORPHAN_RESOLUTION_PLAN.json`
- `topology_wire_graph_canonical.png`
- `.env.example`

## wolfden

Files detected: 7

Owns:
- stack-specific files detected by topology scan

Must not own:
- unrelated stack mutation
- broker/live execution unless explicitly certified
- cross-layer shortcuts

Sample files:
- `backend/app/stacks/wolfden_ai/memory.py`
- `backend/app/stacks/wolfden_ai/__init__.py`
- `backend/app/stacks/wolfden_ai/agent_router.py`
- `backend/app/stacks/wolfden_ai/orchestrator.py`
- `backend/app/stacks/wolfden_ai/routing.py`
- `backend/app/stacks/wolfden_ai/runtime.py`
- `backend/app/stacks/wolfden_ai/base.py`

---

# 15. [Stack Architecture] Stack Graph

Source: `handoff/project_bible/architecture_atlas/TOPOLOGY/stack_graph.json`

```json
{
  "auth": {
    "file_count": 4,
    "sample_files": [
      "backend/app/stacks/auth_identity/__init__.py",
      "backend/app/stacks/auth_identity/base.py",
      "backend/app/stacks/auth_identity/validator.py",
      "backend/app/stacks/auth_identity/gate.py"
    ]
  },
  "backend_uncategorized": {
    "file_count": 27,
    "sample_files": [
      "backend/__init__.py",
      "backend/requirements.txt",
      "backend/app/main.py",
      "backend/app/__init__.py",
      "backend/scripts/backup_db.sh",
      "backend/app/schemas/__init__.py",
      "backend/app/schemas/dashboard.py",
      "backend/app/test/test_neuro_repo_companion.py",
      "backend/app/test/test_trading_pipeline.py",
      "backend/app/api/graph_ws.py",
      "backend/app/services/__init__.py",
      "backend/app/analysis/architecture.py",
      "backend/app/core/cognitive_nodes.py",
      "backend/app/core/__init__.py",
      "backend/app/core/cognitive_types.py",
      "backend/app/core/config.py",
      "backend/app/core/cognitive_graph_state.py",
      "backend/app/core/cognitive_event_bus.py",
      "backend/app/core/runtime_firewall_v1.py",
      "backend/app/core/global_firewall_v1.py",
      "backend/app/stacks/__init__.py",
      "backend/app/stacks/registry.json",
      "backend/app/routers/__init__.py",
      "backend/app/stacks/db_model/__init__.py",
      "backend/app/stacks/db_model/market_schema.py",
      "backend/app/stacks/db_model/base.py",
      "backend/app/stacks/events/broker.py"
    ]
  },
  "chat": {
    "file_count": 43,
    "sample_files": [
      ".aider.chat.history.md",
      "scripts/phase20f_floating_chat_widget_certification.py",
      "scripts/phase26f_chat_ui_state_cleanup_metadata_rendering_certification.py",
      "scripts/phase26d_frontend_chat_response_normalizer_certification.py",
      "scripts/phase26f_chat_ui_state_cleanup_metadata_rendering.py",
      "scripts/phase21cd_chat_ux_persistent_cache.py",
      "scripts/phase21_fix_chat_service_generator.py",
      "scripts/phase26a_chat_intent_regex_ollama_router.py",
      "scripts/phase26e_chat_metadata_chips_typing_enter_certification.py",
      "scripts/phase20_floating_chat_widget_service_chain.py",
      "scripts/phase21cd_chat_ux_persistent_cache_certification.py",
      "scripts/phase26b_wire_ollama_into_chat_runtime.py",
      "scripts/phase25b_tab_layout_polish_chat_panel.py",
      "scripts/phase26d_frontend_chat_response_normalizer.py",
      "scripts/phase21ab_chat_cache_history_certification.py",
      "scripts/phase61a_archive_or_new_chat_handoff_summary.py",
      "scripts/phase26e_chat_metadata_chips_typing_enter.py",
      "scripts/phase21ab_chat_cache_history.py",
      "scripts/phase20e_chat_service_chain_graph_export.py",
      "scripts/phase25b_tab_layout_polish_chat_panel_certification.py",
      "frontend/services/chatService.ts",
      "frontend/app/api/v1/chat/route.ts",
      "backend/app/stacks/chat_public/chat_intent_regex.py",
      "backend/app/stacks/chat_public/context_loader.py",
      "backend/app/stacks/chat_public/__init__.py",
      "backend/app/stacks/chat_public/chat_runtime.py",
      "backend/app/stacks/chat_public/chat_system_prompt.py",
      "backend/app/stacks/chat_public/conversation_store.py",
      "backend/app/stacks/chat_public/chat_memory.py",
      "backend/app/stacks/chat_public/ollama_chat_client.py",
      "backend/app/stacks/chat_public/chat_service.py",
      "backend/app/stacks/chat_public/time_context.py",
      "backend/app/stacks/chat_public/strategy_proposal_capture.py",
      "backend/app/stacks/chat_public/base.py",
      "backend/app/stacks/chat_public/chat_api.py",
      "runtime/certifications/phase25b_tab_layout_polish_chat_panel_certification_latest.json",
      "runtime/certifications/phase26e_chat_metadata_chips_typing_enter_certification_latest.json",
      "runtime/certifications/phase21ab_chat_cache_history_certification_latest.json",
      "runtime/certifications/phase20f_floating_chat_widget_certification_latest.json",
      "runtime/certifications/phase26d_frontend_chat_response_normalizer_certification_latest.json"
    ]
  },
  "execution": {
    "file_count": 19,
    "sample_files": [
      "scripts/phase28d_candidate_sandbox_execution_contract_certification.py",
      "scripts/phase28d_candidate_sandbox_execution_contract.py",
      "scripts/phase26c_chat_safety_prompt_live_execution_guard_certification.py",
      "backend/app/stacks/execution/__init__.py",
      "backend/app/stacks/execution/sandbox_runtime.py",
      "backend/app/stacks/execution/commission_engine.py",
      "backend/app/stacks/execution/sandbox.py",
      "backend/app/stacks/execution/regime_modes.py",
      "backend/app/stacks/execution/pnl_engine.py",
      "backend/app/stacks/execution/executor.py",
      "backend/app/stacks/execution/trade_ledger.py",
      "backend/app/stacks/execution/regime_simulator.py",
      "backend/app/stacks/execution/paper_broker.py",
      "backend/app/stacks/execution/broker.py",
      "backend/app/stacks/execution/fill_engine.py",
      "backend/app/stacks/execution/base.py",
      "backend/app/stacks/execution/accounting_engine.py",
      "runtime/certifications/phase26c_chat_safety_prompt_live_execution_guard_certification_latest.json",
      "runtime/certifications/phase28d_candidate_sandbox_execution_contract_certification_latest.json"
    ]
  },
  "frontend": {
    "file_count": 28,
    "sample_files": [
      "frontend/next-env.d.ts",
      "frontend/package-lock.json",
      "frontend/CLAUDE.md",
      "frontend/next.config.ts",
      "frontend/eslint.config.mjs",
      "frontend/tsconfig.json",
      "frontend/postcss.config.mjs",
      "frontend/README.md",
      "frontend/.gitignore",
      "frontend/package.json",
      "frontend/AGENTS.md",
      "frontend/app/globals.css",
      "frontend/app/layout.tsx",
      "frontend/app/page.tsx",
      "frontend/app/favicon.ico",
      "frontend/services/observabilityTimelineService.ts",
      "frontend/services/graphService.ts",
      "frontend/services/marketService.ts",
      "frontend/services/requestNormalizer.ts",
      "frontend/services/requestObservability.ts",
      "frontend/services/backendHealthService.ts",
      "frontend/public/window.svg",
      "frontend/public/file.svg",
      "frontend/public/vercel.svg",
      "frontend/public/globe.svg",
      "frontend/public/next.svg",
      "frontend/app/api/v1/graph/live/route.ts",
      "frontend/app/api/v1/market/live-price/[symbol]/route.ts"
    ]
  },
  "journal": {
    "file_count": 4,
    "sample_files": [
      "backend/app/stacks/journal_ledger/ledger.py",
      "backend/app/stacks/journal_ledger/__init__.py",
      "backend/app/stacks/journal_ledger/record.py",
      "backend/app/stacks/journal_ledger/base.py"
    ]
  },
  "learning": {
    "file_count": 9,
    "sample_files": [
      "backend/app/stacks/learning_research/strategy_evaluator.py",
      "backend/app/stacks/learning_research/__init__.py",
      "backend/app/stacks/learning_research/monte_carlo_mix.py",
      "backend/app/stacks/learning_research/monte_carlo.py",
      "backend/app/stacks/learning_research/research_loader.py",
      "backend/app/stacks/learning_research/probability_engine.py",
      "backend/app/stacks/learning_research/research_runtime.py",
      "backend/app/stacks/learning_research/base.py",
      "backend/app/stacks/learning_research/backtest_engine.py"
    ]
  },
  "market_data": {
    "file_count": 15,
    "sample_files": [
      "scripts/phase29e_historical_replay_market_data_provider_contract_certification.py",
      "scripts/phase29e_historical_replay_market_data_provider_contract.py",
      "backend/app/stacks/market_data/yfinance_ingestor.py",
      "backend/app/stacks/market_data/provider_registry.py",
      "backend/app/stacks/market_data/__init__.py",
      "backend/app/stacks/market_data/feed.py",
      "backend/app/stacks/market_data/market_data_service.py",
      "backend/app/stacks/market_data/bars.py",
      "backend/app/stacks/market_data/market_session.py",
      "backend/app/stacks/market_data/provider_router.py",
      "backend/app/stacks/market_data/price.py",
      "backend/app/stacks/market_data/yfinance_historical_bars_adapter.py",
      "backend/app/stacks/market_data/provider_cache.py",
      "backend/app/stacks/market_data/base.py",
      "runtime/certifications/phase29e_historical_replay_market_data_provider_contract_certification_latest.json"
    ]
  },
  "notification": {
    "file_count": 2,
    "sample_files": [
      "backend/app/stacks/notification/__init__.py",
      "backend/app/stacks/notification/base.py"
    ]
  },
  "portfolio": {
    "file_count": 19,
    "sample_files": [
      "scripts/phase13f_portfolio_positions_service_chain_certification.py",
      "scripts/phase13e_portfolio_service_chain_graph_export.py",
      "scripts/phase13_portfolio_positions_service_chain.py",
      "scripts/phase13g_portfolio_chain_dashboard_certification.py",
      "scripts/phase13g_add_portfolio_chain_to_dashboard.py",
      "frontend/services/portfolioService.ts",
      "frontend/app/api/v1/portfolio/positions/route.ts",
      "backend/app/stacks/portfolio/portfolio_service.py",
      "backend/app/stacks/portfolio/allocator.py",
      "backend/app/stacks/portfolio/__init__.py",
      "backend/app/stacks/portfolio/accounting.py",
      "backend/app/stacks/portfolio/portfolio_runtime.py",
      "backend/app/stacks/portfolio/reconciliation.py",
      "backend/app/stacks/portfolio/dashboard_service.py",
      "backend/app/stacks/portfolio/rebalance.py",
      "backend/app/stacks/portfolio/base.py",
      "runtime/certifications/phase13f_portfolio_positions_service_chain_certification_latest.json",
      "runtime/certifications/phase13g_portfolio_chain_dashboard_certification_latest.json",
      "runtime/repo_memory/portfolio_service_chain_graph_v1.json"
    ]
  },
  "research": {
    "file_count": 2,
    "sample_files": [
      "scripts/phase1_repo_research_market_bootstrap.py",
      "runtime/research_db/research_seed.json"
    ]
  },
  "risk": {
    "file_count": 22,
    "sample_files": [
      "scripts/phase15_risk_gate_service_chain.py",
      "scripts/phase15g_add_risk_chain_to_dashboard.py",
      "scripts/phase38b_risk_gate_validation_stub.py",
      "scripts/phase15e_risk_service_chain_graph_export.py",
      "scripts/phase38c_risk_gate_pipeline_rollup_certification.py",
      "scripts/phase15g_risk_chain_dashboard_certification.py",
      "scripts/phase15f_risk_gate_service_chain_certification.py",
      "scripts/phase38a_risk_gate_contract_stub.py",
      "frontend/services/riskService.ts",
      "frontend/app/api/v1/risk/gate/[symbol]/route.ts",
      "backend/app/stacks/risk/loss_streak_guard.py",
      "backend/app/stacks/risk/__init__.py",
      "backend/app/stacks/risk/drawdown_guard.py",
      "backend/app/stacks/risk/risk_runtime_service.py",
      "backend/app/stacks/risk/exposure.py",
      "backend/app/stacks/risk/kill_switch.py",
      "backend/app/stacks/risk/limits.py",
      "backend/app/stacks/risk/base.py",
      "backend/app/stacks/risk/risk_service.py",
      "runtime/certifications/phase15g_risk_chain_dashboard_certification_latest.json",
      "runtime/certifications/phase15f_risk_gate_service_chain_certification_latest.json",
      "runtime/repo_memory/risk_service_chain_graph_v1.json"
    ]
  },
  "runtime_artifacts": {
    "file_count": 103,
    "sample_files": [
      "runtime/market_warehouse/symbol_registry.json",
      "runtime/handoff_snapshot/live_graph_validate_latest.json",
      "runtime/handoff_snapshot/file_manifest_latest.txt",
      "runtime/handoff_snapshot/simulate_trade_guard_latest.json",
      "runtime/handoff_snapshot/topology_tree_latest.txt",
      "runtime/handoff_snapshot/neurovest_training_handoff_bundle_latest.json",
      "runtime/certifications/phase11_live_market_price_api_bridge_certification_latest.json",
      "runtime/certifications/phase22b_live_graph_visualization_certification_latest.json",
      "runtime/certifications/phase30f_yfinance_historical_bars_adapter_wire_preview_certification_latest.json",
      "runtime/certifications/phase17_dashboard_route_map_certification_latest.json",
      "runtime/certifications/phase30b_yfinance_provider_selection_snapshot_latest.json",
      "runtime/certifications/phase10d_runtime_static_dependency_diff_certification_latest.json",
      "runtime/certifications/phase12g_service_chain_dashboard_certification_latest.json",
      "runtime/certifications/phase22_live_graph_tab_certification_latest.json",
      "runtime/certifications/phase28a_candidate_sandbox_simulation_harness_stub_certification_latest.json",
      "runtime/certifications/phase25c_split_dashboard_panels_into_tab_workspaces_certification_latest.json",
      "runtime/certifications/phase19c_endpoint_activation_certification_latest.json",
      "runtime/certifications/phase3m_graph_certification_latest.json",
      "runtime/certifications/phase5c_repo_memory_certification_v2_latest.json",
      "runtime/certifications/phase25a_dashboard_tab_shell_layout_navigation_certification_latest.json",
      "runtime/certifications/phase27e_candidate_sandbox_result_stub_generator_certification_latest.json",
      "runtime/certifications/phase29g_historical_replay_provider_readiness_snapshot_latest.json",
      "runtime/certifications/phase27f_candidate_sandbox_readiness_lock_snapshot_latest.json",
      "runtime/certifications/phase24b_persist_observability_backend_health_certification_latest.json",
      "runtime/certifications/phase30a_yfinance_historical_bars_provider_probe_certification_latest.json",
      "runtime/certifications/phase18_real_positions_panel_certification_latest.json",
      "runtime/certifications/phase11f_frontend_type_lint_repair_certification_latest.json",
      "runtime/certifications/phase11c_frontend_polling_api_cleanup_certification_latest.json",
      "runtime/certifications/phase10h_architecture_dashboard_command_certification_latest.json",
      "runtime/certifications/phase6d_dependency_graph_certification_latest.json",
      "runtime/certifications/phase23a_frontend_request_normalizer_certification_latest.json",
      "runtime/certifications/phase29f_historical_replay_provider_adapter_stub_certification_latest.json",
      "runtime/certifications/phase27d_candidate_sandbox_result_schema_certification_latest.json",
      "runtime/certifications/phase10e_diff_classification_certification_latest.json",
      "runtime/certifications/phase30g_yfinance_historical_bars_adapter_wire_certification_latest.json",
      "runtime/certifications/phase10_domain_subsystem_visualization_certification_latest.json",
      "runtime/certifications/phase29d_historical_replay_readiness_snapshot_latest.json",
      "runtime/certifications/phase11g_live_market_dashboard_expansion_certification_latest.json",
      "runtime/certifications/phase9e_canonical_graph_certification_latest.json",
      "runtime/certifications/phase24d_observability_lock_handoff_snapshot_latest.json"
    ]
  },
  "snaptrade": {
    "file_count": 7,
    "sample_files": [
      "backend/app/snaptrade/executions/config.py",
      "backend/app/snaptrade/executions/execution_layer.py",
      "backend/app/stacks/snaptrade/__init__.py",
      "backend/app/stacks/snaptrade/execution.py",
      "backend/app/stacks/snaptrade/adapter.py",
      "backend/app/stacks/snaptrade/broker.py",
      "backend/app/stacks/snaptrade/base.py"
    ]
  },
  "strategy": {
    "file_count": 247,
    "sample_files": [
      "scripts/phase36a_strategy_rule_enablement_gate_contract_stub.py",
      "scripts/phase27a_strategy_proposal_capture_certification.py",
      "scripts/phase27b_strategy_candidate_review_index.py",
      "scripts/phase35e_strategy_sandbox_wiregraph_certification.py",
      "scripts/phase14e_strategy_service_chain_graph_export.py",
      "scripts/phase27b_strategy_candidate_review_index_certification.py",
      "scripts/phase14f_strategy_decision_service_chain_certification.py",
      "scripts/phase14g_strategy_chain_dashboard_certification.py",
      "scripts/phase14g_add_strategy_chain_to_dashboard.py",
      "scripts/phase27a_strategy_proposal_capture.py",
      "scripts/phase14_strategy_decision_service_chain.py",
      "frontend/services/strategyService.ts",
      "frontend/app/api/v1/strategy/decision/[symbol]/route.ts",
      "backend/app/stacks/strategy/strategy_registry.py",
      "backend/app/stacks/strategy/strategy_service.py",
      "backend/app/stacks/strategy/strategy_runtime.py",
      "backend/app/stacks/strategy/__init__.py",
      "backend/app/stacks/strategy/selector.py",
      "backend/app/stacks/strategy/signal.py",
      "backend/app/stacks/strategy/engine.py",
      "backend/app/stacks/strategy/evolution_engine.py",
      "backend/app/stacks/strategy/llm_strategy_engine.py",
      "backend/app/stacks/strategy/candidate_registry.py",
      "backend/app/stacks/strategy/base.py",
      "backend/app/stacks/strategy_candidate_sandbox/replay_metrics_generator.py",
      "backend/app/stacks/strategy_candidate_sandbox/hold_signal_generator_stub.py",
      "backend/app/stacks/strategy_candidate_sandbox/qwen_context_response_contract.py",
      "backend/app/stacks/strategy_candidate_sandbox/replay_metrics_contract.py",
      "backend/app/stacks/strategy_candidate_sandbox/strategy_rule_enablement_gate_contract.py",
      "backend/app/stacks/strategy_candidate_sandbox/safe_read_only_architecture_inspector.py",
      "backend/app/stacks/strategy_candidate_sandbox/trade_event_validator.py",
      "backend/app/stacks/strategy_candidate_sandbox/entry_exit_signal_contract.py",
      "backend/app/stacks/strategy_candidate_sandbox/hold_decision_to_hold_event_bridge.py",
      "backend/app/stacks/strategy_candidate_sandbox/entry_signal_rule_contract.py",
      "backend/app/stacks/strategy_candidate_sandbox/exit_signal_rule_contract.py",
      "backend/app/stacks/strategy_candidate_sandbox/qwen_read_only_architecture_summary_gate.py",
      "backend/app/stacks/strategy_candidate_sandbox/trade_simulation_enablement_gate_contract.py",
      "backend/app/stacks/strategy_candidate_sandbox/exit_signal_rule_validator.py",
      "backend/app/stacks/strategy_candidate_sandbox/qwen_read_only_architecture_context.py",
      "backend/app/stacks/strategy_candidate_sandbox/risk_gate_validator.py"
    ]
  },
  "unknown": {
    "file_count": 269,
    "sample_files": [
      "OUTPUT",
      "ARCHITECTURE_REPAIR_PLAN.json",
      "TOPOLOGY_NORMALIZED_STATE.json",
      "ARCH_GOVERNANCE.md",
      "fix_phase9_self_fingerprint.sh",
      "TOPOLOGY_STATE.json",
      "topology_wire_graph.png",
      "neurovest_repo_context.md",
      "Directory Structure",
      "ORPHAN_RESOLUTION_PLAN.json",
      "topology_wire_graph_canonical.png",
      ".env.example",
      "domain_subsystem_graph.png",
      "generate_wire_graph.py",
      "neuro_health.sh",
      "neuro_cli_file_inspection.json",
      ".aider.input.history",
      "FINAL_ARCHITECTURE_STATE.json",
      "system_tree.txt",
      "docker-compose.yml",
      "ARCH_ENFORCEMENT_REPORT.json",
      "spine_mvp_full.sh",
      "pytest.ini",
      ".gitignore",
      "$OUTPUT",
      "SERVICE_RELOCATION_PLAN_RECONCILED.json",
      ".env",
      "domain_runtime_overlay_graph.png",
      "cursor.AppImage",
      "neuro",
      "neuro_cli.py",
      "neuro_engineer.py",
      "SERVICE_RELOCATION_PLAN.json",
      "architecture_backup/dashboard_service.py",
      "scripts/phase59b_qwen_read_only_final_handoff_certification_rollup_certification.py",
      "scripts/phase22_live_graph_tab_certification.py",
      "scripts/phase48c_handoff_bundle_refresh.py",
      "scripts/phase51a_qwen_read_only_architecture_loop_boundary_stub.py",
      "scripts/phase30g_yfinance_historical_bars_adapter_wire.py",
      "scripts/phase10d_runtime_static_dependency_diff_certification.py"
    ]
  },
  "wolfden": {
    "file_count": 7,
    "sample_files": [
      "backend/app/stacks/wolfden_ai/memory.py",
      "backend/app/stacks/wolfden_ai/__init__.py",
      "backend/app/stacks/wolfden_ai/agent_router.py",
      "backend/app/stacks/wolfden_ai/orchestrator.py",
      "backend/app/stacks/wolfden_ai/routing.py",
      "backend/app/stacks/wolfden_ai/runtime.py",
      "backend/app/stacks/wolfden_ai/base.py"
    ]
  }
}
```

---

# 16. [Node / Topology] Runtime Node Graph

Source: `handoff/runtime_node_graph.txt`

```text
NEUROVEST SYSTEM NODE MAP

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
```

---

# 17. [Node / Topology] Node Graph

Source: `handoff/project_bible/architecture_atlas/TOPOLOGY/node_graph.md`

# Node Graph

```text
NEUROVEST SYSTEM NODE MAP

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

```

---

# 18. [Node / Topology] Dependency Graph

Source: `handoff/project_bible/architecture_atlas/TOPOLOGY/dependency_graph.md`

# Dependency Graph

```text
HIGH-LEVEL DEPENDENCY GRAPH

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

```

---

# 19. [Node / Topology] Topology Summary

Source: `handoff/topology_summary.json`

```json
{
  "phase": "62A_MASTER_ARCHITECTURE_HANDOFF_CONTROLLER",
  "created_at": "2026-07-07T02:55:08.948274+00:00",
  "mode": "READ_ONLY",
  "root": "/home/tkanhai/Neurovest",
  "artifact_count": 153,
  "certified_count": 110,
  "uncertified_count": 43,
  "stacks": {
    "auth": 4,
    "backend_uncategorized": 27,
    "chat": 43,
    "execution": 19,
    "frontend": 28,
    "journal": 4,
    "learning": 9,
    "market_data": 15,
    "notification": 2,
    "portfolio": 19,
    "research": 2,
    "risk": 22,
    "runtime_artifacts": 103,
    "snaptrade": 7,
    "strategy": 247,
    "unknown": 269,
    "wolfden": 7
  },
  "layers": {
    "L0_external_adapter": 52,
    "L1_security_auth_safety": 68,
    "L2_domain": 243,
    "L3_service_facade": 36,
    "L4_runtime_orchestration": 112,
    "L5_api_presentation": 20,
    "L6_frontend": 104,
    "L7_tests": 4,
    "UNCLASSIFIED": 188
  },
  "terminal_archive_source": "/home/tkanhai/Neurovest/runtime/strategy_candidate_sandbox/61A_archive_or_new_chat_handoff_summary_latest.json",
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
    "topology_summary.json"
  ],
  "certified": true
}
```

---

# 20. [Node / Topology] Node Map

Source: `handoff/project_bible/NODE_MAP.md`

# Node Map

```text
NEUROVEST SYSTEM NODE MAP

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

```

---

# 21. [Dependency Atlas] Dependency Graph

Source: `handoff/dependency_graph.txt`

```text
HIGH-LEVEL DEPENDENCY GRAPH

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
```

---

# 22. [Dependency Atlas] Import Dependency Atlas

Source: `handoff/project_bible/architecture_atlas/IMPORT_DEPENDENCY_ATLAS.json`

```json
{
  "stack_edges": {
    "chat_public": [
      "chat_public"
    ],
    "execution": [
      "journal_ledger",
      "market_data",
      "portfolio",
      "risk",
      "strategy"
    ],
    "learning_research": [
      "db_model",
      "journal_ledger"
    ],
    "market_data": [
      "db_model",
      "journal_ledger",
      "market_data"
    ],
    "phase_scripts": [
      "market_data",
      "strategy_candidate_sandbox"
    ],
    "portfolio": [
      "execution",
      "journal_ledger",
      "market_data"
    ],
    "risk": [
      "journal_ledger",
      "risk"
    ],
    "root_or_misc": [
      "chat_public",
      "events",
      "execution",
      "journal_ledger",
      "market_data",
      "portfolio",
      "risk",
      "strategy",
      "wolfden_ai"
    ],
    "strategy": [
      "market_data",
      "portfolio",
      "strategy"
    ],
    "strategy_candidate_sandbox": [
      "strategy_candidate_sandbox"
    ],
    "wolfden_ai": [
      "execution",
      "journal_ledger",
      "risk",
      "strategy"
    ]
  },
  "file_imports": {
    "generate_wire_graph.py": [
      "json",
      "matplotlib.pyplot",
      "networkx",
      "urllib.request"
    ],
    "neuro_cli.py": [
      "json",
      "sys",
      "urllib.error",
      "urllib.request"
    ],
    "neuro_engineer.py": [
      "json",
      "os",
      "readline",
      "urllib.request"
    ],
    "architecture_backup/dashboard_service.py": [
      "decimal",
      "typing"
    ],
    "scripts/phase59b_qwen_read_only_final_handoff_certification_rollup_certification.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase22_live_graph_tab_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase20f_floating_chat_widget_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase48c_handoff_bundle_refresh.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase51a_qwen_read_only_architecture_loop_boundary_stub.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase30g_yfinance_historical_bars_adapter_wire.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase10d_runtime_static_dependency_diff_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase35a_exit_signal_rule_contract_stub.py": [
      "backend.app.stacks.strategy_candidate_sandbox.exit_signal_rule_contract",
      "datetime",
      "json",
      "pathlib",
      "py_compile"
    ],
    "scripts/phase23b_polling_governor_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "re",
      "subprocess",
      "sys"
    ],
    "scripts/phase23a_frontend_request_normalizer_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase29c_historical_replay_validation_stub.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase26f_chat_ui_state_cleanup_metadata_rendering_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase6c_dependency_graph_export.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase25a_dashboard_tab_shell_layout_navigation_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase27d_candidate_sandbox_result_schema_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase10h_architecture_dashboard_command_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase26d_frontend_chat_response_normalizer_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase13f_portfolio_positions_service_chain_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase31a_historical_bars_fetch_validation.py": [
      "backend.app.stacks.market_data.yfinance_historical_bars_adapter",
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase12g_service_chain_repair.py": [
      "pathlib"
    ],
    "scripts/phase52b_qwen_read_only_final_guardrail_summary_rollup_certification.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase27e_candidate_sandbox_result_stub_generator.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase40b_sandbox_runtime_dependency_trace_rollup_certification.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase36a_strategy_rule_enablement_gate_contract_stub.py": [
      "backend.app.stacks.strategy_candidate_sandbox.strategy_rule_enablement_gate_contract",
      "datetime",
      "json",
      "pathlib",
      "py_compile"
    ],
    "scripts/phase54a_qwen_read_only_handoff_export_summary_stub.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase26f_chat_ui_state_cleanup_metadata_rendering.py": [
      "pathlib"
    ],
    "scripts/phase63a_project_bible_generator.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase4g_repo_memory_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase25a_dashboard_tab_shell_layout_navigation.py": [
      "pathlib"
    ],
    "scripts/phase21cd_chat_ux_persistent_cache.py": [
      "pathlib"
    ],
    "scripts/phase11c_frontend_polling_api_cleanup.py": [
      "pathlib"
    ],
    "scripts/phase47b_qwen_read_only_recommendation_filter_rollup_certification.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase30a_yfinance_historical_bars_provider_probe_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase11g_live_market_dashboard_expansion.py": [
      "pathlib"
    ],
    "scripts/phase28b_candidate_sandbox_mock_metrics_generator.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase32a_real_metrics_generation.py": [
      "backend.app.stacks.market_data.yfinance_historical_bars_adapter",
      "backend.app.stacks.strategy_candidate_sandbox.replay_metrics_generator",
      "datetime",
      "json",
      "math",
      "pathlib",
      "py_compile"
    ],
    "scripts/phase41a_safe_read_only_architecture_inspector_stub.py": [
      "backend.app.stacks.strategy_candidate_sandbox.safe_read_only_architecture_inspector",
      "datetime",
      "json",
      "pathlib",
      "py_compile"
    ],
    "scripts/phase21_fix_chat_service_generator.py": [
      "pathlib"
    ],
    "scripts/phase12_service_layer_alignment.py": [
      "pathlib"
    ],
    "scripts/phase12g_service_chain_dashboard_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase9e_canonical_graph_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase40a_sandbox_runtime_dependency_trace_stub.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase4d_root_shadow_diff_report.py": [
      "ast",
      "datetime",
      "difflib",
      "hashlib",
      "json",
      "pathlib"
    ],
    "scripts/phase2_yfinance_market_warehouse.py": [
      "datetime",
      "json",
      "pathlib",
      "sys",
      "yfinance"
    ],
    "scripts/phase27a_strategy_proposal_capture_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase25c_split_dashboard_panels_into_tab_workspaces.py": [
      "pathlib"
    ],
    "scripts/phase29b_historical_replay_input_contract_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase48a_qwen_read_only_response_validator_stub.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase31f_replay_metrics_contract.py": [
      "backend.app.stacks.strategy_candidate_sandbox.replay_metrics_contract",
      "datetime",
      "json",
      "pathlib",
      "py_compile"
    ],
    "scripts/phase57a_qwen_read_only_policy_boundary_matrix_stub.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase9a_canonical_layer_graph_export.py": [
      "collections",
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase32b_candidate_scorecard_from_replay_metrics.py": [
      "backend.app.stacks.market_data.yfinance_historical_bars_adapter",
      "backend.app.stacks.strategy_candidate_sandbox.candidate_scorecard_from_replay_metrics",
      "backend.app.stacks.strategy_candidate_sandbox.replay_metrics_generator",
      "datetime",
      "json",
      "pathlib",
      "py_compile"
    ],
    "scripts/phase26a_chat_intent_regex_ollama_router.py": [
      "pathlib"
    ],
    "scripts/phase30a_yfinance_historical_bars_provider_probe.py": [
      "datetime",
      "importlib",
      "json",
      "pathlib"
    ],
    "scripts/phase33h_trade_simulation_pipeline_rollup_certification.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/architecture_enforcement_v1.py": [
      "__future__",
      "ast",
      "collections",
      "json",
      "os",
      "pathlib"
    ],
    "scripts/phase60b_qwen_read_only_terminal_freeze_rollup_certification.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase10c_runtime_flow_overlay_export.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase57c_handoff_bundle_refresh.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase35f_handoff_bundle_refresh.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/orphan_resolution_engine_v1.py": [
      "json",
      "pathlib"
    ],
    "scripts/phase12f_service_chain_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase11d_next_api_proxy_live_price.py": [
      "pathlib"
    ],
    "scripts/phase39b_master_sandbox_gate_wiregraph_rollup_certification.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase36b_enablement_gate_validation_stub.py": [
      "backend.app.stacks.strategy_candidate_sandbox.strategy_rule_enablement_gate_contract",
      "backend.app.stacks.strategy_candidate_sandbox.strategy_rule_enablement_gate_validator",
      "datetime",
      "json",
      "pathlib",
      "py_compile"
    ],
    "scripts/phase26e_chat_metadata_chips_typing_enter_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase43b_qwen_context_response_contract_rollup_certification.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase30e_yfinance_historical_bars_adapter_shape_validation.py": [
      "backend.app.stacks.market_data.yfinance_historical_bars_adapter",
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase30b_yfinance_provider_selection_snapshot.py": [
      "datetime",
      "hashlib",
      "json",
      "pathlib",
      "subprocess"
    ],
    "scripts/phase18_real_positions_panel_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase53b_qwen_read_only_handoff_freeze_rollup_certification.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase33d_entry_exit_signal_contract_stub.py": [
      "backend.app.stacks.strategy_candidate_sandbox.entry_exit_signal_contract",
      "datetime",
      "json",
      "pathlib",
      "py_compile"
    ],
    "scripts/phase18_real_positions_panel_component.py": [
      "pathlib"
    ],
    "scripts/phase11_live_market_price_api_bridge_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase27b_strategy_candidate_review_index.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase35c_exit_signal_generator_disabled_stub.py": [
      "backend.app.stacks.market_data.yfinance_historical_bars_adapter",
      "backend.app.stacks.strategy_candidate_sandbox.exit_signal_generator_disabled_stub",
      "backend.app.stacks.strategy_candidate_sandbox.exit_signal_rule_contract",
      "datetime",
      "json",
      "pathlib",
      "py_compile"
    ],
    "scripts/phase11_live_market_price_api_bridge.py": [
      "pathlib"
    ],
    "scripts/phase54c_handoff_bundle_refresh.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase10e_classify_runtime_static_diff_edges.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase19_dashboard_visual_layout_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase10g_architecture_drift_dashboard_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase4e_quarantine_root_shadows.py": [
      "datetime",
      "json",
      "pathlib",
      "shutil"
    ],
    "scripts/phase55b_qwen_read_only_architecture_state_machine_rollup_certification.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase35d_exit_signal_pipeline_rollup_certification.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase45a_qwen_read_only_architecture_summary_gate_stub.py": [
      "backend.app.stacks.strategy_candidate_sandbox.qwen_read_only_architecture_summary_gate",
      "datetime",
      "json",
      "pathlib",
      "py_compile"
    ],
    "scripts/phase63b_architecture_atlas_generator.py": [
      "ast",
      "collections",
      "datetime",
      "json",
      "pathlib",
      "re"
    ],
    "scripts/phase19b_endpoint_activation_probe_repair.py": [
      "pathlib"
    ],
    "scripts/phase6d_dependency_graph_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase60a_qwen_read_only_terminal_freeze_stub.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase31b_historical_bars_multi_symbol_validation.py": [
      "backend.app.stacks.market_data.yfinance_historical_bars_adapter",
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase23a_frontend_request_normalizer.py": [
      "pathlib"
    ],
    "scripts/phase28c_candidate_sandbox_mock_scorecard.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase44c_handoff_bundle_refresh.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase51c_handoff_bundle_refresh.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase34b_entry_signal_rule_validation_stub.py": [
      "backend.app.stacks.strategy_candidate_sandbox.entry_signal_rule_contract",
      "backend.app.stacks.strategy_candidate_sandbox.entry_signal_rule_validator",
      "datetime",
      "json",
      "pathlib",
      "py_compile"
    ],
    "scripts/phase46a_qwen_read_only_missing_context_detector_stub.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase24b_persist_observability_backend_health_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase33c_trade_simulation_dry_run_stub.py": [
      "backend.app.stacks.market_data.yfinance_historical_bars_adapter",
      "backend.app.stacks.strategy_candidate_sandbox.trade_simulation_dry_run_stub",
      "datetime",
      "json",
      "pathlib",
      "py_compile"
    ],
    "scripts/phase9l_stack_layer_sankey_export.py": [
      "collections",
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase38d_handoff_bundle_refresh.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase13e_portfolio_service_chain_graph_export.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase59c_handoff_bundle_refresh.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase46c_handoff_bundle_refresh.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase10_domain_subsystem_visualization.py": [
      "json",
      "matplotlib.pyplot",
      "networkx",
      "pathlib"
    ],
    "scripts/phase35e_strategy_sandbox_wiregraph_certification.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase30f_yfinance_historical_bars_adapter_wire_preview_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase24a_frontend_observability_dashboard.py": [
      "pathlib"
    ],
    "scripts/phase30d_yfinance_historical_bars_adapter_stub_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase9m_canonical_graph_certification_v2.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase53c_handoff_bundle_refresh.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase7a_dependency_topology_overlay_export.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase34d_entry_signal_pipeline_rollup_certification.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase6b_dependency_validation_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase51b_qwen_read_only_architecture_loop_boundary_rollup_certification.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase27e_candidate_sandbox_result_stub_generator_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase10f_architecture_drift_watch_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase1_repo_research_market_bootstrap.py": [
      "ast",
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase58b_qwen_read_only_final_context_package_rollup_certification.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase14e_strategy_service_chain_graph_export.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/orphan_finalizer_v1.py": [
      "json",
      "pathlib"
    ],
    "scripts/phase33f_entry_exit_decision_engine_stub.py": [
      "backend.app.stacks.market_data.yfinance_historical_bars_adapter",
      "backend.app.stacks.strategy_candidate_sandbox.entry_exit_decision_engine_stub",
      "backend.app.stacks.strategy_candidate_sandbox.hold_signal_generator_stub",
      "datetime",
      "json",
      "pathlib",
      "py_compile"
    ],
    "scripts/phase24c_observability_event_timeline_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase28b_candidate_sandbox_mock_metrics_generator_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase56c_handoff_bundle_refresh.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase15_risk_gate_service_chain.py": [
      "pathlib"
    ],
    "scripts/phase20_floating_chat_widget_service_chain.py": [
      "pathlib"
    ],
    "scripts/phase33i_handoff_bundle_refresh.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase49a_qwen_read_only_architecture_session_contract_stub.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase11g_live_market_dashboard_expansion_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase30f_yfinance_historical_bars_adapter_wire_preview.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase44b_qwen_read_only_response_sample_rollup_certification.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase54b_qwen_read_only_handoff_export_summary_rollup_certification.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase36d_handoff_bundle_refresh.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase31e_first_single_candidate_replay_dry_run.py": [
      "backend.app.stacks.market_data.yfinance_historical_bars_adapter",
      "backend.app.stacks.strategy_candidate_sandbox.historical_replay_bar_iterator",
      "backend.app.stacks.strategy_candidate_sandbox.historical_replay_executor",
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase13_portfolio_positions_service_chain.py": [
      "pathlib"
    ],
    "scripts/phase5c_repo_memory_certification_v2.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase27b_strategy_candidate_review_index_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase14f_strategy_decision_service_chain_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase45c_handoff_bundle_refresh.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase39c_handoff_bundle_refresh.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase60c_handoff_bundle_refresh.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase9c_generate_layer_colored_wire_graph.py": [
      "json",
      "matplotlib.pyplot",
      "networkx",
      "pathlib"
    ],
    "scripts/phase27c_candidate_sandbox_dry_run_stub.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase29g_historical_replay_provider_readiness_snapshot.py": [
      "datetime",
      "hashlib",
      "json",
      "pathlib",
      "subprocess"
    ],
    "scripts/phase30g_yfinance_historical_bars_adapter_wire_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase32e_handoff_bundle_refresh.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase37d_handoff_bundle_refresh.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase28a_candidate_sandbox_simulation_harness_stub.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase37a_trade_simulation_enablement_gate_contract_stub.py": [
      "backend.app.stacks.strategy_candidate_sandbox.trade_simulation_enablement_gate_contract",
      "datetime",
      "json",
      "pathlib",
      "py_compile"
    ],
    "scripts/phase39a_master_sandbox_gate_wiregraph_refresh.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase29f_historical_replay_provider_adapter_stub.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase14g_strategy_chain_dashboard_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/reconcile_repo_state_v1.py": [
      "json",
      "pathlib"
    ],
    "scripts/phase15g_add_risk_chain_to_dashboard.py": [
      "pathlib"
    ],
    "scripts/architecture_normalization_engine_v1.py": [
      "collections",
      "json",
      "pathlib"
    ],
    "scripts/phase52c_handoff_bundle_refresh.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase14g_add_strategy_chain_to_dashboard.py": [
      "pathlib"
    ],
    "scripts/phase33e_hold_signal_generator_stub.py": [
      "backend.app.stacks.market_data.yfinance_historical_bars_adapter",
      "backend.app.stacks.strategy_candidate_sandbox.hold_signal_generator_stub",
      "datetime",
      "json",
      "pathlib",
      "py_compile"
    ],
    "scripts/phase37b_trade_simulation_enablement_gate_validation_stub.py": [
      "backend.app.stacks.strategy_candidate_sandbox.trade_simulation_enablement_gate_contract",
      "backend.app.stacks.strategy_candidate_sandbox.trade_simulation_enablement_gate_validator",
      "datetime",
      "json",
      "pathlib",
      "py_compile"
    ],
    "scripts/phase34c_entry_signal_generator_disabled_stub.py": [
      "backend.app.stacks.market_data.yfinance_historical_bars_adapter",
      "backend.app.stacks.strategy_candidate_sandbox.entry_signal_generator_disabled_stub",
      "backend.app.stacks.strategy_candidate_sandbox.entry_signal_rule_contract",
      "datetime",
      "json",
      "pathlib",
      "py_compile"
    ],
    "scripts/phase29e_historical_replay_market_data_provider_contract_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase58c_handoff_bundle_refresh.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase11d_next_api_proxy_live_price_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase24b_persist_observability_backend_health.py": [
      "pathlib"
    ],
    "scripts/phase31d_historical_replay_bar_iterator.py": [
      "backend.app.stacks.market_data.yfinance_historical_bars_adapter",
      "backend.app.stacks.strategy_candidate_sandbox.historical_replay_bar_iterator",
      "datetime",
      "json",
      "pathlib",
      "py_compile"
    ],
    "scripts/phase10c_runtime_flow_overlay_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase33g_hold_decision_to_hold_event_bridge.py": [
      "backend.app.stacks.market_data.yfinance_historical_bars_adapter",
      "backend.app.stacks.strategy_candidate_sandbox.entry_exit_decision_engine_stub",
      "backend.app.stacks.strategy_candidate_sandbox.hold_decision_to_hold_event_bridge",
      "backend.app.stacks.strategy_candidate_sandbox.hold_signal_generator_stub",
      "datetime",
      "json",
      "pathlib",
      "py_compile"
    ],
    "scripts/phase19_dashboard_visual_layout_hardening.py": [
      "pathlib"
    ],
    "scripts/phase33b_trade_event_validation_stub.py": [
      "backend.app.stacks.strategy_candidate_sandbox.trade_event_validator",
      "datetime",
      "json",
      "pathlib",
      "py_compile"
    ],
    "scripts/phase7g_graph_visualization_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase29d_historical_replay_readiness_snapshot.py": [
      "datetime",
      "hashlib",
      "json",
      "pathlib",
      "subprocess"
    ],
    "scripts/phase9b_component_overlay_export.py": [
      "collections",
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase43a_qwen_context_response_contract_stub.py": [
      "backend.app.stacks.strategy_candidate_sandbox.qwen_context_response_contract",
      "datetime",
      "json",
      "pathlib",
      "py_compile"
    ],
    "scripts/phase8c_neuro_cli_hotspots_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase58a_qwen_read_only_final_context_package_stub.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase13g_portfolio_chain_dashboard_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase13g_add_portfolio_chain_to_dashboard.py": [
      "pathlib"
    ],
    "scripts/phase3m_graph_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase40c_handoff_bundle_refresh.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase48b_qwen_read_only_response_validator_rollup_certification.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase38b_risk_gate_validation_stub.py": [
      "backend.app.stacks.strategy_candidate_sandbox.risk_gate_contract",
      "backend.app.stacks.strategy_candidate_sandbox.risk_gate_validator",
      "datetime",
      "json",
      "pathlib",
      "py_compile"
    ],
    "scripts/phase19c_endpoint_activation_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase17_dashboard_route_map_frontend_card_verification.py": [
      "datetime",
      "json",
      "pathlib",
      "re"
    ],
    "scripts/phase34e_handoff_bundle_refresh.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase29b_historical_replay_input_contract.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase59a_qwen_read_only_final_handoff_certification_stub.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase30c_historical_bars_contract.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase55c_handoff_bundle_refresh.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase56b_qwen_read_only_architecture_policy_map_rollup_certification.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase28d_candidate_sandbox_execution_contract_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase32d_pipeline_rollup_certification.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase50a_qwen_read_only_session_response_bridge_stub.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase21cd_chat_ux_persistent_cache_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase26b_wire_ollama_into_chat_runtime.py": [
      "pathlib"
    ],
    "scripts/phase29f_historical_replay_provider_adapter_stub_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase25b_tab_layout_polish_chat_panel.py": [
      "pathlib"
    ],
    "scripts/phase10g_architecture_drift_dashboard_summary.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase25c_split_dashboard_panels_into_tab_workspaces_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase11f_frontend_type_lint_repair.py": [
      "pathlib",
      "re"
    ],
    "scripts/phase10c_domain_runtime_overlay_visualization.py": [
      "json",
      "matplotlib.pyplot",
      "networkx",
      "pathlib"
    ],
    "scripts/phase15e_risk_service_chain_graph_export.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase22b_live_graph_visualization_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase38c_risk_gate_pipeline_rollup_certification.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase15g_risk_chain_dashboard_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase26d_frontend_chat_response_normalizer.py": [
      "pathlib"
    ],
    "scripts/phase47a_qwen_read_only_recommendation_filter_stub.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase43c_handoff_bundle_refresh.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase27a_strategy_proposal_capture.py": [
      "pathlib"
    ],
    "scripts/phase24c_observability_event_timeline.py": [
      "pathlib"
    ],
    "scripts/phase16_api_route_separation_certification.py": [
      "backend.app.main",
      "datetime",
      "fastapi.routing",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase42b_qwen_read_only_architecture_context_rollup_certification.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase28d_candidate_sandbox_execution_contract.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase50b_qwen_read_only_session_response_bridge_rollup_certification.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase29a_historical_replay_engine_stub_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase49c_handoff_bundle_refresh.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/apply_service_relocation_v1.py": [
      "json",
      "os",
      "pathlib",
      "shutil"
    ],
    "scripts/phase30c_historical_bars_contract_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase55a_qwen_read_only_architecture_state_machine_stub.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase22b_live_graph_visualization.py": [
      "pathlib"
    ],
    "scripts/phase45b_qwen_read_only_architecture_summary_gate_rollup_certification.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase17_dashboard_route_map_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase35b_exit_signal_rule_validation_stub.py": [
      "backend.app.stacks.strategy_candidate_sandbox.exit_signal_rule_contract",
      "backend.app.stacks.strategy_candidate_sandbox.exit_signal_rule_validator",
      "datetime",
      "json",
      "pathlib",
      "py_compile"
    ],
    "scripts/phase11e_frontend_build_type_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase10e_diff_classification_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase12g_add_service_chain_to_dashboard.py": [
      "pathlib"
    ],
    "scripts/phase26c_chat_safety_prompt_live_execution_guard_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase42c_handoff_bundle_refresh.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase27f_candidate_sandbox_readiness_lock_snapshot.py": [
      "datetime",
      "hashlib",
      "json",
      "pathlib",
      "subprocess"
    ],
    "scripts/phase21ab_chat_cache_history_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase29c_historical_replay_validation_stub_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase47c_handoff_bundle_refresh.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase42a_qwen_read_only_architecture_context_stub.py": [
      "backend.app.stacks.strategy_candidate_sandbox.qwen_read_only_architecture_context",
      "datetime",
      "json",
      "pathlib",
      "py_compile"
    ],
    "scripts/phase28a_candidate_sandbox_simulation_harness_stub_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/topology_state_lock_v1.py": [
      "collections",
      "json",
      "pathlib"
    ],
    "scripts/phase11b_frontend_live_price_card_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase52a_qwen_read_only_final_guardrail_summary_stub.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase28c_candidate_sandbox_mock_scorecard_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase14_strategy_decision_service_chain.py": [
      "pathlib"
    ],
    "scripts/phase50c_handoff_bundle_refresh.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase24d_observability_lock_handoff_snapshot.py": [
      "datetime",
      "hashlib",
      "json",
      "pathlib",
      "subprocess"
    ],
    "scripts/phase61a_archive_or_new_chat_handoff_summary.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase27d_candidate_sandbox_result_schema.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase46b_qwen_read_only_missing_context_detector_rollup_certification.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase49b_qwen_read_only_architecture_session_contract_rollup_certification.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase41c_handoff_bundle_refresh.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase29e_historical_replay_market_data_provider_contract.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase31c_historical_replay_executor_stub.py": [
      "backend.app.stacks.strategy_candidate_sandbox.historical_replay_executor",
      "datetime",
      "json",
      "pathlib",
      "py_compile"
    ],
    "scripts/phase41b_safe_read_only_architecture_inspector_rollup_certification.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/service_stack_relocator_v1.py": [
      "json",
      "pathlib"
    ],
    "scripts/phase26e_chat_metadata_chips_typing_enter.py": [
      "pathlib",
      "re"
    ],
    "scripts/phase44a_qwen_read_only_response_sample_stub.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase33a_trade_simulation_contract_stub.py": [
      "backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract",
      "datetime",
      "json",
      "pathlib",
      "py_compile"
    ],
    "scripts/phase11c_frontend_polling_api_cleanup_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase11f_frontend_type_lint_repair_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase10d_runtime_static_dependency_diff.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase15f_risk_gate_service_chain_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase30d_yfinance_historical_bars_adapter_stub.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase10_domain_subsystem_visualization_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase34a_entry_signal_rule_contract_stub.py": [
      "backend.app.stacks.strategy_candidate_sandbox.entry_signal_rule_contract",
      "datetime",
      "json",
      "pathlib",
      "py_compile"
    ],
    "scripts/phase4c_loose_root_duplicate_quarantine_plan.py": [
      "datetime",
      "hashlib",
      "json",
      "pathlib"
    ],
    "scripts/phase56a_qwen_read_only_architecture_policy_map_stub.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase4_repo_memory_indexer_v2.py": [
      "ast",
      "collections",
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase38a_risk_gate_contract_stub.py": [
      "backend.app.stacks.strategy_candidate_sandbox.risk_gate_contract",
      "datetime",
      "json",
      "pathlib",
      "py_compile"
    ],
    "scripts/phase12e_service_chain_graph_export.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase21ab_chat_cache_history.py": [
      "pathlib"
    ],
    "scripts/phase62a_master_architecture_handoff_controller.py": [
      "__future__",
      "collections",
      "datetime",
      "json",
      "os",
      "pathlib"
    ],
    "scripts/phase57b_qwen_read_only_policy_boundary_matrix_rollup_certification.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase29a_historical_replay_engine_stub.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase30e_yfinance_historical_bars_adapter_shape_validation_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase53a_qwen_read_only_handoff_freeze_stub.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase11b_frontend_live_price_card.py": [
      "pathlib"
    ],
    "scripts/phase36c_enablement_gate_pipeline_rollup_certification.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase32c_manual_promotion_gate_stub.py": [
      "backend.app.stacks.market_data.yfinance_historical_bars_adapter",
      "backend.app.stacks.strategy_candidate_sandbox.candidate_scorecard_from_replay_metrics",
      "backend.app.stacks.strategy_candidate_sandbox.manual_promotion_gate",
      "backend.app.stacks.strategy_candidate_sandbox.replay_metrics_generator",
      "datetime",
      "json",
      "pathlib",
      "py_compile"
    ],
    "scripts/phase24a_frontend_observability_dashboard_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase37c_trade_simulation_enablement_gate_pipeline_rollup_certification.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase22_live_graph_tab.py": [
      "pathlib"
    ],
    "scripts/phase9k_domain_subsystem_graph_export.py": [
      "collections",
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase20e_chat_service_chain_graph_export.py": [
      "datetime",
      "json",
      "pathlib"
    ],
    "scripts/phase27c_candidate_sandbox_dry_run_stub_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "scripts/phase25b_tab_layout_polish_chat_panel_certification.py": [
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys"
    ],
    "backend/__init__.py": [],
    "backend/app/main.py": [
      "asyncio",
      "backend.app.core.cognitive_graph_state",
      "backend.app.core.global_firewall_v1",
      "backend.app.stacks.chat_public.chat_api",
      "backend.app.stacks.events.broker",
      "backend.app.stacks.execution.paper_broker",
      "backend.app.stacks.journal_ledger.ledger",
      "backend.app.stacks.market_data.market_data_service",
      "backend.app.stacks.portfolio.portfolio_service",
      "backend.app.stacks.portfolio.reconciliation",
      "backend.app.stacks.risk.risk_service",
      "backend.app.stacks.strategy.engine",
      "backend.app.stacks.strategy.strategy_service",
      "contextlib",
      "fastapi",
      "fastapi.middleware.cors",
      "json",
      "sqlalchemy",
      "subprocess"
    ],
    "backend/app/__init__.py": [],
    "backend/app/schemas/__init__.py": [],
    "backend/app/schemas/dashboard.py": [
      "datetime",
      "pydantic",
      "typing"
    ],
    "backend/app/test/test_neuro_repo_companion.py": [],
    "backend/app/test/test_trading_pipeline.py": [
      "backend.app.stacks.execution.paper_broker",
      "backend.app.stacks.wolfden_ai.agent_router",
      "pytest",
      "unittest.mock"
    ],
    "backend/app/api/graph_ws.py": [
      "asyncio",
      "backend.app.core.cognitive_graph_state",
      "fastapi"
    ],
    "backend/app/services/__init__.py": [],
    "backend/app/analysis/architecture.py": [],
    "backend/app/core/cognitive_nodes.py": [],
    "backend/app/core/__init__.py": [],
    "backend/app/core/cognitive_types.py": [],
    "backend/app/core/config.py": [
      "os",
      "pydantic_settings"
    ],
    "backend/app/core/cognitive_graph_state.py": [
      "collections",
      "datetime",
      "json",
      "pathlib"
    ],
    "backend/app/core/cognitive_event_bus.py": [
      "asyncio",
      "backend.app.core.cognitive_graph_state",
      "collections"
    ],
    "backend/app/core/runtime_firewall_v1.py": [
      "inspect",
      "pathlib",
      "sys"
    ],
    "backend/app/core/global_firewall_v1.py": [
      "importlib.abc",
      "importlib.util",
      "pathlib",
      "sys"
    ],
    "backend/app/stacks/__init__.py": [],
    "backend/app/routers/__init__.py": [],
    "backend/app/snaptrade/executions/config.py": [],
    "backend/app/snaptrade/executions/execution_layer.py": [],
    "backend/app/stacks/strategy/strategy_registry.py": [],
    "backend/app/stacks/strategy/strategy_service.py": [
      "backend.app.stacks.strategy.engine"
    ],
    "backend/app/stacks/strategy/strategy_runtime.py": [],
    "backend/app/stacks/strategy/__init__.py": [],
    "backend/app/stacks/strategy/selector.py": [],
    "backend/app/stacks/strategy/signal.py": [
      "numpy"
    ],
    "backend/app/stacks/strategy/engine.py": [
      "backend.app.stacks.market_data.bars",
      "backend.app.stacks.market_data.price",
      "backend.app.stacks.portfolio.rebalance",
      "backend.app.stacks.strategy.signal"
    ],
    "backend/app/stacks/strategy/evolution_engine.py": [],
    "backend/app/stacks/strategy/llm_strategy_engine.py": [
      "json",
      "subprocess",
      "typing"
    ],
    "backend/app/stacks/strategy/candidate_registry.py": [],
    "backend/app/stacks/strategy/base.py": [],
    "backend/app/stacks/portfolio/portfolio_service.py": [
      "backend.app.stacks.execution.paper_broker"
    ],
    "backend/app/stacks/portfolio/allocator.py": [
      "backend.app.stacks.market_data.bars"
    ],
    "backend/app/stacks/portfolio/__init__.py": [],
    "backend/app/stacks/portfolio/accounting.py": [
      "backend.app.stacks.journal_ledger.ledger",
      "sqlalchemy"
    ],
    "backend/app/stacks/portfolio/portfolio_runtime.py": [],
    "backend/app/stacks/portfolio/reconciliation.py": [
      "asyncio",
      "backend.app.stacks.journal_ledger.ledger",
      "sqlalchemy"
    ],
    "backend/app/stacks/portfolio/dashboard_service.py": [
      "decimal",
      "typing"
    ],
    "backend/app/stacks/portfolio/rebalance.py": [],
    "backend/app/stacks/portfolio/base.py": [],
    "backend/app/stacks/auth_identity/__init__.py": [],
    "backend/app/stacks/auth_identity/base.py": [],
    "backend/app/stacks/auth_identity/validator.py": [],
    "backend/app/stacks/auth_identity/gate.py": [],
    "backend/app/stacks/notification/__init__.py": [],
    "backend/app/stacks/notification/base.py": [],
    "backend/app/stacks/execution/__init__.py": [],
    "backend/app/stacks/execution/sandbox_runtime.py": [],
    "backend/app/stacks/execution/commission_engine.py": [],
    "backend/app/stacks/execution/sandbox.py": [],
    "backend/app/stacks/execution/regime_modes.py": [],
    "backend/app/stacks/execution/pnl_engine.py": [],
    "backend/app/stacks/execution/executor.py": [],
    "backend/app/stacks/execution/trade_ledger.py": [],
    "backend/app/stacks/execution/regime_simulator.py": [],
    "backend/app/stacks/execution/paper_broker.py": [
      "backend.app.stacks.journal_ledger.ledger",
      "backend.app.stacks.market_data.bars",
      "backend.app.stacks.market_data.feed",
      "backend.app.stacks.market_data.price",
      "backend.app.stacks.portfolio.accounting",
      "backend.app.stacks.portfolio.allocator",
      "backend.app.stacks.portfolio.rebalance",
      "backend.app.stacks.risk.drawdown_guard",
      "backend.app.stacks.risk.kill_switch",
      "backend.app.stacks.strategy.signal",
      "random"
    ],
    "backend/app/stacks/execution/broker.py": [],
    "backend/app/stacks/execution/fill_engine.py": [],
    "backend/app/stacks/execution/base.py": [],
    "backend/app/stacks/execution/accounting_engine.py": [],
    "backend/app/stacks/wolfden_ai/memory.py": [],
    "backend/app/stacks/wolfden_ai/__init__.py": [],
    "backend/app/stacks/wolfden_ai/agent_router.py": [
      "backend.app.stacks.execution.paper_broker",
      "backend.app.stacks.journal_ledger.ledger",
      "backend.app.stacks.risk.drawdown_guard",
      "backend.app.stacks.risk.kill_switch",
      "backend.app.stacks.strategy.engine",
      "time"
    ],
    "backend/app/stacks/wolfden_ai/orchestrator.py": [],
    "backend/app/stacks/wolfden_ai/routing.py": [],
    "backend/app/stacks/wolfden_ai/runtime.py": [],
    "backend/app/stacks/wolfden_ai/base.py": [],
    "backend/app/stacks/chat_public/chat_intent_regex.py": [
      "dataclasses",
      "re"
    ],
    "backend/app/stacks/chat_public/context_loader.py": [
      "json",
      "pathlib"
    ],
    "backend/app/stacks/chat_public/__init__.py": [],
    "backend/app/stacks/chat_public/chat_runtime.py": [
      "backend.app.stacks.chat_public.chat_intent_regex",
      "backend.app.stacks.chat_public.ollama_chat_client",
      "backend.app.stacks.chat_public.strategy_proposal_capture"
    ],
    "backend/app/stacks/chat_public/chat_system_prompt.py": [],
    "backend/app/stacks/chat_public/conversation_store.py": [],
    "backend/app/stacks/chat_public/chat_memory.py": [],
    "backend/app/stacks/chat_public/ollama_chat_client.py": [
      "backend.app.stacks.chat_public.chat_system_prompt",
      "backend.app.stacks.chat_public.time_context",
      "json",
      "urllib.request"
    ],
    "backend/app/stacks/chat_public/chat_service.py": [],
    "backend/app/stacks/chat_public/time_context.py": [
      "datetime",
      "zoneinfo"
    ],
    "backend/app/stacks/chat_public/strategy_proposal_capture.py": [
      "datetime",
      "json",
      "pathlib",
      "re",
      "uuid"
    ],
    "backend/app/stacks/chat_public/base.py": [],
    "backend/app/stacks/chat_public/chat_api.py": [
      "backend.app.stacks.chat_public.chat_runtime",
      "fastapi"
    ],
    "backend/app/stacks/strategy_candidate_sandbox/replay_metrics_generator.py": [
      "__future__",
      "math",
      "typing"
    ],
    "backend/app/stacks/strategy_candidate_sandbox/hold_signal_generator_stub.py": [
      "__future__",
      "backend.app.stacks.strategy_candidate_sandbox.entry_exit_signal_contract",
      "backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract",
      "typing"
    ],
    "backend/app/stacks/strategy_candidate_sandbox/qwen_context_response_contract.py": [
      "__future__",
      "typing"
    ],
    "backend/app/stacks/strategy_candidate_sandbox/replay_metrics_contract.py": [
      "__future__",
      "typing"
    ],
    "backend/app/stacks/strategy_candidate_sandbox/strategy_rule_enablement_gate_contract.py": [
      "__future__",
      "backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract",
      "typing"
    ],
    "backend/app/stacks/strategy_candidate_sandbox/safe_read_only_architecture_inspector.py": [
      "__future__",
      "typing"
    ],
    "backend/app/stacks/strategy_candidate_sandbox/trade_event_validator.py": [
      "__future__",
      "backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract",
      "typing"
    ],
    "backend/app/stacks/strategy_candidate_sandbox/entry_exit_signal_contract.py": [
      "__future__",
      "backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract",
      "typing"
    ],
    "backend/app/stacks/strategy_candidate_sandbox/hold_decision_to_hold_event_bridge.py": [
      "__future__",
      "backend.app.stacks.strategy_candidate_sandbox.trade_event_validator",
      "backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract",
      "typing"
    ],
    "backend/app/stacks/strategy_candidate_sandbox/entry_signal_rule_contract.py": [
      "__future__",
      "backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract",
      "typing"
    ],
    "backend/app/stacks/strategy_candidate_sandbox/exit_signal_rule_contract.py": [
      "__future__",
      "backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract",
      "typing"
    ],
    "backend/app/stacks/strategy_candidate_sandbox/qwen_read_only_architecture_summary_gate.py": [
      "__future__",
      "typing"
    ],
    "backend/app/stacks/strategy_candidate_sandbox/trade_simulation_enablement_gate_contract.py": [
      "__future__",
      "backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract",
      "typing"
    ],
    "backend/app/stacks/strategy_candidate_sandbox/exit_signal_rule_validator.py": [
      "__future__",
      "backend.app.stacks.strategy_candidate_sandbox.exit_signal_rule_contract",
      "backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract",
      "typing"
    ],
    "backend/app/stacks/strategy_candidate_sandbox/qwen_read_only_architecture_context.py": [
      "__future__",
      "typing"
    ],
    "backend/app/stacks/strategy_candidate_sandbox/risk_gate_validator.py": [
      "__future__",
      "backend.app.stacks.strategy_candidate_sandbox.risk_gate_contract",
      "backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract",
      "typing"
    ],
    "backend/app/stacks/strategy_candidate_sandbox/entry_signal_rule_validator.py": [
      "__future__",
      "backend.app.stacks.strategy_candidate_sandbox.entry_signal_rule_contract",
      "backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract",
      "typing"
    ],
    "backend/app/stacks/strategy_candidate_sandbox/trade_simulation_dry_run_stub.py": [
      "__future__",
      "backend.app.stacks.strategy_candidate_sandbox.trade_event_validator",
      "backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract",
      "typing"
    ],
    "backend/app/stacks/strategy_candidate_sandbox/historical_replay_bar_iterator.py": [
      "__future__",
      "typing"
    ],
    "backend/app/stacks/strategy_candidate_sandbox/candidate_scorecard_from_replay_metrics.py": [
      "__future__",
      "typing"
    ],
    "backend/app/stacks/strategy_candidate_sandbox/entry_signal_generator_disabled_stub.py": [
      "__future__",
      "backend.app.stacks.strategy_candidate_sandbox.entry_signal_rule_validator",
      "backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract",
      "typing"
    ],
    "backend/app/stacks/strategy_candidate_sandbox/trade_simulation_contract.py": [
      "__future__",
      "typing"
    ],
    "backend/app/stacks/strategy_candidate_sandbox/historical_replay_executor.py": [
      "__future__",
      "typing"
    ],
    "backend/app/stacks/strategy_candidate_sandbox/strategy_rule_enablement_gate_validator.py": [
      "__future__",
      "backend.app.stacks.strategy_candidate_sandbox.strategy_rule_enablement_gate_contract",
      "backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract",
      "typing"
    ],
    "backend/app/stacks/strategy_candidate_sandbox/manual_promotion_gate.py": [
      "__future__",
      "typing"
    ],
    "backend/app/stacks/strategy_candidate_sandbox/exit_signal_generator_disabled_stub.py": [
      "__future__",
      "backend.app.stacks.strategy_candidate_sandbox.exit_signal_rule_validator",
      "backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract",
      "typing"
    ],
    "backend/app/stacks/strategy_candidate_sandbox/trade_simulation_enablement_gate_validator.py": [
      "__future__",
      "backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract",
      "backend.app.stacks.strategy_candidate_sandbox.trade_simulation_enablement_gate_contract",
      "typing"
    ],
    "backend/app/stacks/strategy_candidate_sandbox/risk_gate_contract.py": [
      "__future__",
      "backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract",
      "typing"
    ],
    "backend/app/stacks/strategy_candidate_sandbox/entry_exit_decision_engine_stub.py": [
      "__future__",
      "backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract",
      "typing"
    ],
    "backend/app/stacks/db_model/__init__.py": [],
    "backend/app/stacks/db_model/market_schema.py": [
      "datetime",
      "sqlalchemy",
      "sqlalchemy.orm"
    ],
    "backend/app/stacks/db_model/base.py": [],
    "backend/app/stacks/events/broker.py": [
      "asyncio",
      "backend.app.core.cognitive_graph_state"
    ],
    "backend/app/stacks/market_data/yfinance_ingestor.py": [
      "backend.app.stacks.db_model.market_schema",
      "backend.app.stacks.journal_ledger.ledger",
      "datetime",
      "yfinance"
    ],
    "backend/app/stacks/market_data/provider_registry.py": [],
    "backend/app/stacks/market_data/__init__.py": [],
    "backend/app/stacks/market_data/feed.py": [
      "asyncio",
      "concurrent.futures",
      "yfinance"
    ],
    "backend/app/stacks/market_data/market_data_service.py": [
      "backend.app.stacks.market_data.feed"
    ],
    "backend/app/stacks/market_data/bars.py": [
      "yfinance"
    ],
    "backend/app/stacks/market_data/market_session.py": [],
    "backend/app/stacks/market_data/provider_router.py": [],
    "backend/app/stacks/market_data/price.py": [],
    "backend/app/stacks/market_data/yfinance_historical_bars_adapter.py": [
      "__future__",
      "math",
      "typing",
      "yfinance"
    ],
    "backend/app/stacks/market_data/provider_cache.py": [],
    "backend/app/stacks/market_data/base.py": [],
    "backend/app/stacks/learning_research/strategy_evaluator.py": [],
    "backend/app/stacks/learning_research/__init__.py": [],
    "backend/app/stacks/learning_research/monte_carlo_mix.py": [],
    "backend/app/stacks/learning_research/monte_carlo.py": [],
    "backend/app/stacks/learning_research/research_loader.py": [
      "backend.app.stacks.db_model.market_schema",
      "backend.app.stacks.journal_ledger.ledger"
    ],
    "backend/app/stacks/learning_research/probability_engine.py": [],
    "backend/app/stacks/learning_research/research_runtime.py": [],
    "backend/app/stacks/learning_research/base.py": [],
    "backend/app/stacks/learning_research/backtest_engine.py": [],
    "backend/app/stacks/risk/loss_streak_guard.py": [],
    "backend/app/stacks/risk/__init__.py": [],
    "backend/app/stacks/risk/drawdown_guard.py": [
      "backend.app.stacks.journal_ledger.ledger",
      "datetime",
      "sqlalchemy"
    ],
    "backend/app/stacks/risk/risk_runtime_service.py": [],
    "backend/app/stacks/risk/exposure.py": [],
    "backend/app/stacks/risk/kill_switch.py": [],
    "backend/app/stacks/risk/limits.py": [],
    "backend/app/stacks/risk/base.py": [],
    "backend/app/stacks/risk/risk_service.py": [
      "backend.app.stacks.risk.drawdown_guard"
    ],
    "backend/app/stacks/journal_ledger/ledger.py": [
      "datetime",
      "sqlalchemy",
      "sqlalchemy.ext.asyncio",
      "sqlalchemy.orm"
    ],
    "backend/app/stacks/journal_ledger/__init__.py": [],
    "backend/app/stacks/journal_ledger/record.py": [
      "datetime"
    ],
    "backend/app/stacks/journal_ledger/base.py": [],
    "backend/app/stacks/snaptrade/__init__.py": [],
    "backend/app/stacks/snaptrade/execution.py": [],
    "backend/app/stacks/snaptrade/adapter.py": [],
    "backend/app/stacks/snaptrade/broker.py": [],
    "backend/app/stacks/snaptrade/base.py": [],
    "scripts/ci/architecture_ci_guard_v1.py": [
      "ast",
      "pathlib",
      "sys"
    ]
  }
}
```

---

# 23. [Dependency Atlas] Dependency Graph

Source: `handoff/project_bible/DEPENDENCY_GRAPH.md`

# Dependency Graph

```text
HIGH-LEVEL DEPENDENCY GRAPH

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

```

---

# 24. [Runtime State] Runtime State Machine

Source: `handoff/runtime_state_machine.txt`

```text
QWEN READ-ONLY STATE MACHINE

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
```

---

# 25. [Flows] Data Flow

Source: `handoff/project_bible/DATA_FLOW.md`

# Data Flow


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

---

# 26. [Flows] Market Data

Source: `handoff/project_bible/architecture_atlas/FLOWS/market_data.md`

# Market Data Flow

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

---

# 27. [Flows] Candidate Pipeline

Source: `handoff/project_bible/architecture_atlas/FLOWS/candidate_pipeline.md`

# Candidate Pipeline

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

---

# 28. [Flows] Execution Disabled

Source: `handoff/project_bible/architecture_atlas/FLOWS/execution_disabled.md`

# Execution Flow — Disabled

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

---

# 29. [Qwen Read-Only] Qwen Read Only Architecture

Source: `handoff/project_bible/QWEN_READ_ONLY_ARCHITECTURE.md`

# Qwen Read-Only Architecture


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

---

# 30. [Certification History] Certification Timeline

Source: `handoff/certification_timeline.txt`

```text
• candidate_sandbox_result_schema_v1

• 27C_CANDIDATE_SANDBOX_DRY_RUN_STUB

• 27E_CANDIDATE_SANDBOX_RESULT_STUB_GENERATOR

• 28A_CANDIDATE_SANDBOX_SIMULATION_HARNESS_STUB

• 28B_CANDIDATE_SANDBOX_MOCK_METRICS_GENERATOR

• 28C_CANDIDATE_SANDBOX_MOCK_SCORECARD

• 28D_CANDIDATE_SANDBOX_EXECUTION_CONTRACT

• 29A_HISTORICAL_REPLAY_ENGINE_STUB

• 29B_HISTORICAL_REPLAY_INPUT_CONTRACT

• 29C_HISTORICAL_REPLAY_VALIDATION_STUB

• 29E_HISTORICAL_REPLAY_MARKET_DATA_PROVIDER_CONTRACT

• 29F_HISTORICAL_REPLAY_PROVIDER_ADAPTER_STUB

• 30A_YFINANCE_HISTORICAL_BARS_PROVIDER_PROBE

• 30C_HISTORICAL_BARS_CONTRACT

• 30D_YFINANCE_HISTORICAL_BARS_ADAPTER_STUB

• 30E_YFINANCE_HISTORICAL_BARS_ADAPTER_SHAPE_VALIDATION

• 30F_YFINANCE_HISTORICAL_BARS_ADAPTER_WIRE_PREVIEW

• 30G_YFINANCE_HISTORICAL_BARS_ADAPTER_WIRE

✅ 31A_HISTORICAL_BARS_FETCH_VALIDATION

✅ 31B_HISTORICAL_BARS_MULTI_SYMBOL_VALIDATION

✅ 31C_HISTORICAL_REPLAY_EXECUTOR_STUB

✅ 31D_HISTORICAL_REPLAY_BAR_ITERATOR

✅ 31E_FIRST_SINGLE_CANDIDATE_REPLAY_DRY_RUN

✅ 31F_REPLAY_METRICS_CONTRACT

✅ 32A_REAL_METRICS_GENERATION

✅ 32B_CANDIDATE_SCORECARD_FROM_REPLAY_METRICS

✅ 32C_MANUAL_PROMOTION_GATE_STUB

✅ 32D_PIPELINE_ROLLUP_CERTIFICATION

✅ 32E_HANDOFF_BUNDLE_REFRESH
   └─ Early Training Infrastructure + Bar-Only Replay Metrics Pipeline Complete
      next: 33A_TRADE_SIMULATION_CONTRACT_STUB

✅ 33A_TRADE_SIMULATION_CONTRACT_STUB

✅ 33B_TRADE_EVENT_VALIDATION_STUB

✅ 33C_TRADE_SIMULATION_DRY_RUN_STUB

✅ 33D_ENTRY_EXIT_SIGNAL_CONTRACT_STUB

✅ 33E_HOLD_SIGNAL_GENERATOR_STUB

✅ 33F_ENTRY_EXIT_DECISION_ENGINE_STUB

✅ 33G_HOLD_DECISION_TO_HOLD_EVENT_BRIDGE

✅ 33H_TRADE_SIMULATION_PIPELINE_ROLLUP_CERTIFICATION
      next: 33I_HANDOFF_BUNDLE_REFRESH

✅ 33I_HANDOFF_BUNDLE_REFRESH
   └─ Early Training Infrastructure + Bar-Only Metrics + Hold-Only Trade Simulation Runway Complete
      next: 34A_ENTRY_SIGNAL_RULE_CONTRACT_STUB

✅ 34A_ENTRY_SIGNAL_RULE_CONTRACT_STUB

✅ 34B_ENTRY_SIGNAL_RULE_VALIDATION_STUB

✅ 34C_ENTRY_SIGNAL_GENERATOR_DISABLED_STUB

✅ 34D_ENTRY_SIGNAL_PIPELINE_ROLLUP_CERTIFICATION
      next: 34E_HANDOFF_BUNDLE_REFRESH

✅ 34E_HANDOFF_BUNDLE_REFRESH
   └─ Early Training Infrastructure + Hold-Only Simulation Runway + Disabled Entry Signal Pipeline Complete
      next: 35A_EXIT_SIGNAL_RULE_CONTRACT_STUB

✅ 35A_EXIT_SIGNAL_RULE_CONTRACT_STUB

✅ 35B_EXIT_SIGNAL_RULE_VALIDATION_STUB

✅ 35C_EXIT_SIGNAL_GENERATOR_DISABLED_STUB

✅ 35D_EXIT_SIGNAL_PIPELINE_ROLLUP_CERTIFICATION
      next: 35E_HANDOFF_BUNDLE_REFRESH

✅ 35E_STRATEGY_SANDBOX_WIREGRAPH_CERTIFICATION
   └─ Strategy sandbox wiregraph certified

✅ 35F_HANDOFF_BUNDLE_REFRESH
   └─ Strategy Sandbox Wiregraph Complete With Entry/Exit Generation Disabled
      next: 36A_STRATEGY_RULE_ENABLEMENT_GATE_CONTRACT_STUB

✅ 36A_STRATEGY_RULE_ENABLEMENT_GATE_CONTRACT_STUB

✅ 36B_ENABLEMENT_GATE_VALIDATION_STUB

✅ 36C_ENABLEMENT_GATE_PIPELINE_ROLLUP_CERTIFICATION
      next: 36D_HANDOFF_BUNDLE_REFRESH

✅ 36D_HANDOFF_BUNDLE_REFRESH
   └─ Strategy Rule Enablement Gate Certified (Locked)
      next: 37A_TRADE_SIMULATION_ENABLEMENT_GATE_CONTRACT_STUB

✅ 37A_TRADE_SIMULATION_ENABLEMENT_GATE_CONTRACT_STUB

✅ 37B_TRADE_SIMULATION_ENABLEMENT_GATE_VALIDATION_STUB

✅ 37C_TRADE_SIMULATION_ENABLEMENT_GATE_PIPELINE_ROLLUP_CERTIFICATION
      next: 37D_HANDOFF_BUNDLE_REFRESH

✅ 37D_HANDOFF_BUNDLE_REFRESH
   └─ Trade Simulation Enablement Gate Certified Locked
      next: 38A_RISK_GATE_CONTRACT_STUB

✅ 38A_RISK_GATE_CONTRACT_STUB

✅ 38B_RISK_GATE_VALIDATION_STUB

✅ 38C_RISK_GATE_PIPELINE_ROLLUP_CERTIFICATION
      next: 38D_HANDOFF_BUNDLE_REFRESH

✅ 38D_HANDOFF_BUNDLE_REFRESH
   └─ Risk Gate Certified Locked
      next: 39A_MASTER_SANDBOX_GATE_WIREGRAPH_REFRESH

✅ 39A_MASTER_SANDBOX_GATE_WIREGRAPH_REFRESH
   └─ Master sandbox gate dependency wiregraph refreshed

✅ 39B_MASTER_SANDBOX_GATE_WIREGRAPH_ROLLUP_CERTIFICATION
      next: 39C_HANDOFF_BUNDLE_REFRESH

✅ 39C_HANDOFF_BUNDLE_REFRESH
   └─ Master Sandbox Gate Wiregraph Certified
      next: 40A_SANDBOX_RUNTIME_DEPENDENCY_TRACE_STUB

✅ 40A_SANDBOX_RUNTIME_DEPENDENCY_TRACE_STUB

✅ 40B_SANDBOX_RUNTIME_DEPENDENCY_TRACE_ROLLUP_CERTIFICATION
      next: 40C_HANDOFF_BUNDLE_REFRESH

✅ 40C_HANDOFF_BUNDLE_REFRESH
   └─ Sandbox Runtime Dependency Trace Certified Locked
      next: 41A_SAFE_READ_ONLY_ARCHITECTURE_INSPECTOR_STUB

✅ 41A_SAFE_READ_ONLY_ARCHITECTURE_INSPECTOR_STUB

✅ 41B_SAFE_READ_ONLY_ARCHITECTURE_INSPECTOR_ROLLUP_CERTIFICATION
      next: 41C_HANDOFF_BUNDLE_REFRESH

✅ 41C_HANDOFF_BUNDLE_REFRESH
   └─ Read-Only Architecture Inspector Certified
      next: 42A_QWEN_READ_ONLY_ARCHITECTURE_CONTEXT_STUB

✅ 42A_QWEN_READ_ONLY_ARCHITECTURE_CONTEXT_STUB

✅ 42B_QWEN_READ_ONLY_ARCHITECTURE_CONTEXT_ROLLUP_CERTIFICATION
      next: 42C_HANDOFF_BUNDLE_REFRESH

✅ 42C_HANDOFF_BUNDLE_REFRESH
   └─ Qwen Read-Only Architecture Context Certified
      next: 43A_QWEN_CONTEXT_RESPONSE_CONTRACT_STUB

✅ 43A_QWEN_CONTEXT_RESPONSE_CONTRACT_STUB

✅ 43B_QWEN_CONTEXT_RESPONSE_CONTRACT_ROLLUP_CERTIFICATION
      next: 43C_HANDOFF_BUNDLE_REFRESH

✅ 43C_HANDOFF_BUNDLE_REFRESH
   └─ Qwen Read-Only Response Contract Certified
      next: 44A_QWEN_READ_ONLY_RESPONSE_SAMPLE_STUB

✅ 44A_QWEN_READ_ONLY_RESPONSE_SAMPLE_STUB

✅ 44B_QWEN_READ_ONLY_RESPONSE_SAMPLE_ROLLUP_CERTIFICATION
      next: 44C_HANDOFF_BUNDLE_REFRESH

✅ 44C_HANDOFF_BUNDLE_REFRESH
   └─ Qwen Read-Only Response Sample Certified
      next: 45A_QWEN_READ_ONLY_ARCHITECTURE_SUMMARY_GATE_STUB

✅ 45A_QWEN_READ_ONLY_ARCHITECTURE_SUMMARY_GATE_STUB

✅ 45B_QWEN_READ_ONLY_ARCHITECTURE_SUMMARY_GATE_ROLLUP_CERTIFICATION
      next: 45C_HANDOFF_BUNDLE_REFRESH

✅ 45C_HANDOFF_BUNDLE_REFRESH
   └─ Qwen Read-Only Architecture Summary Gate Certified
      next: 46A_QWEN_READ_ONLY_MISSING_CONTEXT_DETECTOR_STUB

✅ 46A_QWEN_READ_ONLY_MISSING_CONTEXT_DETECTOR_STUB

✅ 46B_QWEN_READ_ONLY_MISSING_CONTEXT_DETECTOR_ROLLUP_CERTIFICATION
      next: 46C_HANDOFF_BUNDLE_REFRESH

✅ 46C_HANDOFF_BUNDLE_REFRESH
   └─ Qwen Read-Only Missing Context Detector Certified
      next: 47A_QWEN_READ_ONLY_RECOMMENDATION_FILTER_STUB

✅ 47A_QWEN_READ_ONLY_RECOMMENDATION_FILTER_STUB

✅ 47B_QWEN_READ_ONLY_RECOMMENDATION_FILTER_ROLLUP_CERTIFICATION
      next: 47C_HANDOFF_BUNDLE_REFRESH

✅ 47C_HANDOFF_BUNDLE_REFRESH
   └─ Qwen Read-Only Recommendation Filter Certified
      next: 48A_QWEN_READ_ONLY_RESPONSE_VALIDATOR_STUB

✅ 48A_QWEN_READ_ONLY_RESPONSE_VALIDATOR_STUB

✅ 48B_QWEN_READ_ONLY_RESPONSE_VALIDATOR_ROLLUP_CERTIFICATION
      next: 48C_HANDOFF_BUNDLE_REFRESH

✅ 48C_HANDOFF_BUNDLE_REFRESH
   └─ Qwen Read-Only Response Validator Certified
      next: 49A_QWEN_READ_ONLY_ARCHITECTURE_SESSION_CONTRACT_STUB

✅ 49A_QWEN_READ_ONLY_ARCHITECTURE_SESSION_CONTRACT_STUB

✅ 49B_QWEN_READ_ONLY_ARCHITECTURE_SESSION_CONTRACT_ROLLUP_CERTIFICATION
      next: 49C_HANDOFF_BUNDLE_REFRESH

✅ 49C_HANDOFF_BUNDLE_REFRESH
   └─ Qwen Read-Only Architecture Session Contract Certified
      next: 50A_QWEN_READ_ONLY_SESSION_RESPONSE_BRIDGE_STUB

✅ 50A_QWEN_READ_ONLY_SESSION_RESPONSE_BRIDGE_STUB

✅ 50B_QWEN_READ_ONLY_SESSION_RESPONSE_BRIDGE_ROLLUP_CERTIFICATION
      next: 50C_HANDOFF_BUNDLE_REFRESH

✅ 50C_HANDOFF_BUNDLE_REFRESH
   └─ Qwen Read-Only Session Response Bridge Certified
      next: 51A_QWEN_READ_ONLY_ARCHITECTURE_LOOP_BOUNDARY_STUB

✅ 51A_QWEN_READ_ONLY_ARCHITECTURE_LOOP_BOUNDARY_STUB

✅ 51B_QWEN_READ_ONLY_ARCHITECTURE_LOOP_BOUNDARY_ROLLUP_CERTIFICATION
      next: 51C_HANDOFF_BUNDLE_REFRESH

✅ 51C_HANDOFF_BUNDLE_REFRESH
   └─ Qwen Read-Only Architecture Loop Boundary Certified
      next: 52A_QWEN_READ_ONLY_FINAL_GUARDRAIL_SUMMARY_STUB

✅ 52A_QWEN_READ_ONLY_FINAL_GUARDRAIL_SUMMARY_STUB

✅ 52B_QWEN_READ_ONLY_FINAL_GUARDRAIL_SUMMARY_ROLLUP_CERTIFICATION
      next: 52C_HANDOFF_BUNDLE_REFRESH

✅ 52C_HANDOFF_BUNDLE_REFRESH
   └─ Qwen Read-Only Final Guardrail Summary Certified
      next: 53A_QWEN_READ_ONLY_HANDOFF_FREEZE_STUB

✅ 53A_QWEN_READ_ONLY_HANDOFF_FREEZE_STUB

✅ 53B_QWEN_READ_ONLY_HANDOFF_FREEZE_ROLLUP_CERTIFICATION
      next: 53C_HANDOFF_BUNDLE_REFRESH

✅ 53C_HANDOFF_BUNDLE_REFRESH
   └─ Qwen Read-Only Handoff Freeze Certified
      next: 54A_QWEN_READ_ONLY_HANDOFF_EXPORT_SUMMARY_STUB

✅ 54A_QWEN_READ_ONLY_HANDOFF_EXPORT_SUMMARY_STUB

✅ 54B_QWEN_READ_ONLY_HANDOFF_EXPORT_SUMMARY_ROLLUP_CERTIFICATION
      next: 54C_HANDOFF_BUNDLE_REFRESH

✅ 54C_HANDOFF_BUNDLE_REFRESH
   └─ Qwen Read-Only Handoff Export Summary Certified
      next: 55A_QWEN_READ_ONLY_ARCHITECTURE_STATE_MACHINE_STUB

✅ 55A_QWEN_READ_ONLY_ARCHITECTURE_STATE_MACHINE_STUB

✅ 55B_QWEN_READ_ONLY_ARCHITECTURE_STATE_MACHINE_ROLLUP_CERTIFICATION
      next: 55C_HANDOFF_BUNDLE_REFRESH

✅ 55C_HANDOFF_BUNDLE_REFRESH
      next: 56A_QWEN_READ_ONLY_ARCHITECTURE_POLICY_MAP_STUB

✅ 56A_QWEN_READ_ONLY_ARCHITECTURE_POLICY_MAP_STUB

✅ 56B_QWEN_READ_ONLY_ARCHITECTURE_POLICY_MAP_ROLLUP_CERTIFICATION
      next: 56C_HANDOFF_BUNDLE_REFRESH

✅ 56C_HANDOFF_BUNDLE_REFRESH
      next: 57A_QWEN_READ_ONLY_POLICY_BOUNDARY_MATRIX_STUB

✅ 57A_QWEN_READ_ONLY_POLICY_BOUNDARY_MATRIX_STUB

✅ 57B_QWEN_READ_ONLY_POLICY_BOUNDARY_MATRIX_ROLLUP_CERTIFICATION
      next: 57C_HANDOFF_BUNDLE_REFRESH

✅ 57C_HANDOFF_BUNDLE_REFRESH
      next: 58A_QWEN_READ_ONLY_FINAL_CONTEXT_PACKAGE_STUB

✅ 58A_QWEN_READ_ONLY_FINAL_CONTEXT_PACKAGE_STUB

✅ 58B_QWEN_READ_ONLY_FINAL_CONTEXT_PACKAGE_ROLLUP_CERTIFICATION
      next: 58C_HANDOFF_BUNDLE_REFRESH

✅ 58C_HANDOFF_BUNDLE_REFRESH
      next: 59A_QWEN_READ_ONLY_FINAL_HANDOFF_CERTIFICATION_STUB

✅ 59A_QWEN_READ_ONLY_FINAL_HANDOFF_CERTIFICATION_STUB

✅ 59B_QWEN_READ_ONLY_FINAL_HANDOFF_CERTIFICATION_ROLLUP_CERTIFICATION
      next: 59C_HANDOFF_BUNDLE_REFRESH

✅ 59C_HANDOFF_BUNDLE_REFRESH
      next: 60A_QWEN_READ_ONLY_TERMINAL_FREEZE_STUB

✅ 60A_QWEN_READ_ONLY_TERMINAL_FREEZE_STUB

✅ 60B_QWEN_READ_ONLY_TERMINAL_FREEZE_ROLLUP_CERTIFICATION
      next: 60C_HANDOFF_BUNDLE_REFRESH

✅ 60C_HANDOFF_BUNDLE_REFRESH
      next: HANDOFF_TO_NEW_CHAT_OR_ARCHIVE_ONLY

✅ 61A_ARCHIVE_OR_NEW_CHAT_HANDOFF_SUMMARY

• candidate_sandbox_result_example_latest

• candidate_20260706_144431_8a545b3c_mock_metrics

• candidate_20260706_144431_8a545b3c_mock_scorecard

• candidate_20260706_144431_8a545b3c_sandbox_result_stub

• candidate_20260706_144431_8a545b3c_sandbox_stub

• candidate_20260706_145350_816903d1_mock_metrics

• candidate_20260706_145350_816903d1_mock_scorecard

• candidate_20260706_145350_816903d1_sandbox_result_stub

• candidate_20260706_145350_816903d1_sandbox_stub

• candidate_20260706_150540_4fc7b8ab_mock_metrics

• candidate_20260706_150540_4fc7b8ab_mock_scorecard

• candidate_20260706_150540_4fc7b8ab_sandbox_result_stub

• candidate_20260706_150540_4fc7b8ab_sandbox_stub

• candidate_20260706_151330_9f852272_mock_metrics

• candidate_20260706_151330_9f852272_mock_scorecard

• candidate_20260706_151330_9f852272_sandbox_result_stub

• candidate_20260706_151330_9f852272_sandbox_stub

• candidate_20260706_152354_e2129e4e_mock_metrics

• candidate_20260706_152354_e2129e4e_mock_scorecard

• candidate_20260706_152354_e2129e4e_sandbox_result_stub

• candidate_20260706_152354_e2129e4e_sandbox_stub

• candidate_20260706_152930_73031c40_mock_metrics

• candidate_20260706_152930_73031c40_mock_scorecard

• candidate_20260706_152930_73031c40_sandbox_result_stub

• candidate_20260706_152930_73031c40_sandbox_stub
```

---

# 31. [Certification History] Phase Timeline

Source: `handoff/project_bible/architecture_atlas/PHASE_TIMELINE.md`

## Foundation / Provider / Candidate Prep

• **candidate_sandbox_result_schema_v1**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_sandbox_result_schema_v1.json`

✅ **3M_GRAPH_CERTIFICATION**
   - evidence: `runtime/certifications/phase3m_graph_certification_latest.json`

✅ **4G_REPO_MEMORY_CERTIFICATION**
   - evidence: `runtime/certifications/phase4g_repo_memory_certification_latest.json`

✅ **5C_REPO_MEMORY_CERTIFICATION_V2**
   - evidence: `runtime/certifications/phase5c_repo_memory_certification_v2_latest.json`

✅ **6B_DEPENDENCY_VALIDATION_CERTIFICATION**
   - evidence: `runtime/certifications/phase6b_dependency_validation_certification_latest.json`

✅ **6D_DEPENDENCY_GRAPH_CERTIFICATION**
   - evidence: `runtime/certifications/phase6d_dependency_graph_certification_latest.json`

✅ **7G_GRAPH_VISUALIZATION_CERTIFICATION**
   - evidence: `runtime/certifications/phase7g_graph_visualization_certification_latest.json`

✅ **8C_NEURO_CLI_HOTSPOTS_CERTIFICATION**
   - evidence: `runtime/certifications/phase8c_neuro_cli_hotspots_certification_latest.json`

⚠️ **9E_CANONICAL_GRAPH_CERTIFICATION**
   - evidence: `runtime/certifications/phase9e_canonical_graph_certification_latest.json`

✅ **9M_CANONICAL_GRAPH_CERTIFICATION_V2**
   - evidence: `runtime/certifications/phase9m_canonical_graph_certification_v2_latest.json`

✅ **10C_RUNTIME_FLOW_OVERLAY_CERTIFICATION**
   - evidence: `runtime/certifications/phase10c_runtime_flow_overlay_certification_latest.json`

✅ **10D_RUNTIME_STATIC_DEPENDENCY_DIFF_CERTIFICATION**
   - evidence: `runtime/certifications/phase10d_runtime_static_dependency_diff_certification_latest.json`

✅ **10E_DIFF_CLASSIFICATION_CERTIFICATION**
   - evidence: `runtime/certifications/phase10e_diff_classification_certification_latest.json`

✅ **10F_ARCHITECTURE_DRIFT_WATCH_CERTIFICATION**
   - evidence: `runtime/certifications/phase10f_architecture_drift_watch_certification_latest.json`

✅ **10G_ARCHITECTURE_DRIFT_DASHBOARD_CERTIFICATION**
   - evidence: `runtime/certifications/phase10g_architecture_drift_dashboard_certification_latest.json`

✅ **10H_ARCHITECTURE_DASHBOARD_COMMAND_CERTIFICATION**
   - evidence: `runtime/certifications/phase10h_architecture_dashboard_command_certification_latest.json`

✅ **10_DOMAIN_SUBSYSTEM_VISUALIZATION_CERTIFICATION**
   - evidence: `runtime/certifications/phase10_domain_subsystem_visualization_certification_latest.json`

⚠️ **11B_FRONTEND_LIVE_PRICE_CARD_CERTIFICATION**
   - evidence: `runtime/certifications/phase11b_frontend_live_price_card_certification_latest.json`

⚠️ **11C_FRONTEND_POLLING_API_CLEANUP_CERTIFICATION**
   - evidence: `runtime/certifications/phase11c_frontend_polling_api_cleanup_certification_latest.json`

✅ **11D_NEXT_API_PROXY_LIVE_PRICE_CERTIFICATION**
   - evidence: `runtime/certifications/phase11d_next_api_proxy_live_price_certification_latest.json`

⚠️ **11E_FRONTEND_BUILD_TYPE_CERTIFICATION**
   - evidence: `runtime/certifications/phase11e_frontend_build_type_certification_latest.json`

✅ **11F_FRONTEND_TYPE_LINT_REPAIR_CERTIFICATION**
   - evidence: `runtime/certifications/phase11f_frontend_type_lint_repair_certification_latest.json`

✅ **11G_LIVE_MARKET_DASHBOARD_EXPANSION_CERTIFICATION**
   - evidence: `runtime/certifications/phase11g_live_market_dashboard_expansion_certification_latest.json`

✅ **11_LIVE_MARKET_PRICE_API_BRIDGE_CERTIFICATION**
   - evidence: `runtime/certifications/phase11_live_market_price_api_bridge_certification_latest.json`

⚠️ **12F_SERVICE_CHAIN_CERTIFICATION**
   - evidence: `runtime/certifications/phase12f_service_chain_certification_latest.json`

✅ **12G_SERVICE_CHAIN_DASHBOARD_CERTIFICATION**
   - evidence: `runtime/certifications/phase12g_service_chain_dashboard_certification_latest.json`

⚠️ **13F_PORTFOLIO_POSITIONS_SERVICE_CHAIN_CERTIFICATION**
   - evidence: `runtime/certifications/phase13f_portfolio_positions_service_chain_certification_latest.json`

✅ **13G_PORTFOLIO_CHAIN_DASHBOARD_CERTIFICATION**
   - evidence: `runtime/certifications/phase13g_portfolio_chain_dashboard_certification_latest.json`

⚠️ **14F_STRATEGY_DECISION_SERVICE_CHAIN_CERTIFICATION**
   - evidence: `runtime/certifications/phase14f_strategy_decision_service_chain_certification_latest.json`

✅ **14G_STRATEGY_CHAIN_DASHBOARD_CERTIFICATION**
   - evidence: `runtime/certifications/phase14g_strategy_chain_dashboard_certification_latest.json`

⚠️ **15F_RISK_GATE_SERVICE_CHAIN_CERTIFICATION**
   - evidence: `runtime/certifications/phase15f_risk_gate_service_chain_certification_latest.json`

✅ **15G_RISK_CHAIN_DASHBOARD_CERTIFICATION**
   - evidence: `runtime/certifications/phase15g_risk_chain_dashboard_certification_latest.json`

⚠️ **16_API_ROUTE_SEPARATION_CERTIFICATION**
   - evidence: `runtime/certifications/phase16_api_route_separation_certification_latest.json`

✅ **17_DASHBOARD_ROUTE_MAP_CERTIFICATION**
   - evidence: `runtime/certifications/phase17_dashboard_route_map_certification_latest.json`

✅ **18_REAL_POSITIONS_PANEL_CERTIFICATION**
   - evidence: `runtime/certifications/phase18_real_positions_panel_certification_latest.json`

⚠️ **19C_ENDPOINT_ACTIVATION_CERTIFICATION**
   - evidence: `runtime/certifications/phase19c_endpoint_activation_certification_latest.json`

✅ **19_DASHBOARD_VISUAL_LAYOUT_CERTIFICATION**
   - evidence: `runtime/certifications/phase19_dashboard_visual_layout_certification_latest.json`

⚠️ **20F_FLOATING_CHAT_WIDGET_CERTIFICATION**
   - evidence: `runtime/certifications/phase20f_floating_chat_widget_certification_latest.json`

⚠️ **21AB_CHAT_CACHE_HISTORY_CERTIFICATION**
   - evidence: `runtime/certifications/phase21ab_chat_cache_history_certification_latest.json`

⚠️ **21CD_CHAT_UX_PERSISTENT_CACHE_CERTIFICATION**
   - evidence: `runtime/certifications/phase21cd_chat_ux_persistent_cache_certification_latest.json`

⚠️ **22B_LIVE_GRAPH_VISUALIZATION_CERTIFICATION**
   - evidence: `runtime/certifications/phase22b_live_graph_visualization_certification_latest.json`

⚠️ **22_LIVE_GRAPH_TAB_CERTIFICATION**
   - evidence: `runtime/certifications/phase22_live_graph_tab_certification_latest.json`

⚠️ **23A_FRONTEND_REQUEST_NORMALIZER_CERTIFICATION**
   - evidence: `runtime/certifications/phase23a_frontend_request_normalizer_certification_latest.json`

⚠️ **23B_POLLING_GOVERNOR_CERTIFICATION**
   - evidence: `runtime/certifications/phase23b_polling_governor_certification_latest.json`

⚠️ **24A_FRONTEND_OBSERVABILITY_DASHBOARD_CERTIFICATION**
   - evidence: `runtime/certifications/phase24a_frontend_observability_dashboard_certification_latest.json`

⚠️ **24B_PERSIST_OBSERVABILITY_BACKEND_HEALTH_CERTIFICATION**
   - evidence: `runtime/certifications/phase24b_persist_observability_backend_health_certification_latest.json`

⚠️ **24C_OBSERVABILITY_EVENT_TIMELINE_CERTIFICATION**
   - evidence: `runtime/certifications/phase24c_observability_event_timeline_certification_latest.json`

✅ **24D_OBSERVABILITY_LOCK_HANDOFF_SNAPSHOT**
   - next: `Phase 25A — Dashboard Tab Shell / Layout Navigation`
   - evidence: `runtime/certifications/phase24d_observability_lock_handoff_snapshot_latest.json`

✅ **25A_DASHBOARD_TAB_SHELL_LAYOUT_NAVIGATION_CERTIFICATION**
   - evidence: `runtime/certifications/phase25a_dashboard_tab_shell_layout_navigation_certification_latest.json`

✅ **25B_TAB_LAYOUT_POLISH_CHAT_PANEL_CERTIFICATION**
   - evidence: `runtime/certifications/phase25b_tab_layout_polish_chat_panel_certification_latest.json`

✅ **25C_SPLIT_DASHBOARD_PANELS_INTO_TAB_WORKSPACES_CERTIFICATION**
   - evidence: `runtime/certifications/phase25c_split_dashboard_panels_into_tab_workspaces_certification_latest.json`

✅ **26C_CHAT_SAFETY_PROMPT_LIVE_EXECUTION_GUARD_CERTIFICATION**
   - evidence: `runtime/certifications/phase26c_chat_safety_prompt_live_execution_guard_certification_latest.json`

⚠️ **26D_FRONTEND_CHAT_RESPONSE_NORMALIZER_CERTIFICATION**
   - evidence: `runtime/certifications/phase26d_frontend_chat_response_normalizer_certification_latest.json`

✅ **26E_CHAT_METADATA_CHIPS_TYPING_ENTER_CERTIFICATION**
   - evidence: `runtime/certifications/phase26e_chat_metadata_chips_typing_enter_certification_latest.json`

⚠️ **26F_CHAT_UI_STATE_CLEANUP_METADATA_RENDERING_CERTIFICATION**
   - evidence: `runtime/certifications/phase26f_chat_ui_state_cleanup_metadata_rendering_certification_latest.json`

⚠️ **27A_STRATEGY_PROPOSAL_CAPTURE_CERTIFICATION**
   - evidence: `runtime/certifications/phase27a_strategy_proposal_capture_certification_latest.json`

⚠️ **27B_STRATEGY_CANDIDATE_REVIEW_INDEX_CERTIFICATION**
   - evidence: `runtime/certifications/phase27b_strategy_candidate_review_index_certification_latest.json`

• **27C_CANDIDATE_SANDBOX_DRY_RUN_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/sandbox_dry_run_index_latest.json`

⚠️ **27C_CANDIDATE_SANDBOX_DRY_RUN_STUB_CERTIFICATION**
   - evidence: `runtime/certifications/phase27c_candidate_sandbox_dry_run_stub_certification_latest.json`

⚠️ **27D_CANDIDATE_SANDBOX_RESULT_SCHEMA_CERTIFICATION**
   - evidence: `runtime/certifications/phase27d_candidate_sandbox_result_schema_certification_latest.json`

• **27E_CANDIDATE_SANDBOX_RESULT_STUB_GENERATOR**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_sandbox_result_stub_index_latest.json`

⚠️ **27E_CANDIDATE_SANDBOX_RESULT_STUB_GENERATOR_CERTIFICATION**
   - evidence: `runtime/certifications/phase27e_candidate_sandbox_result_stub_generator_certification_latest.json`

✅ **27F_CANDIDATE_SANDBOX_READINESS_LOCK_SNAPSHOT**
   - next: `Phase 28A — Candidate Sandbox Simulation Harness Stub`
   - evidence: `runtime/certifications/phase27f_candidate_sandbox_readiness_lock_snapshot_latest.json`

• **28A_CANDIDATE_SANDBOX_SIMULATION_HARNESS_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/simulation_harness_stub_latest.json`

✅ **28A_CANDIDATE_SANDBOX_SIMULATION_HARNESS_STUB_CERTIFICATION**
   - evidence: `runtime/certifications/phase28a_candidate_sandbox_simulation_harness_stub_certification_latest.json`

• **28B_CANDIDATE_SANDBOX_MOCK_METRICS_GENERATOR**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_sandbox_mock_metrics_index_latest.json`

✅ **28B_CANDIDATE_SANDBOX_MOCK_METRICS_GENERATOR_CERTIFICATION**
   - evidence: `runtime/certifications/phase28b_candidate_sandbox_mock_metrics_generator_certification_latest.json`

• **28C_CANDIDATE_SANDBOX_MOCK_SCORECARD**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_sandbox_mock_scorecard_latest.json`

✅ **28C_CANDIDATE_SANDBOX_MOCK_SCORECARD_CERTIFICATION**
   - evidence: `runtime/certifications/phase28c_candidate_sandbox_mock_scorecard_certification_latest.json`

• **28D_CANDIDATE_SANDBOX_EXECUTION_CONTRACT**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_sandbox_execution_contract_v1.json`

✅ **28D_CANDIDATE_SANDBOX_EXECUTION_CONTRACT_CERTIFICATION**
   - evidence: `runtime/certifications/phase28d_candidate_sandbox_execution_contract_certification_latest.json`

• **29A_HISTORICAL_REPLAY_ENGINE_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/historical_replay_engine_stub_latest.json`

✅ **29A_HISTORICAL_REPLAY_ENGINE_STUB_CERTIFICATION**
   - evidence: `runtime/certifications/phase29a_historical_replay_engine_stub_certification_latest.json`

• **29B_HISTORICAL_REPLAY_INPUT_CONTRACT**
   - evidence: `runtime/strategy_candidate_sandbox/historical_replay_input_contract_v1.json`

✅ **29B_HISTORICAL_REPLAY_INPUT_CONTRACT_CERTIFICATION**
   - evidence: `runtime/certifications/phase29b_historical_replay_input_contract_certification_latest.json`

• **29C_HISTORICAL_REPLAY_VALIDATION_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/historical_replay_validation_stub_latest.json`

✅ **29C_HISTORICAL_REPLAY_VALIDATION_STUB_CERTIFICATION**
   - evidence: `runtime/certifications/phase29c_historical_replay_validation_stub_certification_latest.json`

✅ **29D_HISTORICAL_REPLAY_READINESS_SNAPSHOT**
   - next: `Phase 29E — Historical Replay Market Data Provider Contract`
   - evidence: `runtime/certifications/phase29d_historical_replay_readiness_snapshot_latest.json`

• **29E_HISTORICAL_REPLAY_MARKET_DATA_PROVIDER_CONTRACT**
   - evidence: `runtime/strategy_candidate_sandbox/historical_replay_market_data_provider_contract_v1.json`

✅ **29E_HISTORICAL_REPLAY_MARKET_DATA_PROVIDER_CONTRACT_CERTIFICATION**
   - evidence: `runtime/certifications/phase29e_historical_replay_market_data_provider_contract_certification_latest.json`

• **29F_HISTORICAL_REPLAY_PROVIDER_ADAPTER_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/historical_replay_provider_adapter_stub_latest.json`

✅ **29F_HISTORICAL_REPLAY_PROVIDER_ADAPTER_STUB_CERTIFICATION**
   - evidence: `runtime/certifications/phase29f_historical_replay_provider_adapter_stub_certification_latest.json`

✅ **29G_HISTORICAL_REPLAY_PROVIDER_READINESS_SNAPSHOT**
   - next: `Phase 30A — Historical Replay Market Data Provider Probe`
   - evidence: `runtime/certifications/phase29g_historical_replay_provider_readiness_snapshot_latest.json`

• **30A_YFINANCE_HISTORICAL_BARS_PROVIDER_PROBE**
   - evidence: `runtime/strategy_candidate_sandbox/yfinance_historical_bars_provider_probe_latest.json`

✅ **30A_YFINANCE_HISTORICAL_BARS_PROVIDER_PROBE_CERTIFICATION**
   - evidence: `runtime/certifications/phase30a_yfinance_historical_bars_provider_probe_certification_latest.json`

✅ **30B_YFINANCE_PROVIDER_SELECTION_SNAPSHOT**
   - next: `Phase 30C — Historical Bars Contract`
   - evidence: `runtime/certifications/phase30b_yfinance_provider_selection_snapshot_latest.json`

• **30C_HISTORICAL_BARS_CONTRACT**
   - evidence: `runtime/strategy_candidate_sandbox/historical_bars_contract_v1.json`

✅ **30C_HISTORICAL_BARS_CONTRACT_CERTIFICATION**
   - evidence: `runtime/certifications/phase30c_historical_bars_contract_certification_latest.json`

• **30D_YFINANCE_HISTORICAL_BARS_ADAPTER_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_stub_latest.json`

✅ **30D_YFINANCE_HISTORICAL_BARS_ADAPTER_STUB_CERTIFICATION**
   - evidence: `runtime/certifications/phase30d_yfinance_historical_bars_adapter_stub_certification_latest.json`

• **30E_YFINANCE_HISTORICAL_BARS_ADAPTER_SHAPE_VALIDATION**
   - evidence: `runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_shape_validation_latest.json`

✅ **30E_YFINANCE_HISTORICAL_BARS_ADAPTER_SHAPE_VALIDATION_CERTIFICATION**
   - evidence: `runtime/certifications/phase30e_yfinance_historical_bars_adapter_shape_validation_certification_latest.json`

• **30F_YFINANCE_HISTORICAL_BARS_ADAPTER_WIRE_PREVIEW**
   - evidence: `runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_wire_preview_latest.json`

✅ **30F_YFINANCE_HISTORICAL_BARS_ADAPTER_WIRE_PREVIEW_CERTIFICATION**
   - evidence: `runtime/certifications/phase30f_yfinance_historical_bars_adapter_wire_preview_certification_latest.json`

• **30G_YFINANCE_HISTORICAL_BARS_ADAPTER_WIRE**
   - evidence: `runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_wire_latest.json`

✅ **30G_YFINANCE_HISTORICAL_BARS_ADAPTER_WIRE_CERTIFICATION**
   - evidence: `runtime/certifications/phase30g_yfinance_historical_bars_adapter_wire_certification_latest.json`

## Historical Replay + Metrics

✅ **31A_HISTORICAL_BARS_FETCH_VALIDATION**
   - evidence: `runtime/strategy_candidate_sandbox/31A_historical_bars_fetch_validation_latest.json`

✅ **31B_HISTORICAL_BARS_MULTI_SYMBOL_VALIDATION**
   - evidence: `runtime/strategy_candidate_sandbox/31B_historical_bars_multi_symbol_validation_latest.json`

✅ **31C_HISTORICAL_REPLAY_EXECUTOR_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/31C_historical_replay_executor_stub_latest.json`

✅ **31D_HISTORICAL_REPLAY_BAR_ITERATOR**
   - evidence: `runtime/strategy_candidate_sandbox/31D_historical_replay_bar_iterator_latest.json`

✅ **31E_FIRST_SINGLE_CANDIDATE_REPLAY_DRY_RUN**
   - evidence: `runtime/strategy_candidate_sandbox/31E_first_single_candidate_replay_dry_run_latest.json`

✅ **31F_REPLAY_METRICS_CONTRACT**
   - evidence: `runtime/strategy_candidate_sandbox/31F_replay_metrics_contract_latest.json`

✅ **32A_REAL_METRICS_GENERATION**
   - evidence: `runtime/strategy_candidate_sandbox/32A_real_metrics_generation_latest.json`

✅ **32B_CANDIDATE_SCORECARD_FROM_REPLAY_METRICS**
   - evidence: `runtime/strategy_candidate_sandbox/32B_candidate_scorecard_from_replay_metrics_latest.json`

✅ **32C_MANUAL_PROMOTION_GATE_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/32C_manual_promotion_gate_stub_latest.json`

✅ **32D_PIPELINE_ROLLUP_CERTIFICATION**
   - evidence: `runtime/strategy_candidate_sandbox/32D_pipeline_rollup_certification_latest.json`

✅ **32E_HANDOFF_BUNDLE_REFRESH**
   - Early Training Infrastructure + Bar-Only Replay Metrics Pipeline Complete
   - next: `33A_TRADE_SIMULATION_CONTRACT_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/32E_handoff_bundle_refresh_latest.json`

## Trade Simulation Contracts + Entry/Exit Disabled

✅ **33A_TRADE_SIMULATION_CONTRACT_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/33A_trade_simulation_contract_stub_latest.json`

✅ **33B_TRADE_EVENT_VALIDATION_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/33B_trade_event_validation_stub_latest.json`

✅ **33C_TRADE_SIMULATION_DRY_RUN_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/33C_trade_simulation_dry_run_stub_latest.json`

✅ **33D_ENTRY_EXIT_SIGNAL_CONTRACT_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/33D_entry_exit_signal_contract_stub_latest.json`

✅ **33E_HOLD_SIGNAL_GENERATOR_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/33E_hold_signal_generator_stub_latest.json`

✅ **33F_ENTRY_EXIT_DECISION_ENGINE_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/33F_entry_exit_decision_engine_stub_latest.json`

✅ **33G_HOLD_DECISION_TO_HOLD_EVENT_BRIDGE**
   - evidence: `runtime/strategy_candidate_sandbox/33G_hold_decision_to_hold_event_bridge_latest.json`

✅ **33H_TRADE_SIMULATION_PIPELINE_ROLLUP_CERTIFICATION**
   - next: `33I_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/33H_trade_simulation_pipeline_rollup_certification_latest.json`

✅ **33I_HANDOFF_BUNDLE_REFRESH**
   - Early Training Infrastructure + Bar-Only Metrics + Hold-Only Trade Simulation Runway Complete
   - next: `34A_ENTRY_SIGNAL_RULE_CONTRACT_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/33I_handoff_bundle_refresh_latest.json`

✅ **34A_ENTRY_SIGNAL_RULE_CONTRACT_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/34A_entry_signal_rule_contract_stub_latest.json`

✅ **34B_ENTRY_SIGNAL_RULE_VALIDATION_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/34B_entry_signal_rule_validation_stub_latest.json`

✅ **34C_ENTRY_SIGNAL_GENERATOR_DISABLED_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/34C_entry_signal_generator_disabled_stub_latest.json`

✅ **34D_ENTRY_SIGNAL_PIPELINE_ROLLUP_CERTIFICATION**
   - next: `34E_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/34D_entry_signal_pipeline_rollup_certification_latest.json`

✅ **34E_HANDOFF_BUNDLE_REFRESH**
   - Early Training Infrastructure + Hold-Only Simulation Runway + Disabled Entry Signal Pipeline Complete
   - next: `35A_EXIT_SIGNAL_RULE_CONTRACT_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/34E_handoff_bundle_refresh_latest.json`

✅ **35A_EXIT_SIGNAL_RULE_CONTRACT_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/35A_exit_signal_rule_contract_stub_latest.json`

✅ **35B_EXIT_SIGNAL_RULE_VALIDATION_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/35B_exit_signal_rule_validation_stub_latest.json`

✅ **35C_EXIT_SIGNAL_GENERATOR_DISABLED_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/35C_exit_signal_generator_disabled_stub_latest.json`

✅ **35D_EXIT_SIGNAL_PIPELINE_ROLLUP_CERTIFICATION**
   - next: `35E_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/35D_exit_signal_pipeline_rollup_certification_latest.json`

✅ **35E_STRATEGY_SANDBOX_WIREGRAPH_CERTIFICATION**
   - Strategy sandbox wiregraph certified
   - evidence: `runtime/strategy_candidate_sandbox/35E_strategy_sandbox_wiregraph_latest.json`

✅ **35F_HANDOFF_BUNDLE_REFRESH**
   - Strategy Sandbox Wiregraph Complete With Entry/Exit Generation Disabled
   - next: `36A_STRATEGY_RULE_ENABLEMENT_GATE_CONTRACT_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/35F_handoff_bundle_refresh_latest.json`

## Sandbox Gates + Dependency Trace

✅ **36A_STRATEGY_RULE_ENABLEMENT_GATE_CONTRACT_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/36A_strategy_rule_enablement_gate_contract_stub_latest.json`

✅ **36B_ENABLEMENT_GATE_VALIDATION_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/36B_enablement_gate_validation_stub_latest.json`

✅ **36C_ENABLEMENT_GATE_PIPELINE_ROLLUP_CERTIFICATION**
   - next: `36D_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/36C_enablement_gate_pipeline_rollup_certification_latest.json`

✅ **36D_HANDOFF_BUNDLE_REFRESH**
   - Strategy Rule Enablement Gate Certified (Locked)
   - next: `37A_TRADE_SIMULATION_ENABLEMENT_GATE_CONTRACT_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/36D_handoff_bundle_refresh_latest.json`

✅ **37A_TRADE_SIMULATION_ENABLEMENT_GATE_CONTRACT_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/37A_trade_simulation_enablement_gate_contract_stub_latest.json`

✅ **37B_TRADE_SIMULATION_ENABLEMENT_GATE_VALIDATION_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/37B_trade_simulation_enablement_gate_validation_stub_latest.json`

✅ **37C_TRADE_SIMULATION_ENABLEMENT_GATE_PIPELINE_ROLLUP_CERTIFICATION**
   - next: `37D_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/37C_trade_simulation_enablement_gate_pipeline_rollup_certification_latest.json`

✅ **37D_HANDOFF_BUNDLE_REFRESH**
   - Trade Simulation Enablement Gate Certified Locked
   - next: `38A_RISK_GATE_CONTRACT_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/37D_handoff_bundle_refresh_latest.json`

✅ **38A_RISK_GATE_CONTRACT_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/38A_risk_gate_contract_stub_latest.json`

✅ **38B_RISK_GATE_VALIDATION_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/38B_risk_gate_validation_stub_latest.json`

✅ **38C_RISK_GATE_PIPELINE_ROLLUP_CERTIFICATION**
   - next: `38D_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/38C_risk_gate_pipeline_rollup_certification_latest.json`

✅ **38D_HANDOFF_BUNDLE_REFRESH**
   - Risk Gate Certified Locked
   - next: `39A_MASTER_SANDBOX_GATE_WIREGRAPH_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/38D_handoff_bundle_refresh_latest.json`

✅ **39A_MASTER_SANDBOX_GATE_WIREGRAPH_REFRESH**
   - Master sandbox gate dependency wiregraph refreshed
   - evidence: `runtime/strategy_candidate_sandbox/39A_master_sandbox_gate_wiregraph_latest.json`

✅ **39B_MASTER_SANDBOX_GATE_WIREGRAPH_ROLLUP_CERTIFICATION**
   - next: `39C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/39B_master_sandbox_gate_wiregraph_rollup_certification_latest.json`

✅ **39C_HANDOFF_BUNDLE_REFRESH**
   - Master Sandbox Gate Wiregraph Certified
   - next: `40A_SANDBOX_RUNTIME_DEPENDENCY_TRACE_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/39C_handoff_bundle_refresh_latest.json`

✅ **40A_SANDBOX_RUNTIME_DEPENDENCY_TRACE_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/40A_sandbox_runtime_dependency_trace_stub_latest.json`

✅ **40B_SANDBOX_RUNTIME_DEPENDENCY_TRACE_ROLLUP_CERTIFICATION**
   - next: `40C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/40B_sandbox_runtime_dependency_trace_rollup_certification_latest.json`

✅ **40C_HANDOFF_BUNDLE_REFRESH**
   - Sandbox Runtime Dependency Trace Certified Locked
   - next: `41A_SAFE_READ_ONLY_ARCHITECTURE_INSPECTOR_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/40C_handoff_bundle_refresh_latest.json`

## Qwen Read-Only Context + Response Validation

✅ **41A_SAFE_READ_ONLY_ARCHITECTURE_INSPECTOR_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/41A_safe_read_only_architecture_inspector_stub_latest.json`

✅ **41B_SAFE_READ_ONLY_ARCHITECTURE_INSPECTOR_ROLLUP_CERTIFICATION**
   - next: `41C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/41B_safe_read_only_architecture_inspector_rollup_certification_latest.json`

✅ **41C_HANDOFF_BUNDLE_REFRESH**
   - Read-Only Architecture Inspector Certified
   - next: `42A_QWEN_READ_ONLY_ARCHITECTURE_CONTEXT_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/41C_handoff_bundle_refresh_latest.json`

✅ **42A_QWEN_READ_ONLY_ARCHITECTURE_CONTEXT_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/42A_qwen_read_only_architecture_context_stub_latest.json`

✅ **42B_QWEN_READ_ONLY_ARCHITECTURE_CONTEXT_ROLLUP_CERTIFICATION**
   - next: `42C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/42B_qwen_read_only_architecture_context_rollup_certification_latest.json`

✅ **42C_HANDOFF_BUNDLE_REFRESH**
   - Qwen Read-Only Architecture Context Certified
   - next: `43A_QWEN_CONTEXT_RESPONSE_CONTRACT_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/42C_handoff_bundle_refresh_latest.json`

✅ **43A_QWEN_CONTEXT_RESPONSE_CONTRACT_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/43A_qwen_context_response_contract_stub_latest.json`

✅ **43B_QWEN_CONTEXT_RESPONSE_CONTRACT_ROLLUP_CERTIFICATION**
   - next: `43C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/43B_qwen_context_response_contract_rollup_certification_latest.json`

✅ **43C_HANDOFF_BUNDLE_REFRESH**
   - Qwen Read-Only Response Contract Certified
   - next: `44A_QWEN_READ_ONLY_RESPONSE_SAMPLE_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/43C_handoff_bundle_refresh_latest.json`

✅ **44A_QWEN_READ_ONLY_RESPONSE_SAMPLE_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/44A_qwen_read_only_response_sample_stub_latest.json`

✅ **44B_QWEN_READ_ONLY_RESPONSE_SAMPLE_ROLLUP_CERTIFICATION**
   - next: `44C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/44B_qwen_read_only_response_sample_rollup_certification_latest.json`

✅ **44C_HANDOFF_BUNDLE_REFRESH**
   - Qwen Read-Only Response Sample Certified
   - next: `45A_QWEN_READ_ONLY_ARCHITECTURE_SUMMARY_GATE_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/44C_handoff_bundle_refresh_latest.json`

✅ **45A_QWEN_READ_ONLY_ARCHITECTURE_SUMMARY_GATE_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/45A_qwen_read_only_architecture_summary_gate_stub_latest.json`

✅ **45B_QWEN_READ_ONLY_ARCHITECTURE_SUMMARY_GATE_ROLLUP_CERTIFICATION**
   - next: `45C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/45B_qwen_read_only_architecture_summary_gate_rollup_certification_latest.json`

✅ **45C_HANDOFF_BUNDLE_REFRESH**
   - Qwen Read-Only Architecture Summary Gate Certified
   - next: `46A_QWEN_READ_ONLY_MISSING_CONTEXT_DETECTOR_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/45C_handoff_bundle_refresh_latest.json`

✅ **46A_QWEN_READ_ONLY_MISSING_CONTEXT_DETECTOR_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/46A_qwen_read_only_missing_context_detector_stub_latest.json`

✅ **46B_QWEN_READ_ONLY_MISSING_CONTEXT_DETECTOR_ROLLUP_CERTIFICATION**
   - next: `46C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/46B_qwen_read_only_missing_context_detector_rollup_certification_latest.json`

✅ **46C_HANDOFF_BUNDLE_REFRESH**
   - Qwen Read-Only Missing Context Detector Certified
   - next: `47A_QWEN_READ_ONLY_RECOMMENDATION_FILTER_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/46C_handoff_bundle_refresh_latest.json`

✅ **47A_QWEN_READ_ONLY_RECOMMENDATION_FILTER_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/47A_qwen_read_only_recommendation_filter_stub_latest.json`

✅ **47B_QWEN_READ_ONLY_RECOMMENDATION_FILTER_ROLLUP_CERTIFICATION**
   - next: `47C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/47B_qwen_read_only_recommendation_filter_rollup_certification_latest.json`

✅ **47C_HANDOFF_BUNDLE_REFRESH**
   - Qwen Read-Only Recommendation Filter Certified
   - next: `48A_QWEN_READ_ONLY_RESPONSE_VALIDATOR_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/47C_handoff_bundle_refresh_latest.json`

✅ **48A_QWEN_READ_ONLY_RESPONSE_VALIDATOR_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/48A_qwen_read_only_response_validator_stub_latest.json`

✅ **48B_QWEN_READ_ONLY_RESPONSE_VALIDATOR_ROLLUP_CERTIFICATION**
   - next: `48C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/48B_qwen_read_only_response_validator_rollup_certification_latest.json`

✅ **48C_HANDOFF_BUNDLE_REFRESH**
   - Qwen Read-Only Response Validator Certified
   - next: `49A_QWEN_READ_ONLY_ARCHITECTURE_SESSION_CONTRACT_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/48C_handoff_bundle_refresh_latest.json`

## Qwen Session / Bridge / Loop / State Machine

✅ **49A_QWEN_READ_ONLY_ARCHITECTURE_SESSION_CONTRACT_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/49A_qwen_read_only_architecture_session_contract_stub_latest.json`

✅ **49B_QWEN_READ_ONLY_ARCHITECTURE_SESSION_CONTRACT_ROLLUP_CERTIFICATION**
   - next: `49C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/49B_qwen_read_only_architecture_session_contract_rollup_certification_latest.json`

✅ **49C_HANDOFF_BUNDLE_REFRESH**
   - Qwen Read-Only Architecture Session Contract Certified
   - next: `50A_QWEN_READ_ONLY_SESSION_RESPONSE_BRIDGE_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/49C_handoff_bundle_refresh_latest.json`

✅ **50A_QWEN_READ_ONLY_SESSION_RESPONSE_BRIDGE_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/50A_qwen_read_only_session_response_bridge_stub_latest.json`

✅ **50B_QWEN_READ_ONLY_SESSION_RESPONSE_BRIDGE_ROLLUP_CERTIFICATION**
   - next: `50C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/50B_qwen_read_only_session_response_bridge_rollup_certification_latest.json`

✅ **50C_HANDOFF_BUNDLE_REFRESH**
   - Qwen Read-Only Session Response Bridge Certified
   - next: `51A_QWEN_READ_ONLY_ARCHITECTURE_LOOP_BOUNDARY_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/50C_handoff_bundle_refresh_latest.json`

✅ **51A_QWEN_READ_ONLY_ARCHITECTURE_LOOP_BOUNDARY_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/51A_qwen_read_only_architecture_loop_boundary_stub_latest.json`

✅ **51B_QWEN_READ_ONLY_ARCHITECTURE_LOOP_BOUNDARY_ROLLUP_CERTIFICATION**
   - next: `51C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/51B_qwen_read_only_architecture_loop_boundary_rollup_certification_latest.json`

✅ **51C_HANDOFF_BUNDLE_REFRESH**
   - Qwen Read-Only Architecture Loop Boundary Certified
   - next: `52A_QWEN_READ_ONLY_FINAL_GUARDRAIL_SUMMARY_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/51C_handoff_bundle_refresh_latest.json`

✅ **52A_QWEN_READ_ONLY_FINAL_GUARDRAIL_SUMMARY_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/52A_qwen_read_only_final_guardrail_summary_stub_latest.json`

✅ **52B_QWEN_READ_ONLY_FINAL_GUARDRAIL_SUMMARY_ROLLUP_CERTIFICATION**
   - next: `52C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/52B_qwen_read_only_final_guardrail_summary_rollup_certification_latest.json`

✅ **52C_HANDOFF_BUNDLE_REFRESH**
   - Qwen Read-Only Final Guardrail Summary Certified
   - next: `53A_QWEN_READ_ONLY_HANDOFF_FREEZE_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/52C_handoff_bundle_refresh_latest.json`

✅ **53A_QWEN_READ_ONLY_HANDOFF_FREEZE_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/53A_qwen_read_only_handoff_freeze_stub_latest.json`

✅ **53B_QWEN_READ_ONLY_HANDOFF_FREEZE_ROLLUP_CERTIFICATION**
   - next: `53C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/53B_qwen_read_only_handoff_freeze_rollup_certification_latest.json`

✅ **53C_HANDOFF_BUNDLE_REFRESH**
   - Qwen Read-Only Handoff Freeze Certified
   - next: `54A_QWEN_READ_ONLY_HANDOFF_EXPORT_SUMMARY_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/53C_handoff_bundle_refresh_latest.json`

✅ **54A_QWEN_READ_ONLY_HANDOFF_EXPORT_SUMMARY_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/54A_qwen_read_only_handoff_export_summary_stub_latest.json`

✅ **54B_QWEN_READ_ONLY_HANDOFF_EXPORT_SUMMARY_ROLLUP_CERTIFICATION**
   - next: `54C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/54B_qwen_read_only_handoff_export_summary_rollup_certification_latest.json`

✅ **54C_HANDOFF_BUNDLE_REFRESH**
   - Qwen Read-Only Handoff Export Summary Certified
   - next: `55A_QWEN_READ_ONLY_ARCHITECTURE_STATE_MACHINE_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/54C_handoff_bundle_refresh_latest.json`

✅ **55A_QWEN_READ_ONLY_ARCHITECTURE_STATE_MACHINE_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/55A_qwen_read_only_architecture_state_machine_stub_latest.json`

✅ **55B_QWEN_READ_ONLY_ARCHITECTURE_STATE_MACHINE_ROLLUP_CERTIFICATION**
   - next: `55C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/55B_qwen_read_only_architecture_state_machine_rollup_certification_latest.json`

✅ **55C_HANDOFF_BUNDLE_REFRESH**
   - next: `56A_QWEN_READ_ONLY_ARCHITECTURE_POLICY_MAP_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/55C_handoff_bundle_refresh_latest.json`

## Qwen Policy Matrix + Context Package

✅ **56A_QWEN_READ_ONLY_ARCHITECTURE_POLICY_MAP_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/56A_qwen_read_only_architecture_policy_map_stub_latest.json`

✅ **56B_QWEN_READ_ONLY_ARCHITECTURE_POLICY_MAP_ROLLUP_CERTIFICATION**
   - next: `56C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/56B_qwen_read_only_architecture_policy_map_rollup_certification_latest.json`

✅ **56C_HANDOFF_BUNDLE_REFRESH**
   - next: `57A_QWEN_READ_ONLY_POLICY_BOUNDARY_MATRIX_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/56C_handoff_bundle_refresh_latest.json`

✅ **57A_QWEN_READ_ONLY_POLICY_BOUNDARY_MATRIX_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/57A_qwen_read_only_policy_boundary_matrix_stub_latest.json`

✅ **57B_QWEN_READ_ONLY_POLICY_BOUNDARY_MATRIX_ROLLUP_CERTIFICATION**
   - next: `57C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/57B_qwen_read_only_policy_boundary_matrix_rollup_certification_latest.json`

✅ **57C_HANDOFF_BUNDLE_REFRESH**
   - next: `58A_QWEN_READ_ONLY_FINAL_CONTEXT_PACKAGE_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/57C_handoff_bundle_refresh_latest.json`

✅ **58A_QWEN_READ_ONLY_FINAL_CONTEXT_PACKAGE_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/58A_qwen_read_only_final_context_package_stub_latest.json`

✅ **58B_QWEN_READ_ONLY_FINAL_CONTEXT_PACKAGE_ROLLUP_CERTIFICATION**
   - next: `58C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/58B_qwen_read_only_final_context_package_rollup_certification_latest.json`

✅ **58C_HANDOFF_BUNDLE_REFRESH**
   - next: `59A_QWEN_READ_ONLY_FINAL_HANDOFF_CERTIFICATION_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/58C_handoff_bundle_refresh_latest.json`

## Terminal Freeze + Archive

✅ **59A_QWEN_READ_ONLY_FINAL_HANDOFF_CERTIFICATION_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/59A_qwen_read_only_final_handoff_certification_stub_latest.json`

✅ **59B_QWEN_READ_ONLY_FINAL_HANDOFF_CERTIFICATION_ROLLUP_CERTIFICATION**
   - next: `59C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/59B_qwen_read_only_final_handoff_certification_rollup_certification_latest.json`

✅ **59C_HANDOFF_BUNDLE_REFRESH**
   - next: `60A_QWEN_READ_ONLY_TERMINAL_FREEZE_STUB`
   - evidence: `runtime/strategy_candidate_sandbox/59C_handoff_bundle_refresh_latest.json`

✅ **60A_QWEN_READ_ONLY_TERMINAL_FREEZE_STUB**
   - evidence: `runtime/strategy_candidate_sandbox/60A_qwen_read_only_terminal_freeze_stub_latest.json`

✅ **60B_QWEN_READ_ONLY_TERMINAL_FREEZE_ROLLUP_CERTIFICATION**
   - next: `60C_HANDOFF_BUNDLE_REFRESH`
   - evidence: `runtime/strategy_candidate_sandbox/60B_qwen_read_only_terminal_freeze_rollup_certification_latest.json`

✅ **60C_HANDOFF_BUNDLE_REFRESH**
   - next: `HANDOFF_TO_NEW_CHAT_OR_ARCHIVE_ONLY`
   - evidence: `runtime/strategy_candidate_sandbox/60C_handoff_bundle_refresh_latest.json`

✅ **61A_ARCHIVE_OR_NEW_CHAT_HANDOFF_SUMMARY**
   - evidence: `runtime/strategy_candidate_sandbox/61A_archive_or_new_chat_handoff_summary_latest.json`

## Other

• **candidate_sandbox_result_example_latest**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_sandbox_result_example_latest.json`

• **candidate_20260706_144431_8a545b3c_mock_metrics**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_144431_8a545b3c_mock_metrics.json`

• **candidate_20260706_144431_8a545b3c_mock_scorecard**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_144431_8a545b3c_mock_scorecard.json`

• **candidate_20260706_144431_8a545b3c_sandbox_result_stub**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_144431_8a545b3c_sandbox_result_stub.json`

• **candidate_20260706_144431_8a545b3c_sandbox_stub**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_144431_8a545b3c_sandbox_stub.json`

• **candidate_20260706_145350_816903d1_mock_metrics**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_145350_816903d1_mock_metrics.json`

• **candidate_20260706_145350_816903d1_mock_scorecard**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_145350_816903d1_mock_scorecard.json`

• **candidate_20260706_145350_816903d1_sandbox_result_stub**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_145350_816903d1_sandbox_result_stub.json`

• **candidate_20260706_145350_816903d1_sandbox_stub**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_145350_816903d1_sandbox_stub.json`

• **candidate_20260706_150540_4fc7b8ab_mock_metrics**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_150540_4fc7b8ab_mock_metrics.json`

• **candidate_20260706_150540_4fc7b8ab_mock_scorecard**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_150540_4fc7b8ab_mock_scorecard.json`

• **candidate_20260706_150540_4fc7b8ab_sandbox_result_stub**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_150540_4fc7b8ab_sandbox_result_stub.json`

• **candidate_20260706_150540_4fc7b8ab_sandbox_stub**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_150540_4fc7b8ab_sandbox_stub.json`

• **candidate_20260706_151330_9f852272_mock_metrics**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_151330_9f852272_mock_metrics.json`

• **candidate_20260706_151330_9f852272_mock_scorecard**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_151330_9f852272_mock_scorecard.json`

• **candidate_20260706_151330_9f852272_sandbox_result_stub**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_151330_9f852272_sandbox_result_stub.json`

• **candidate_20260706_151330_9f852272_sandbox_stub**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_151330_9f852272_sandbox_stub.json`

• **candidate_20260706_152354_e2129e4e_mock_metrics**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_152354_e2129e4e_mock_metrics.json`

• **candidate_20260706_152354_e2129e4e_mock_scorecard**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_152354_e2129e4e_mock_scorecard.json`

• **candidate_20260706_152354_e2129e4e_sandbox_result_stub**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_152354_e2129e4e_sandbox_result_stub.json`

• **candidate_20260706_152354_e2129e4e_sandbox_stub**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_152354_e2129e4e_sandbox_stub.json`

• **candidate_20260706_152930_73031c40_mock_metrics**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_152930_73031c40_mock_metrics.json`

• **candidate_20260706_152930_73031c40_mock_scorecard**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_152930_73031c40_mock_scorecard.json`

• **candidate_20260706_152930_73031c40_sandbox_result_stub**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_152930_73031c40_sandbox_result_stub.json`

• **candidate_20260706_152930_73031c40_sandbox_stub**
   - evidence: `runtime/strategy_candidate_sandbox/candidate_20260706_152930_73031c40_sandbox_stub.json`

---

# 32. [Certification History] Certified Phase Index

Source: `handoff/certified_phase_index.json`

```json
{
  "certified_count": 110,
  "uncertified_count": 43,
  "certified": [
    {
      "phase": "31A_HISTORICAL_BARS_FETCH_VALIDATION",
      "file": "runtime/strategy_candidate_sandbox/31A_historical_bars_fetch_validation_latest.json",
      "created_at": "2026-07-06T18:27:18.313960+00:00",
      "stage": null
    },
    {
      "phase": "31B_HISTORICAL_BARS_MULTI_SYMBOL_VALIDATION",
      "file": "runtime/strategy_candidate_sandbox/31B_historical_bars_multi_symbol_validation_latest.json",
      "created_at": "2026-07-06T18:29:12.806849+00:00",
      "stage": null
    },
    {
      "phase": "31C_HISTORICAL_REPLAY_EXECUTOR_STUB",
      "file": "runtime/strategy_candidate_sandbox/31C_historical_replay_executor_stub_latest.json",
      "created_at": "2026-07-06T18:31:45.782591+00:00",
      "stage": null
    },
    {
      "phase": "31D_HISTORICAL_REPLAY_BAR_ITERATOR",
      "file": "runtime/strategy_candidate_sandbox/31D_historical_replay_bar_iterator_latest.json",
      "created_at": "2026-07-06T18:33:34.383342+00:00",
      "stage": null
    },
    {
      "phase": "31E_FIRST_SINGLE_CANDIDATE_REPLAY_DRY_RUN",
      "file": "runtime/strategy_candidate_sandbox/31E_first_single_candidate_replay_dry_run_latest.json",
      "created_at": "2026-07-06T18:36:43.498621+00:00",
      "stage": null
    },
    {
      "phase": "31F_REPLAY_METRICS_CONTRACT",
      "file": "runtime/strategy_candidate_sandbox/31F_replay_metrics_contract_latest.json",
      "created_at": "2026-07-06T18:39:11.451527+00:00",
      "stage": null
    },
    {
      "phase": "32A_REAL_METRICS_GENERATION",
      "file": "runtime/strategy_candidate_sandbox/32A_real_metrics_generation_latest.json",
      "created_at": "2026-07-06T18:42:48.877837+00:00",
      "stage": null
    },
    {
      "phase": "32B_CANDIDATE_SCORECARD_FROM_REPLAY_METRICS",
      "file": "runtime/strategy_candidate_sandbox/32B_candidate_scorecard_from_replay_metrics_latest.json",
      "created_at": "2026-07-06T18:44:40.023029+00:00",
      "stage": null
    },
    {
      "phase": "32C_MANUAL_PROMOTION_GATE_STUB",
      "file": "runtime/strategy_candidate_sandbox/32C_manual_promotion_gate_stub_latest.json",
      "created_at": "2026-07-06T18:48:19.801298+00:00",
      "stage": null
    },
    {
      "phase": "32D_PIPELINE_ROLLUP_CERTIFICATION",
      "file": "runtime/strategy_candidate_sandbox/32D_pipeline_rollup_certification_latest.json",
      "created_at": "2026-07-06T18:52:21.164171+00:00",
      "stage": null
    },
    {
      "phase": "32E_HANDOFF_BUNDLE_REFRESH",
      "file": "runtime/strategy_candidate_sandbox/32E_handoff_bundle_refresh_latest.json",
      "created_at": "2026-07-06T18:55:14.892759+00:00",
      "stage": "Early Training Infrastructure + Bar-Only Replay Metrics Pipeline Complete"
    },
    {
      "phase": "33A_TRADE_SIMULATION_CONTRACT_STUB",
      "file": "runtime/strategy_candidate_sandbox/33A_trade_simulation_contract_stub_latest.json",
      "created_at": "2026-07-06T18:58:14.254891+00:00",
      "stage": null
    },
    {
      "phase": "33B_TRADE_EVENT_VALIDATION_STUB",
      "file": "runtime/strategy_candidate_sandbox/33B_trade_event_validation_stub_latest.json",
      "created_at": "2026-07-06T19:00:39.127702+00:00",
      "stage": null
    },
    {
      "phase": "33C_TRADE_SIMULATION_DRY_RUN_STUB",
      "file": "runtime/strategy_candidate_sandbox/33C_trade_simulation_dry_run_stub_latest.json",
      "created_at": "2026-07-06T19:05:27.675387+00:00",
      "stage": null
    },
    {
      "phase": "33D_ENTRY_EXIT_SIGNAL_CONTRACT_STUB",
      "file": "runtime/strategy_candidate_sandbox/33D_entry_exit_signal_contract_stub_latest.json",
      "created_at": "2026-07-06T19:10:35.941176+00:00",
      "stage": null
    },
    {
      "phase": "33E_HOLD_SIGNAL_GENERATOR_STUB",
      "file": "runtime/strategy_candidate_sandbox/33E_hold_signal_generator_stub_latest.json",
      "created_at": "2026-07-06T19:14:15.343710+00:00",
      "stage": null
    },
    {
      "phase": "33F_ENTRY_EXIT_DECISION_ENGINE_STUB",
      "file": "runtime/strategy_candidate_sandbox/33F_entry_exit_decision_engine_stub_latest.json",
      "created_at": "2026-07-06T19:16:19.905494+00:00",
      "stage": null
    },
    {
      "phase": "33G_HOLD_DECISION_TO_HOLD_EVENT_BRIDGE",
      "file": "runtime/strategy_candidate_sandbox/33G_hold_decision_to_hold_event_bridge_latest.json",
      "created_at": "2026-07-06T19:18:40.891521+00:00",
      "stage": null
    },
    {
      "phase": "33H_TRADE_SIMULATION_PIPELINE_ROLLUP_CERTIFICATION",
      "file": "runtime/strategy_candidate_sandbox/33H_trade_simulation_pipeline_rollup_certification_latest.json",
      "created_at": "2026-07-06T19:22:11.779631+00:00",
      "stage": null
    },
    {
      "phase": "33I_HANDOFF_BUNDLE_REFRESH",
      "file": "runtime/strategy_candidate_sandbox/33I_handoff_bundle_refresh_latest.json",
      "created_at": "2026-07-06T19:23:46.331915+00:00",
      "stage": "Early Training Infrastructure + Bar-Only Metrics + Hold-Only Trade Simulation Runway Complete"
    },
    {
      "phase": "34A_ENTRY_SIGNAL_RULE_CONTRACT_STUB",
      "file": "runtime/strategy_candidate_sandbox/34A_entry_signal_rule_contract_stub_latest.json",
      "created_at": "2026-07-06T19:25:48.885111+00:00",
      "stage": null
    },
    {
      "phase": "34B_ENTRY_SIGNAL_RULE_VALIDATION_STUB",
      "file": "runtime/strategy_candidate_sandbox/34B_entry_signal_rule_validation_stub_latest.json",
      "created_at": "2026-07-06T19:28:33.879043+00:00",
      "stage": null
    },
    {
      "phase": "34C_ENTRY_SIGNAL_GENERATOR_DISABLED_STUB",
      "file": "runtime/strategy_candidate_sandbox/34C_entry_signal_generator_disabled_stub_latest.json",
      "created_at": "2026-07-06T19:31:16.111474+00:00",
      "stage": null
    },
    {
      "phase": "34D_ENTRY_SIGNAL_PIPELINE_ROLLUP_CERTIFICATION",
      "file": "runtime/strategy_candidate_sandbox/34D_entry_signal_pipeline_rollup_certification_latest.json",
      "created_at": "2026-07-06T19:33:28.314160+00:00",
      "stage": null
    },
    {
      "phase": "34E_HANDOFF_BUNDLE_REFRESH",
      "file": "runtime/strategy_candidate_sandbox/34E_handoff_bundle_refresh_latest.json",
      "created_at": "2026-07-06T19:35:23.698145+00:00",
      "stage": "Early Training Infrastructure + Hold-Only Simulation Runway + Disabled Entry Signal Pipeline Complete"
    },
    {
      "phase": "35A_EXIT_SIGNAL_RULE_CONTRACT_STUB",
      "file": "runtime/strategy_candidate_sandbox/35A_exit_signal_rule_contract_stub_latest.json",
      "created_at": "2026-07-06T19:38:18.235263+00:00",
      "stage": null
    },
    {
      "phase": "35B_EXIT_SIGNAL_RULE_VALIDATION_STUB",
      "file": "runtime/strategy_candidate_sandbox/35B_exit_signal_rule_validation_stub_latest.json",
      "created_at": "2026-07-06T19:40:15.980262+00:00",
      "stage": null
    },
    {
      "phase": "35C_EXIT_SIGNAL_GENERATOR_DISABLED_STUB",
      "file": "runtime/strategy_candidate_sandbox/35C_exit_signal_generator_disabled_stub_latest.json",
      "created_at": "2026-07-06T19:44:23.581778+00:00",
      "stage": null
    },
    {
      "phase": "35D_EXIT_SIGNAL_PIPELINE_ROLLUP_CERTIFICATION",
      "file": "runtime/strategy_candidate_sandbox/35D_exit_signal_pipeline_rollup_certification_latest.json",
      "created_at": "2026-07-06T19:46:32.120342+00:00",
      "stage": null
    },
    {
      "phase": "35E_STRATEGY_SANDBOX_WIREGRAPH_CERTIFICATION",
      "file": "runtime/strategy_candidate_sandbox/35E_strategy_sandbox_wiregraph_latest.json",
      "created_at": "2026-07-06T19:49:34.817433+00:00",
      "stage": "Strategy sandbox wiregraph certified"
    },
    {
      "phase": "35F_HANDOFF_BUNDLE_REFRESH",
      "file": "runtime/strategy_candidate_sandbox/35F_handoff_bundle_refresh_latest.json",
      "created_at": "2026-07-06T19:52:35.833832+00:00",
      "stage": "Strategy Sandbox Wiregraph Complete With Entry/Exit Generation Disabled"
    },
    {
      "phase": "36A_STRATEGY_RULE_ENABLEMENT_GATE_CONTRACT_STUB",
      "file": "runtime/strategy_candidate_sandbox/36A_strategy_rule_enablement_gate_contract_stub_latest.json",
      "created_at": "2026-07-06T19:55:44.349096+00:00",
      "stage": null
    },
    {
      "phase": "36B_ENABLEMENT_GATE_VALIDATION_STUB",
      "file": "runtime/strategy_candidate_sandbox/36B_enablement_gate_validation_stub_latest.json",
      "created_at": "2026-07-06T19:58:26.676219+00:00",
      "stage": null
    },
    {
      "phase": "36C_ENABLEMENT_GATE_PIPELINE_ROLLUP_CERTIFICATION",
      "file": "runtime/strategy_candidate_sandbox/36C_enablement_gate_pipeline_rollup_certification_latest.json",
      "created_at": "2026-07-06T20:02:28.038402+00:00",
      "stage": null
    },
    {
      "phase": "36D_HANDOFF_BUNDLE_REFRESH",
      "file": "runtime/strategy_candidate_sandbox/36D_handoff_bundle_refresh_latest.json",
      "created_at": "2026-07-06T20:05:41.776956+00:00",
      "stage": "Strategy Rule Enablement Gate Certified (Locked)"
    },
    {
      "phase": "37A_TRADE_SIMULATION_ENABLEMENT_GATE_CONTRACT_STUB",
      "file": "runtime/strategy_candidate_sandbox/37A_trade_simulation_enablement_gate_contract_stub_latest.json",
      "created_at": "2026-07-06T20:09:04.083312+00:00",
      "stage": null
    },
    {
      "phase": "37B_TRADE_SIMULATION_ENABLEMENT_GATE_VALIDATION_STUB",
      "file": "runtime/strategy_candidate_sandbox/37B_trade_simulation_enablement_gate_validation_stub_latest.json",
      "created_at": "2026-07-06T20:13:09.604935+00:00",
      "stage": null
    },
    {
      "phase": "37C_TRADE_SIMULATION_ENABLEMENT_GATE_PIPELINE_ROLLUP_CERTIFICATION",
      "file": "runtime/strategy_candidate_sandbox/37C_trade_simulation_enablement_gate_pipeline_rollup_certification_latest.json",
      "created_at": "2026-07-06T20:15:35.524801+00:00",
      "stage": null
    },
    {
      "phase": "37D_HANDOFF_BUNDLE_REFRESH",
      "file": "runtime/strategy_candidate_sandbox/37D_handoff_bundle_refresh_latest.json",
      "created_at": "2026-07-06T20:18:33.855507+00:00",
      "stage": "Trade Simulation Enablement Gate Certified Locked"
    },
    {
      "phase": "38A_RISK_GATE_CONTRACT_STUB",
      "file": "runtime/strategy_candidate_sandbox/38A_risk_gate_contract_stub_latest.json",
      "created_at": "2026-07-06T20:21:43.120826+00:00",
      "stage": null
    },
    {
      "phase": "38B_RISK_GATE_VALIDATION_STUB",
      "file": "runtime/strategy_candidate_sandbox/38B_risk_gate_validation_stub_latest.json",
      "created_at": "2026-07-06T20:24:38.466894+00:00",
      "stage": null
    },
    {
      "phase": "38C_RISK_GATE_PIPELINE_ROLLUP_CERTIFICATION",
      "file": "runtime/strategy_candidate_sandbox/38C_risk_gate_pipeline_rollup_certification_latest.json",
      "created_at": "2026-07-06T20:26:58.877062+00:00",
      "stage": null
    },
    {
      "phase": "38D_HANDOFF_BUNDLE_REFRESH",
      "file": "runtime/strategy_candidate_sandbox/38D_handoff_bundle_refresh_latest.json",
      "created_at": "2026-07-06T20:29:52.325331+00:00",
      "stage": "Risk Gate Certified Locked"
    },
    {
      "phase": "39A_MASTER_SANDBOX_GATE_WIREGRAPH_REFRESH",
      "file": "runtime/strategy_candidate_sandbox/39A_master_sandbox_gate_wiregraph_latest.json",
      "created_at": "2026-07-06T20:32:40.063512+00:00",
      "stage": "Master sandbox gate dependency wiregraph refreshed"
    },
    {
      "phase": "39B_MASTER_SANDBOX_GATE_WIREGRAPH_ROLLUP_CERTIFICATION",
      "file": "runtime/strategy_candidate_sandbox/39B_master_sandbox_gate_wiregraph_rollup_certification_latest.json",
      "created_at": "2026-07-06T20:36:03.392382+00:00",
      "stage": null
    },
    {
      "phase": "39C_HANDOFF_BUNDLE_REFRESH",
      "file": "runtime/strategy_candidate_sandbox/39C_handoff_bundle_refresh_latest.json",
      "created_at": "2026-07-06T20:39:55.025662+00:00",
      "stage": "Master Sandbox Gate Wiregraph Certified"
    },
    {
      "phase": "40A_SANDBOX_RUNTIME_DEPENDENCY_TRACE_STUB",
      "file": "runtime/strategy_candidate_sandbox/40A_sandbox_runtime_dependency_trace_stub_latest.json",
      "created_at": "2026-07-06T20:43:08.180228+00:00",
      "stage": null
    },
    {
      "phase": "40B_SANDBOX_RUNTIME_DEPENDENCY_TRACE_ROLLUP_CERTIFICATION",
      "file": "runtime/strategy_candidate_sandbox/40B_sandbox_runtime_dependency_trace_rollup_certification_latest.json",
      "created_at": "2026-07-06T20:45:55.493430+00:00",
      "stage": null
    },
    {
      "phase": "40C_HANDOFF_BUNDLE_REFRESH",
      "file": "runtime/strategy_candidate_sandbox/40C_handoff_bundle_refresh_latest.json",
      "created_at": "2026-07-06T20:49:59.854484+00:00",
      "stage": "Sandbox Runtime Dependency Trace Certified Locked"
    },
    {
      "phase": "41A_SAFE_READ_ONLY_ARCHITECTURE_INSPECTOR_STUB",
      "file": "runtime/strategy_candidate_sandbox/41A_safe_read_only_architecture_inspector_stub_latest.json",
      "created_at": "2026-07-06T20:53:18.625197+00:00",
      "stage": null
    },
    {
      "phase": "41B_SAFE_READ_ONLY_ARCHITECTURE_INSPECTOR_ROLLUP_CERTIFICATION",
      "file": "runtime/strategy_candidate_sandbox/41B_safe_read_only_architecture_inspector_rollup_certification_latest.json",
      "created_at": "2026-07-06T20:55:52.196584+00:00",
      "stage": null
    },
    {
      "phase": "41C_HANDOFF_BUNDLE_REFRESH",
      "file": "runtime/strategy_candidate_sandbox/41C_handoff_bundle_refresh_latest.json",
      "created_at": "2026-07-06T20:58:02.331309+00:00",
      "stage": "Read-Only Architecture Inspector Certified"
    },
    {
      "phase": "42A_QWEN_READ_ONLY_ARCHITECTURE_CONTEXT_STUB",
      "file": "runtime/strategy_candidate_sandbox/42A_qwen_read_only_architecture_context_stub_latest.json",
      "created_at": "2026-07-06T21:01:15.596924+00:00",
      "stage": null
    },
    {
      "phase": "42B_QWEN_READ_ONLY_ARCHITECTURE_CONTEXT_ROLLUP_CERTIFICATION",
      "file": "runtime/strategy_candidate_sandbox/42B_qwen_read_only_architecture_context_rollup_certification_latest.json",
      "created_at": "2026-07-06T21:04:22.718605+00:00",
      "stage": null
    },
    {
      "phase": "42C_HANDOFF_BUNDLE_REFRESH",
      "file": "runtime/strategy_candidate_sandbox/42C_handoff_bundle_refresh_latest.json",
      "created_at": "2026-07-06T21:06:37.047217+00:00",
      "stage": "Qwen Read-Only Architecture Context Certified"
    },
    {
      "phase": "43A_QWEN_CONTEXT_RESPONSE_CONTRACT_STUB",
      "file": "runtime/strategy_candidate_sandbox/43A_qwen_context_response_contract_stub_latest.json",
      "created_at": "2026-07-06T21:09:10.049664+00:00",
      "stage": null
    },
    {
      "phase": "43B_QWEN_CONTEXT_RESPONSE_CONTRACT_ROLLUP_CERTIFICATION",
      "file": "runtime/strategy_candidate_sandbox/43B_qwen_context_response_contract_rollup_certification_latest.json",
      "created_at": "2026-07-06T21:11:50.634224+00:00",
      "stage": null
    },
    {
      "phase": "43C_HANDOFF_BUNDLE_REFRESH",
      "file": "runtime/strategy_candidate_sandbox/43C_handoff_bundle_refresh_latest.json",
      "created_at": "2026-07-06T21:14:24.786420+00:00",
      "stage": "Qwen Read-Only Response Contract Certified"
    },
    {
      "phase": "44A_QWEN_READ_ONLY_RESPONSE_SAMPLE_STUB",
      "file": "runtime/strategy_candidate_sandbox/44A_qwen_read_only_response_sample_stub_latest.json",
      "created_at": "2026-07-06T21:16:24.820093+00:00",
      "stage": null
    },
    {
      "phase": "44B_QWEN_READ_ONLY_RESPONSE_SAMPLE_ROLLUP_CERTIFICATION",
      "file": "runtime/strategy_candidate_sandbox/44B_qwen_read_only_response_sample_rollup_certification_latest.json",
      "created_at": "2026-07-06T21:18:57.388283+00:00",
      "stage": null
    },
    {
      "phase": "44C_HANDOFF_BUNDLE_REFRESH",
      "file": "runtime/strategy_candidate_sandbox/44C_handoff_bundle_refresh_latest.json",
      "created_at": "2026-07-06T21:21:01.853669+00:00",
      "stage": "Qwen Read-Only Response Sample Certified"
    },
    {
      "phase": "45A_QWEN_READ_ONLY_ARCHITECTURE_SUMMARY_GATE_STUB",
      "file": "runtime/strategy_candidate_sandbox/45A_qwen_read_only_architecture_summary_gate_stub_latest.json",
      "created_at": "2026-07-06T21:25:42.745106+00:00",
      "stage": null
    },
    {
      "phase": "45B_QWEN_READ_ONLY_ARCHITECTURE_SUMMARY_GATE_ROLLUP_CERTIFICATION",
      "file": "runtime/strategy_candidate_sandbox/45B_qwen_read_only_architecture_summary_gate_rollup_certification_latest.json",
      "created_at": "2026-07-06T21:28:53.810764+00:00",
      "stage": null
    },
    {
      "phase": "45C_HANDOFF_BUNDLE_REFRESH",
      "file": "runtime/strategy_candidate_sandbox/45C_handoff_bundle_refresh_latest.json",
      "created_at": "2026-07-06T21:32:00.091252+00:00",
      "stage": "Qwen Read-Only Architecture Summary Gate Certified"
    },
    {
      "phase": "46A_QWEN_READ_ONLY_MISSING_CONTEXT_DETECTOR_STUB",
      "file": "runtime/strategy_candidate_sandbox/46A_qwen_read_only_missing_context_detector_stub_latest.json",
      "created_at": "2026-07-06T21:35:24.814949+00:00",
      "stage": null
    },
    {
      "phase": "46B_QWEN_READ_ONLY_MISSING_CONTEXT_DETECTOR_ROLLUP_CERTIFICATION",
      "file": "runtime/strategy_candidate_sandbox/46B_qwen_read_only_missing_context_detector_rollup_certification_latest.json",
      "created_at": "2026-07-06T21:39:48.423408+00:00",
      "stage": null
    },
    {
      "phase": "46C_HANDOFF_BUNDLE_REFRESH",
      "file": "runtime/strategy_candidate_sandbox/46C_handoff_bundle_refresh_latest.json",
      "created_at": "2026-07-06T21:41:11.257800+00:00",
      "stage": "Qwen Read-Only Missing Context Detector Certified"
    },
    {
      "phase": "47A_QWEN_READ_ONLY_RECOMMENDATION_FILTER_STUB",
      "file": "runtime/strategy_candidate_sandbox/47A_qwen_read_only_recommendation_filter_stub_latest.json",
      "created_at": "2026-07-06T21:45:08.946023+00:00",
      "stage": null
    },
    {
      "phase": "47B_QWEN_READ_ONLY_RECOMMENDATION_FILTER_ROLLUP_CERTIFICATION",
      "file": "runtime/strategy_candidate_sandbox/47B_qwen_read_only_recommendation_filter_rollup_certification_latest.json",
      "created_at": "2026-07-06T22:08:54.397858+00:00",
      "stage": null
    },
    {
      "phase": "47C_HANDOFF_BUNDLE_REFRESH",
      "file": "runtime/strategy_candidate_sandbox/47C_handoff_bundle_refresh_latest.json",
      "created_at": "2026-07-06T22:09:39.927679+00:00",
      "stage": "Qwen Read-Only Recommendation Filter Certified"
    },
    {
      "phase": "48A_QWEN_READ_ONLY_RESPONSE_VALIDATOR_STUB",
      "file": "runtime/strategy_candidate_sandbox/48A_qwen_read_only_response_validator_stub_latest.json",
      "created_at": "2026-07-06T22:11:13.119522+00:00",
      "stage": null
    },
    {
      "phase": "48B_QWEN_READ_ONLY_RESPONSE_VALIDATOR_ROLLUP_CERTIFICATION",
      "file": "runtime/strategy_candidate_sandbox/48B_qwen_read_only_response_validator_rollup_certification_latest.json",
      "created_at": "2026-07-06T22:12:03.143651+00:00",
      "stage": null
    },
    {
      "phase": "48C_HANDOFF_BUNDLE_REFRESH",
      "file": "runtime/strategy_candidate_sandbox/48C_handoff_bundle_refresh_latest.json",
      "created_at": "2026-07-06T22:15:16.297721+00:00",
      "stage": "Qwen Read-Only Response Validator Certified"
    },
    {
      "phase": "49A_QWEN_READ_ONLY_ARCHITECTURE_SESSION_CONTRACT_STUB",
      "file": "runtime/strategy_candidate_sandbox/49A_qwen_read_only_architecture_session_contract_stub_latest.json",
      "created_at": "2026-07-06T22:17:35.202350+00:00",
      "stage": null
    },
    {
      "phase": "49B_QWEN_READ_ONLY_ARCHITECTURE_SESSION_CONTRACT_ROLLUP_CERTIFICATION",
      "file": "runtime/strategy_candidate_sandbox/49B_qwen_read_only_architecture_session_contract_rollup_certification_latest.json",
      "created_at": "2026-07-06T22:26:01.510612+00:00",
      "stage": null
    },
    {
      "phase": "49C_HANDOFF_BUNDLE_REFRESH",
      "file": "runtime/strategy_candidate_sandbox/49C_handoff_bundle_refresh_latest.json",
      "created_at": "2026-07-06T22:30:16.874890+00:00",
      "stage": "Qwen Read-Only Architecture Session Contract Certified"
    },
    {
      "phase": "50A_QWEN_READ_ONLY_SESSION_RESPONSE_BRIDGE_STUB",
      "file": "runtime/strategy_candidate_sandbox/50A_qwen_read_only_session_response_bridge_stub_latest.json",
      "created_at": "2026-07-06T22:34:49.531887+00:00",
      "stage": null
    },
    {
      "phase": "50B_QWEN_READ_ONLY_SESSION_RESPONSE_BRIDGE_ROLLUP_CERTIFICATION",
      "file": "runtime/strategy_candidate_sandbox/50B_qwen_read_only_session_response_bridge_rollup_certification_latest.json",
      "created_at": "2026-07-06T22:37:09.980723+00:00",
      "stage": null
    },
    {
      "phase": "50C_HANDOFF_BUNDLE_REFRESH",
      "file": "runtime/strategy_candidate_sandbox/50C_handoff_bundle_refresh_latest.json",
      "created_at": "2026-07-06T22:41:15.678267+00:00",
      "stage": "Qwen Read-Only Session Response Bridge Certified"
    },
    {
      "phase": "51A_QWEN_READ_ONLY_ARCHITECTURE_LOOP_BOUNDARY_STUB",
      "file": "runtime/strategy_candidate_sandbox/51A_qwen_read_only_architecture_loop_boundary_stub_latest.json",
      "created_at": "2026-07-06T22:42:43.254863+00:00",
      "stage": null
    },
    {
      "phase": "51B_QWEN_READ_ONLY_ARCHITECTURE_LOOP_BOUNDARY_ROLLUP_CERTIFICATION",
      "file": "runtime/strategy_candidate_sandbox/51B_qwen_read_only_architecture_loop_boundary_rollup_certification_latest.json",
      "created_at": "2026-07-06T22:46:55.131648+00:00",
      "stage": null
    },
    {
      "phase": "51C_HANDOFF_BUNDLE_REFRESH",
      "file": "runtime/strategy_candidate_sandbox/51C_handoff_bundle_refresh_latest.json",
      "created_at": "2026-07-06T22:49:22.644704+00:00",
      "stage": "Qwen Read-Only Architecture Loop Boundary Certified"
    },
    {
      "phase": "52A_QWEN_READ_ONLY_FINAL_GUARDRAIL_SUMMARY_STUB",
      "file": "runtime/strategy_candidate_sandbox/52A_qwen_read_only_final_guardrail_summary_stub_latest.json",
      "created_at": "2026-07-06T22:51:04.815870+00:00",
      "stage": null
    },
    {
      "phase": "52B_QWEN_READ_ONLY_FINAL_GUARDRAIL_SUMMARY_ROLLUP_CERTIFICATION",
      "file": "runtime/strategy_candidate_sandbox/52B_qwen_read_only_final_guardrail_summary_rollup_certification_latest.json",
      "created_at": "2026-07-06T22:56:56.839945+00:00",
      "stage": null
    },
    {
      "phase": "52C_HANDOFF_BUNDLE_REFRESH",
      "file": "runtime/strategy_candidate_sandbox/52C_handoff_bundle_refresh_latest.json",
      "created_at": "2026-07-06T23:03:11.921540+00:00",
      "stage": "Qwen Read-Only Final Guardrail Summary Certified"
    },
    {
      "phase": "53A_QWEN_READ_ONLY_HANDOFF_FREEZE_STUB",
      "file": "runtime/strategy_candidate_sandbox/53A_qwen_read_only_handoff_freeze_stub_latest.json",
      "created_at": "2026-07-06T23:05:03.653209+00:00",
      "stage": null
    },
    {
      "phase": "53B_QWEN_READ_ONLY_HANDOFF_FREEZE_ROLLUP_CERTIFICATION",
      "file": "runtime/strategy_candidate_sandbox/53B_qwen_read_only_handoff_freeze_rollup_certification_latest.json",
      "created_at": "2026-07-06T23:10:36.551204+00:00",
      "stage": null
    },
    {
      "phase": "53C_HANDOFF_BUNDLE_REFRESH",
      "file": "runtime/strategy_candidate_sandbox/53C_handoff_bundle_refresh_latest.json",
      "created_at": "2026-07-06T23:17:09.795509+00:00",
      "stage": "Qwen Read-Only Handoff Freeze Certified"
    },
    {
      "phase": "54A_QWEN_READ_ONLY_HANDOFF_EXPORT_SUMMARY_STUB",
      "file": "runtime/strategy_candidate_sandbox/54A_qwen_read_only_handoff_export_summary_stub_latest.json",
      "created_at": "2026-07-06T23:21:24.764687+00:00",
      "stage": null
    },
    {
      "phase": "54B_QWEN_READ_ONLY_HANDOFF_EXPORT_SUMMARY_ROLLUP_CERTIFICATION",
      "file": "runtime/strategy_candidate_sandbox/54B_qwen_read_only_handoff_export_summary_rollup_certification_latest.json",
      "created_at": "2026-07-06T23:23:18.350479+00:00",
      "stage": null
    },
    {
      "phase": "54C_HANDOFF_BUNDLE_REFRESH",
      "file": "runtime/strategy_candidate_sandbox/54C_handoff_bundle_refresh_latest.json",
      "created_at": "2026-07-06T23:25:39.367487+00:00",
      "stage": "Qwen Read-Only Handoff Export Summary Certified"
    },
    {
      "phase": "55A_QWEN_READ_ONLY_ARCHITECTURE_STATE_MACHINE_STUB",
      "file": "runtime/strategy_candidate_sandbox/55A_qwen_read_only_architecture_state_machine_stub_latest.json",
      "created_at": "2026-07-06T23:36:15.293068+00:00",
      "stage": null
    },
    {
      "phase": "55B_QWEN_READ_ONLY_ARCHITECTURE_STATE_MACHINE_ROLLUP_CERTIFICATION",
      "file": "runtime/strategy_candidate_sandbox/55B_qwen_read_only_architecture_state_machine_rollup_certification_latest.json",
      "created_at": "2026-07-06T23:39:58.207331+00:00",
      "stage": null
    },
    {
      "phase": "55C_HANDOFF_BUNDLE_REFRESH",
      "file": "runtime/strategy_candidate_sandbox/55C_handoff_bundle_refresh_latest.json",
      "created_at": "2026-07-06T23:41:34.607822+00:00",
      "stage": null
    },
    {
      "phase": "56A_QWEN_READ_ONLY_ARCHITECTURE_POLICY_MAP_STUB",
      "file": "runtime/strategy_candidate_sandbox/56A_qwen_read_only_architecture_policy_map_stub_latest.json",
      "created_at": "2026-07-06T23:41:43.113136+00:00",
      "stage": null
    },
    {
      "phase": "56B_QWEN_READ_ONLY_ARCHITECTURE_POLICY_MAP_ROLLUP_CERTIFICATION",
      "file": "runtime/strategy_candidate_sandbox/56B_qwen_read_only_architecture_policy_map_rollup_certification_latest.json",
      "created_at": "2026-07-06T23:45:11.202145+00:00",
      "stage": null
    },
    {
      "phase": "56C_HANDOFF_BUNDLE_REFRESH",
      "file": "runtime/strategy_candidate_sandbox/56C_handoff_bundle_refresh_latest.json",
      "created_at": "2026-07-06T23:52:07.357357+00:00",
      "stage": null
    },
    {
      "phase": "57A_QWEN_READ_ONLY_POLICY_BOUNDARY_MATRIX_STUB",
      "file": "runtime/strategy_candidate_sandbox/57A_qwen_read_only_policy_boundary_matrix_stub_latest.json",
      "created_at": "2026-07-07T00:00:27.714517+00:00",
      "stage": null
    },
    {
      "phase": "57B_QWEN_READ_ONLY_POLICY_BOUNDARY_MATRIX_ROLLUP_CERTIFICATION",
      "file": "runtime/strategy_candidate_sandbox/57B_qwen_read_only_policy_boundary_matrix_rollup_certification_latest.json",
      "created_at": "2026-07-07T00:05:39.836859+00:00",
      "stage": null
    },
    {
      "phase": "57C_HANDOFF_BUNDLE_REFRESH",
      "file": "runtime/strategy_candidate_sandbox/57C_handoff_bundle_refresh_latest.json",
      "created_at": "2026-07-07T01:34:57.636813+00:00",
      "stage": null
    },
    {
      "phase": "58A_QWEN_READ_ONLY_FINAL_CONTEXT_PACKAGE_STUB",
      "file": "runtime/strategy_candidate_sandbox/58A_qwen_read_only_final_context_package_stub_latest.json",
      "created_at": "2026-07-07T01:42:00.600060+00:00",
      "stage": null
    },
    {
      "phase": "58B_QWEN_READ_ONLY_FINAL_CONTEXT_PACKAGE_ROLLUP_CERTIFICATION",
      "file": "runtime/strategy_candidate_sandbox/58B_qwen_read_only_final_context_package_rollup_certification_latest.json",
      "created_at": "2026-07-07T01:50:46.052707+00:00",
      "stage": null
    },
    {
      "phase": "58C_HANDOFF_BUNDLE_REFRESH",
      "file": "runtime/strategy_candidate_sandbox/58C_handoff_bundle_refresh_latest.json",
      "created_at": "2026-07-07T01:55:54.520435+00:00",
      "stage": null
    },
    {
      "phase": "59A_QWEN_READ_ONLY_FINAL_HANDOFF_CERTIFICATION_STUB",
      "file": "runtime/strategy_candidate_sandbox/59A_qwen_read_only_final_handoff_certification_stub_latest.json",
      "created_at": "2026-07-07T01:57:58.019119+00:00",
      "stage": null
    },
    {
      "phase": "59B_QWEN_READ_ONLY_FINAL_HANDOFF_CERTIFICATION_ROLLUP_CERTIFICATION",
      "file": "runtime/strategy_candidate_sandbox/59B_qwen_read_only_final_handoff_certification_rollup_certification_latest.json",
      "created_at": "2026-07-07T02:03:49.659517+00:00",
      "stage": null
    },
    {
      "phase": "59C_HANDOFF_BUNDLE_REFRESH",
      "file": "runtime/strategy_candidate_sandbox/59C_handoff_bundle_refresh_latest.json",
      "created_at": "2026-07-07T02:07:59.342307+00:00",
      "stage": null
    },
    {
      "phase": "60A_QWEN_READ_ONLY_TERMINAL_FREEZE_STUB",
      "file": "runtime/strategy_candidate_sandbox/60A_qwen_read_only_terminal_freeze_stub_latest.json",
      "created_at": "2026-07-07T02:17:06.874264+00:00",
      "stage": null
    },
    {
      "phase": "60B_QWEN_READ_ONLY_TERMINAL_FREEZE_ROLLUP_CERTIFICATION",
      "file": "runtime/strategy_candidate_sandbox/60B_qwen_read_only_terminal_freeze_rollup_certification_latest.json",
      "created_at": "2026-07-07T02:21:23.020937+00:00",
      "stage": null
    },
    {
      "phase": "60C_HANDOFF_BUNDLE_REFRESH",
      "file": "runtime/strategy_candidate_sandbox/60C_handoff_bundle_refresh_latest.json",
      "created_at": "2026-07-07T02:26:36.247863+00:00",
      "stage": null
    },
    {
      "phase": "61A_ARCHIVE_OR_NEW_CHAT_HANDOFF_SUMMARY",
      "file": "runtime/strategy_candidate_sandbox/61A_archive_or_new_chat_handoff_summary_latest.json",
      "created_at": "2026-07-07T02:31:19.347342+00:00",
      "stage": null
    }
  ],
  "uncertified": [
    {
      "phase": "27C_CANDIDATE_SANDBOX_DRY_RUN_STUB",
      "file": "runtime/strategy_candidate_sandbox/sandbox_dry_run_index_latest.json",
      "created_at": null,
      "stage": null
    },
    {
      "phase": "27E_CANDIDATE_SANDBOX_RESULT_STUB_GENERATOR",
      "file": "runtime/strategy_candidate_sandbox/candidate_sandbox_result_stub_index_latest.json",
      "created_at": null,
      "stage": null
    },
    {
      "phase": "28A_CANDIDATE_SANDBOX_SIMULATION_HARNESS_STUB",
      "file": "runtime/strategy_candidate_sandbox/simulation_harness_stub_latest.json",
      "created_at": null,
      "stage": null
    },
    {
      "phase": "28B_CANDIDATE_SANDBOX_MOCK_METRICS_GENERATOR",
      "file": "runtime/strategy_candidate_sandbox/candidate_sandbox_mock_metrics_index_latest.json",
      "created_at": null,
      "stage": null
    },
    {
      "phase": "28C_CANDIDATE_SANDBOX_MOCK_SCORECARD",
      "file": "runtime/strategy_candidate_sandbox/candidate_sandbox_mock_scorecard_latest.json",
      "created_at": null,
      "stage": null
    },
    {
      "phase": "28D_CANDIDATE_SANDBOX_EXECUTION_CONTRACT",
      "file": "runtime/strategy_candidate_sandbox/candidate_sandbox_execution_contract_v1.json",
      "created_at": null,
      "stage": null
    },
    {
      "phase": "29A_HISTORICAL_REPLAY_ENGINE_STUB",
      "file": "runtime/strategy_candidate_sandbox/historical_replay_engine_stub_latest.json",
      "created_at": null,
      "stage": null
    },
    {
      "phase": "29B_HISTORICAL_REPLAY_INPUT_CONTRACT",
      "file": "runtime/strategy_candidate_sandbox/historical_replay_input_contract_v1.json",
      "created_at": null,
      "stage": null
    },
    {
      "phase": "29C_HISTORICAL_REPLAY_VALIDATION_STUB",
      "file": "runtime/strategy_candidate_sandbox/historical_replay_validation_stub_latest.json",
      "created_at": null,
      "stage": null
    },
    {
      "phase": "29E_HISTORICAL_REPLAY_MARKET_DATA_PROVIDER_CONTRACT",
      "file": "runtime/strategy_candidate_sandbox/historical_replay_market_data_provider_contract_v1.json",
      "created_at": null,
      "stage": null
    },
    {
      "phase": "29F_HISTORICAL_REPLAY_PROVIDER_ADAPTER_STUB",
      "file": "runtime/strategy_candidate_sandbox/historical_replay_provider_adapter_stub_latest.json",
      "created_at": null,
      "stage": null
    },
    {
      "phase": "30A_YFINANCE_HISTORICAL_BARS_PROVIDER_PROBE",
      "file": "runtime/strategy_candidate_sandbox/yfinance_historical_bars_provider_probe_latest.json",
      "created_at": null,
      "stage": null
    },
    {
      "phase": "30C_HISTORICAL_BARS_CONTRACT",
      "file": "runtime/strategy_candidate_sandbox/historical_bars_contract_v1.json",
      "created_at": null,
      "stage": null
    },
    {
      "phase": "30D_YFINANCE_HISTORICAL_BARS_ADAPTER_STUB",
      "file": "runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_stub_latest.json",
      "created_at": null,
      "stage": null
    },
    {
      "phase": "30E_YFINANCE_HISTORICAL_BARS_ADAPTER_SHAPE_VALIDATION",
      "file": "runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_shape_validation_latest.json",
      "created_at": null,
      "stage": null
    },
    {
      "phase": "30F_YFINANCE_HISTORICAL_BARS_ADAPTER_WIRE_PREVIEW",
      "file": "runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_wire_preview_latest.json",
      "created_at": null,
      "stage": null
    },
    {
      "phase": "30G_YFINANCE_HISTORICAL_BARS_ADAPTER_WIRE",
      "file": "runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_wire_latest.json",
      "created_at": null,
      "stage": null
    },
    {
      "phase": "candidate_20260706_144431_8a545b3c_mock_metrics",
      "file": "runtime/strategy_candidate_sandbox/candidate_20260706_144431_8a545b3c_mock_metrics.json",
      "created_at": null,
      "stage": null
    },
    {
      "phase": "candidate_20260706_144431_8a545b3c_mock_scorecard",
      "file": "runtime/strategy_candidate_sandbox/candidate_20260706_144431_8a545b3c_mock_scorecard.json",
      "created_at": null,
      "stage": null
    },
    {
      "phase": "candidate_20260706_144431_8a545b3c_sandbox_result_stub",
      "file": "runtime/strategy_candidate_sandbox/candidate_20260706_144431_8a545b3c_sandbox_result_stub.json",
      "created_at": "2026-07-06T15:29:31.227538+00:00",
      "stage": null
    },
    {
      "phase": "candidate_20260706_144431_8a545b3c_sandbox_stub",
      "file": "runtime/strategy_candidate_sandbox/candidate_20260706_144431_8a545b3c_sandbox_stub.json",
      "created_at": "2026-07-06T15:29:30.431602+00:00",
      "stage": null
    },
    {
      "phase": "candidate_20260706_145350_816903d1_mock_metrics",
      "file": "runtime/strategy_candidate_sandbox/candidate_20260706_145350_816903d1_mock_metrics.json",
      "created_at": null,
      "stage": null
    },
    {
      "phase": "candidate_20260706_145350_816903d1_mock_scorecard",
      "file": "runtime/strategy_candidate_sandbox/candidate_20260706_145350_816903d1_mock_scorecard.json",
      "created_at": null,
      "stage": null
    },
    {
      "phase": "candidate_20260706_145350_816903d1_sandbox_result_stub",
      "file": "runtime/strategy_candidate_sandbox/candidate_20260706_145350_816903d1_sandbox_result_stub.json",
      "created_at": "2026-07-06T15:29:31.227641+00:00",
      "stage": null
    },
    {
      "phase": "candidate_20260706_145350_816903d1_sandbox_stub",
      "file": "runtime/strategy_candidate_sandbox/candidate_20260706_145350_816903d1_sandbox_stub.json",
      "created_at": "2026-07-06T15:29:30.431717+00:00",
      "stage": null
    },
    {
      "phase": "candidate_20260706_150540_4fc7b8ab_mock_metrics",
      "file": "runtime/strategy_candidate_sandbox/candidate_20260706_150540_4fc7b8ab_mock_metrics.json",
      "created_at": null,
      "stage": null
    },
    {
      "phase": "candidate_20260706_150540_4fc7b8ab_mock_scorecard",
      "file": "runtime/strategy_candidate_sandbox/candidate_20260706_150540_4fc7b8ab_mock_scorecard.json",
      "created_at": null,
      "stage": null
    },
    {
      "phase": "candidate_20260706_150540_4fc7b8ab_sandbox_result_stub",
      "file": "runtime/strategy_candidate_sandbox/candidate_20260706_150540_4fc7b8ab_sandbox_result_stub.json",
      "created_at": "2026-07-06T15:29:31.227730+00:00",
      "stage": null
    },
    {
      "phase": "candidate_20260706_150540_4fc7b8ab_sandbox_stub",
      "file": "runtime/strategy_candidate_sandbox/candidate_20260706_150540_4fc7b8ab_sandbox_stub.json",
      "created_at": "2026-07-06T15:29:30.431800+00:00",
      "stage": null
    },
    {
      "phase": "candidate_20260706_151330_9f852272_mock_metrics",
      "file": "runtime/strategy_candidate_sandbox/candidate_20260706_151330_9f852272_mock_metrics.json",
      "created_at": null,
      "stage": null
    },
    {
      "phase": "candidate_20260706_151330_9f852272_mock_scorecard",
      "file": "runtime/strategy_candidate_sandbox/candidate_20260706_151330_9f852272_mock_scorecard.json",
      "created_at": null,
      "stage": null
    },
    {
      "phase": "candidate_20260706_151330_9f852272_sandbox_result_stub",
      "file": "runtime/strategy_candidate_sandbox/candidate_20260706_151330_9f852272_sandbox_result_stub.json",
      "created_at": "2026-07-06T15:29:31.227808+00:00",
      "stage": null
    },
    {
      "phase": "candidate_20260706_151330_9f852272_sandbox_stub",
      "file": "runtime/strategy_candidate_sandbox/candidate_20260706_151330_9f852272_sandbox_stub.json",
      "created_at": "2026-07-06T15:29:30.431872+00:00",
      "stage": null
    },
    {
      "phase": "candidate_20260706_152354_e2129e4e_mock_metrics",
      "file": "runtime/strategy_candidate_sandbox/candidate_20260706_152354_e2129e4e_mock_metrics.json",
      "created_at": null,
      "stage": null
    },
    {
      "phase": "candidate_20260706_152354_e2129e4e_mock_scorecard",
      "file": "runtime/strategy_candidate_sandbox/candidate_20260706_152354_e2129e4e_mock_scorecard.json",
      "created_at": null,
      "stage": null
    },
    {
      "phase": "candidate_20260706_152354_e2129e4e_sandbox_result_stub",
      "file": "runtime/strategy_candidate_sandbox/candidate_20260706_152354_e2129e4e_sandbox_result_stub.json",
      "created_at": "2026-07-06T15:29:31.227878+00:00",
      "stage": null
    },
    {
      "phase": "candidate_20260706_152354_e2129e4e_sandbox_stub",
      "file": "runtime/strategy_candidate_sandbox/candidate_20260706_152354_e2129e4e_sandbox_stub.json",
      "created_at": "2026-07-06T15:29:30.431946+00:00",
      "stage": null
    },
    {
      "phase": "candidate_20260706_152930_73031c40_mock_metrics",
      "file": "runtime/strategy_candidate_sandbox/candidate_20260706_152930_73031c40_mock_metrics.json",
      "created_at": null,
      "stage": null
    },
    {
      "phase": "candidate_20260706_152930_73031c40_mock_scorecard",
      "file": "runtime/strategy_candidate_sandbox/candidate_20260706_152930_73031c40_mock_scorecard.json",
      "created_at": null,
      "stage": null
    },
    {
      "phase": "candidate_20260706_152930_73031c40_sandbox_result_stub",
      "file": "runtime/strategy_candidate_sandbox/candidate_20260706_152930_73031c40_sandbox_result_stub.json",
      "created_at": "2026-07-06T15:29:31.227948+00:00",
      "stage": null
    },
    {
      "phase": "candidate_20260706_152930_73031c40_sandbox_stub",
      "file": "runtime/strategy_candidate_sandbox/candidate_20260706_152930_73031c40_sandbox_stub.json",
      "created_at": "2026-07-06T15:29:30.432020+00:00",
      "stage": null
    },
    {
      "phase": "candidate_sandbox_result_example_latest",
      "file": "runtime/strategy_candidate_sandbox/candidate_sandbox_result_example_latest.json",
      "created_at": null,
      "stage": null
    },
    {
      "phase": "candidate_sandbox_result_schema_v1",
      "file": "runtime/strategy_candidate_sandbox/candidate_sandbox_result_schema_v1.json",
      "created_at": null,
      "stage": null
    }
  ]
}
```

---

# 33. [Governance] Developer Rulebook

Source: `handoff/project_bible/DEVELOPER_RULEBOOK.md`

# Developer Rulebook


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

---

# 34. [Roadmap] Roadmap

Source: `handoff/project_bible/ROADMAP.md`

# Roadmap


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

---

# 35. [Glossary] Glossary

Source: `handoff/project_bible/GLOSSARY.md`

# Glossary


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

---

# 36. [Traceability] Traceability Index

Source: `handoff/project_bible/TRACEABILITY_INDEX.md`

# Traceability Index


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

Certified count: 110
Uncertified / historical count: 43

---

# 37. [Machine Index] Repository Statistics

Source: `handoff/repository_statistics.json`

```json
{
  "total_files": 827,
  "total_dirs": 73,
  "python_files": 437,
  "typescript_files": 20,
  "json_files": 296,
  "markdown_files": 29,
  "scripts": 280,
  "tests": 231,
  "largest_files": [
    {
      "file": ".aider.tags.cache.v4/cache.db-wal",
      "bytes": 4124152
    },
    {
      "file": "runtime/graph_history/events.jsonl",
      "bytes": 2423897
    },
    {
      "file": "topology_wire_graph.png",
      "bytes": 1620490
    },
    {
      "file": "runtime/market_warehouse/history/AAPL_history.csv",
      "bytes": 1561584
    },
    {
      "file": "runtime/market_warehouse/history/MSFT_history.csv",
      "bytes": 1284408
    },
    {
      "file": "runtime/market_warehouse/history/TD_TO_history.csv",
      "bytes": 997917
    },
    {
      "file": "runtime/market_warehouse/history/RY_TO_history.csv",
      "bytes": 995607
    },
    {
      "file": "runtime/market_warehouse/history/NVDA_history.csv",
      "bytes": 956580
    },
    {
      "file": "cursor.AppImage",
      "bytes": 690286
    },
    {
      "file": "domain_runtime_overlay_graph.png",
      "bytes": 566611
    },
    {
      "file": "runtime/market_warehouse/history/TSLA_history.csv",
      "bytes": 539919
    },
    {
      "file": "runtime/market_warehouse/history/VFV_TO_history.csv",
      "bytes": 452228
    },
    {
      "file": "runtime/market_warehouse/history/VUN_TO_history.csv",
      "bytes": 426620
    },
    {
      "file": "domain_subsystem_graph.png",
      "bytes": 318287
    },
    {
      "file": "topology_wire_graph_canonical.png",
      "bytes": 308830
    },
    {
      "file": ".aider.chat.history.md",
      "bytes": 294388
    },
    {
      "file": "runtime/repo_memory/repo_index_v2.json",
      "bytes": 250378
    },
    {
      "file": ".aider.tags.cache.v4/cache.db",
      "bytes": 237568
    },
    {
      "file": "frontend/package-lock.json",
      "bytes": 221605
    },
    {
      "file": "neuro_cli_file_inspection.json",
      "bytes": 71718
    },
    {
      "file": "runtime/repo_memory/dependency_graph_v1.json",
      "bytes": 64283
    },
    {
      "file": "runtime/handoff_snapshot/neurovest_training_handoff_bundle_latest.json",
      "bytes": 59780
    },
    {
      "file": "frontend/app/page.tsx",
      "bytes": 35077
    },
    {
      "file": ".aider.input.history",
      "bytes": 33797
    },
    {
      "file": ".aider.tags.cache.v4/cache.db-shm",
      "bytes": 32768
    },
    {
      "file": "runtime/certifications/phase6b_dependency_validation_certification_latest.json",
      "bytes": 32429
    },
    {
      "file": "runtime/repo_memory/component_overlay_v1.json",
      "bytes": 30215
    },
    {
      "file": "runtime/handoff_snapshot/file_manifest_latest.txt",
      "bytes": 28495
    },
    {
      "file": "runtime/repo_memory/repo_index.json",
      "bytes": 27818
    },
    {
      "file": "runtime/handoff_snapshot/topology_tree_latest.txt",
      "bytes": 26518
    }
  ],
  "top_level": {
    "OUTPUT": 1,
    "ARCHITECTURE_REPAIR_PLAN.json": 1,
    "TOPOLOGY_NORMALIZED_STATE.json": 1,
    "ARCH_GOVERNANCE.md": 1,
    "fix_phase9_self_fingerprint.sh": 1,
    "TOPOLOGY_STATE.json": 1,
    "topology_wire_graph.png": 1,
    "neurovest_repo_context.md": 1,
    "Directory Structure": 1,
    "ORPHAN_RESOLUTION_PLAN.json": 1,
    "topology_wire_graph_canonical.png": 1,
    ".env.example": 1,
    "domain_subsystem_graph.png": 1,
    "generate_wire_graph.py": 1,
    "neuro_health.sh": 1,
    "neuro_cli_file_inspection.json": 1,
    ".aider.input.history": 1,
    "FINAL_ARCHITECTURE_STATE.json": 1,
    "system_tree.txt": 1,
    "docker-compose.yml": 1,
    "ARCH_ENFORCEMENT_REPORT.json": 1,
    "spine_mvp_full.sh": 1,
    "pytest.ini": 1,
    ".gitignore": 1,
    "$OUTPUT": 1,
    "SERVICE_RELOCATION_PLAN_RECONCILED.json": 1,
    ".env": 1,
    "domain_runtime_overlay_graph.png": 1,
    ".aider.chat.history.md": 1,
    "cursor.AppImage": 1,
    "neuro": 1,
    "neuro_cli.py": 1,
    "neuro_engineer.py": 1,
    "SERVICE_RELOCATION_PLAN.json": 1,
    "architecture_backup": 1,
    "scripts": 279,
    "backend": 157,
    ".aider.tags.cache.v4": 3,
    "frontend": 36,
    "backups": 1,
    "runtime": 315,
    ".github": 1
  }
}
```

---

# 38. [Machine Index] Project Bible

Source: `handoff/project_bible/PROJECT_BIBLE.json`

```json
{
  "phase": "63A_PROJECT_BIBLE_GENERATOR",
  "created_at": "2026-07-07T03:05:48.839971+00:00",
  "mode": "READ_ONLY_DOCUMENTATION_COMPILER",
  "source_handoff_dir": "/home/tkanhai/Neurovest/handoff",
  "output_dir": "/home/tkanhai/Neurovest/handoff/project_bible",
  "certified_count": 110,
  "uncertified_count": 43,
  "archive_summary": {
    "status": "archive_ready",
    "archive_mode": "terminal_read_only_archive",
    "latest_certified_phase": "60B_QWEN_READ_ONLY_TERMINAL_FREEZE_ROLLUP_CERTIFICATION",
    "terminal_stage": "Qwen Read-Only Terminal Freeze Certified",
    "read_only_chain_closed": true,
    "execution_surface_opened": false,
    "mutation_surface_opened": false,
    "critical_safety_locks": {
      "live_execution_enabled": false,
      "broker_execution_enabled": false,
      "simulation_enabled": false,
      "registry_write_enabled": false,
      "promotion_enabled": false,
      "learning_enabled": false
    },
    "archive_actions": [
      "retain certified artifacts",
      "retain certification chain",
      "retain safety locks",
      "retain read-only capability summaries",
      "handoff to future chat if required"
    ],
    "forbidden_after_archive": [
      "continue certification chain",
      "open runtime",
      "mutate source",
      "execute runtime",
      "broker execution",
      "live trading"
    ],
    "recommended_next_action": "START_NEW_CHAT_FROM_ARCHIVED_HANDOFF"
  },
  "generated_files": [
    "DATA_FLOW.md",
    "DEPENDENCY_GRAPH.md",
    "DEVELOPER_RULEBOOK.md",
    "EXECUTIVE_SUMMARY.md",
    "GLOSSARY.md",
    "NODE_MAP.md",
    "PROJECT_BIBLE.md",
    "QWEN_READ_ONLY_ARCHITECTURE.md",
    "ROADMAP.md",
    "TRACEABILITY_INDEX.md"
  ],
  "certified": true
}
```

---

# 39. [Machine Index] Architecture Atlas

Source: `handoff/project_bible/architecture_atlas/ARCHITECTURE_ATLAS.json`

```json
{
  "phase": "63B_ARCHITECTURE_ATLAS_GENERATOR",
  "created_at": "2026-07-07T03:10:44.679455+00:00",
  "mode": "READ_ONLY_ATLAS_COMPILER",
  "output_dir": "/home/tkanhai/Neurovest/handoff/project_bible/architecture_atlas",
  "phase_artifacts_scanned": 231,
  "python_import_files_scanned": 439,
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
    "TOPOLOGY/stack_graph.json"
  ],
  "certified": true
}
```

---

# Appendix A — Source Manifest

```json
[
  {
    "path": "handoff/project_bible/PROJECT_BIBLE.md",
    "category": "Reference",
    "bytes": 146646,
    "sha256": "6bf696c36520e60cde0ccf007cfcb8a4f9c43c2dc792d1fefd30c813fbb12d9b"
  },
  {
    "path": "handoff/project_bible/architecture_atlas/ARCHITECTURE_ATLAS.md",
    "category": "Reference",
    "bytes": 64337,
    "sha256": "bc09a78543e75e97981e809a35bad0a0ebd148297f404cc54fb96b29a72cfc2c"
  },
  {
    "path": "handoff/project_bible/EXECUTIVE_SUMMARY.md",
    "category": "Executive",
    "bytes": 798,
    "sha256": "07b58f69ad37915b1176af0921fcf2288cb4f77ff8ca3525ec70d1b28b5edabd"
  },
  {
    "path": "handoff/repository_tree.txt",
    "category": "Repository Topology",
    "bytes": 45885,
    "sha256": "07dcb7a687288f0a0ed8969b078c9170013a37548241050c7713d95bc5f17c45"
  },
  {
    "path": "handoff/backend_tree.txt",
    "category": "Repository Topology",
    "bytes": 8186,
    "sha256": "2df7bbfda0b242f577a1beb0c4e3975660dfccff0f0ade6dd4415328b6067e96"
  },
  {
    "path": "handoff/frontend_tree.txt",
    "category": "Repository Topology",
    "bytes": 1792,
    "sha256": "fb64a2e2a469f8f4126f15a70ac0366c874f7f5dd4a5924dc9f818cf84217c58"
  },
  {
    "path": "handoff/runtime_tree.txt",
    "category": "Repository Topology",
    "bytes": 21219,
    "sha256": "cc18035a392082ea2d712bcbad3bb13e1029ed73af06f0158a3d46800c03b35c"
  },
  {
    "path": "handoff/audit_tree.txt",
    "category": "Repository Topology",
    "bytes": 14,
    "sha256": "c3c27203567a7a7b81c295c5f9c729b81ea51cf5bbde19f69dc38a9e4fab2db8"
  },
  {
    "path": "handoff/canonical_layer_map.txt",
    "category": "Layer Architecture",
    "bytes": 23451,
    "sha256": "6a6bb43dcd4f18b1bdf3e35c563c02cfbb7b9ce2fde50f4f169776cfe65e79de"
  },
  {
    "path": "handoff/stack_topology.txt",
    "category": "Stack Architecture",
    "bytes": 20413,
    "sha256": "83740e3dbbd38706e625d5ae7e7a67e8d6e0f2f2327555642100106f69dc4b23"
  },
  {
    "path": "handoff/project_bible/architecture_atlas/STACK_OWNERSHIP.md",
    "category": "Stack Architecture",
    "bytes": 11597,
    "sha256": "2b2e9709c86c0ba7132fc5762744c022662804e237fbfa7562e3bdb454622fab"
  },
  {
    "path": "handoff/project_bible/architecture_atlas/LAYER_OWNERSHIP.md",
    "category": "Layer Architecture",
    "bytes": 7541,
    "sha256": "7f7d6f41df658e06b6570997836722351f38921fb037027b3def6b5f4c494205"
  },
  {
    "path": "handoff/runtime_node_graph.txt",
    "category": "Node / Topology",
    "bytes": 1127,
    "sha256": "09354c3e3b25fdbd162beb4ed273d6967481ff3b1b948c541cd165d4c26a6de5"
  },
  {
    "path": "handoff/project_bible/architecture_atlas/TOPOLOGY/node_graph.md",
    "category": "Node / Topology",
    "bytes": 1154,
    "sha256": "d8431367317c466a304f3b0a15922ba992b9d6ebed75fc9f7868a8efce67fe89"
  },
  {
    "path": "handoff/dependency_graph.txt",
    "category": "Dependency Atlas",
    "bytes": 369,
    "sha256": "5e047267360c3814608234da1ca4fc99d7ccf8eccbcabee45878fddd35384ae9"
  },
  {
    "path": "handoff/project_bible/architecture_atlas/TOPOLOGY/dependency_graph.md",
    "category": "Node / Topology",
    "bytes": 402,
    "sha256": "b1d3bb00b4900d6d9e964d9f3c67d4000e4ee117a4a248e5da39aa9113f5250b"
  },
  {
    "path": "handoff/runtime_state_machine.txt",
    "category": "Runtime State",
    "bytes": 557,
    "sha256": "d24c7833063a51056f0ffc008567e3697e7df035ad15f33d5bf3700f079ffdd6"
  },
  {
    "path": "handoff/project_bible/DATA_FLOW.md",
    "category": "Flows",
    "bytes": 715,
    "sha256": "41a4aafcb68dabb9b6c61c17f6dee94777cab32edfae2aa36559ebcc6cc5bac5"
  },
  {
    "path": "handoff/project_bible/architecture_atlas/FLOWS/market_data.md",
    "category": "Flows",
    "bytes": 166,
    "sha256": "2cb91e3f94132c421eb29e7cbc48fa441a93069eb4ff6c8d64de92715b242860"
  },
  {
    "path": "handoff/project_bible/architecture_atlas/FLOWS/candidate_pipeline.md",
    "category": "Flows",
    "bytes": 186,
    "sha256": "7541ebfa315a9d175e25ef89506d921d4bb5dd0082695c9d9c6c2ae1e74e349d"
  },
  {
    "path": "handoff/project_bible/architecture_atlas/FLOWS/execution_disabled.md",
    "category": "Flows",
    "bytes": 181,
    "sha256": "dfe6dbcf1c9d11551aab941f4c188385f6d342dcbb717b133f8478bc6a414ebd"
  },
  {
    "path": "handoff/project_bible/QWEN_READ_ONLY_ARCHITECTURE.md",
    "category": "Qwen Read-Only",
    "bytes": 609,
    "sha256": "e25b4ef9ad6b6275412e6fb05ed3412ddd5e98d852de59f12345b4b261fc0737"
  },
  {
    "path": "handoff/certification_timeline.txt",
    "category": "Certification History",
    "bytes": 11664,
    "sha256": "48d25564eee27ccfd337081d7ec29ce78ee4b3922c769e91e6aea3749b9b518c"
  },
  {
    "path": "handoff/project_bible/architecture_atlas/PHASE_TIMELINE.md",
    "category": "Certification History",
    "bytes": 41383,
    "sha256": "75493523854ed40952558f735aece8c79d22963e18a53b80b29a79e5315dc747"
  },
  {
    "path": "handoff/project_bible/DEVELOPER_RULEBOOK.md",
    "category": "Governance",
    "bytes": 685,
    "sha256": "6e6120de4324d22b53075b208fb135434915f75d7c8e5d448a952ff56da94914"
  },
  {
    "path": "handoff/project_bible/ROADMAP.md",
    "category": "Roadmap",
    "bytes": 806,
    "sha256": "5a73fa4c86a0040780adb9fdb650f6ebd01ad8284325b83f5d0e09d4242f2312"
  },
  {
    "path": "handoff/project_bible/GLOSSARY.md",
    "category": "Glossary",
    "bytes": 542,
    "sha256": "be1cbcee4f0cc0841d04efd96cf784f752f6d8d44873de16c28c4ae7f8c2c431"
  },
  {
    "path": "handoff/project_bible/TRACEABILITY_INDEX.md",
    "category": "Traceability",
    "bytes": 610,
    "sha256": "b32f0b41621dc615b85e315b4a98ddf799abe63563578004452bd12a22c300ef"
  },
  {
    "path": "handoff/repository_statistics.json",
    "category": "Machine Index",
    "bytes": 4228,
    "sha256": "9ef4ecdc5fc1d00481b66f1228d601f8393b2acad7e0baa6e23f186109a5ffb0"
  },
  {
    "path": "handoff/certified_phase_index.json",
    "category": "Certification History",
    "bytes": 39482,
    "sha256": "4972c0333fe708264215f2764251d2ce4940a9e2481be28ea15d06d35df64b89"
  },
  {
    "path": "handoff/topology_summary.json",
    "category": "Node / Topology",
    "bytes": 1582,
    "sha256": "4cd01df0c00d773e3cf4e029c379203f6555bbe0413b7059198dca13653b3b1b"
  },
  {
    "path": "handoff/project_bible/PROJECT_BIBLE.json",
    "category": "Machine Index",
    "bytes": 1741,
    "sha256": "3eb603ec5e6ca8f9f12917ca0969a0fc9a4642bc01dfb018192e8c3c85215f37"
  },
  {
    "path": "handoff/project_bible/architecture_atlas/ARCHITECTURE_ATLAS.json",
    "category": "Machine Index",
    "bytes": 682,
    "sha256": "f2479e3d4d9ddb97de3d274a63d2907dd67e406a32724a4e3060d217836120f0"
  },
  {
    "path": "handoff/project_bible/architecture_atlas/IMPORT_DEPENDENCY_ATLAS.json",
    "category": "Dependency Atlas",
    "bytes": 59744,
    "sha256": "6fbea90ccd58229c83529fc2da338879ad092da98e53835365a26d6cc2632a32"
  },
  {
    "path": "handoff/MASTER_ARCHITECTURE_HANDOFF.md",
    "category": "Reference",
    "bytes": 10642,
    "sha256": "952b976086d24173d779d253ef7718456a2dc569b729b316703f448e16e5e3d3"
  },
  {
    "path": "handoff/project_bible/DEPENDENCY_GRAPH.md",
    "category": "Dependency Atlas",
    "bytes": 402,
    "sha256": "b1d3bb00b4900d6d9e964d9f3c67d4000e4ee117a4a248e5da39aa9113f5250b"
  },
  {
    "path": "handoff/project_bible/INDEX.md",
    "category": "Reference",
    "bytes": 245,
    "sha256": "615719e55648047a68674729cfa92c69c75a131db860291fc4999d87375b0af7"
  },
  {
    "path": "handoff/project_bible/NODE_MAP.md",
    "category": "Node / Topology",
    "bytes": 1152,
    "sha256": "3bc346e0567f460a9a15456331b0462d1f934d98407424530e5ab439e24a6322"
  },
  {
    "path": "handoff/project_bible/architecture_atlas/TOPOLOGY/stack_graph.json",
    "category": "Stack Architecture",
    "bytes": 20413,
    "sha256": "83740e3dbbd38706e625d5ae7e7a67e8d6e0f2f2327555642100106f69dc4b23"
  }
]
```

# 40. Post-Archive Evolution

## Purpose

This section records architecture evolution occurring after the
62A Terminal Archive.

The 62A archive remains historically accurate and preserved.

Nothing in this section invalidates earlier certifications. It records
subsequent repository evolution, production-readiness inspection,
infrastructure qualification, and hardening activity.

---

## Phase 121–124 — Architecture Intelligence

Completed capabilities:

- Repository discovery
- Contract inventory
- Stack inventory
- Connectivity inspection
- Architecture intelligence
- Learning-artifact generation

Status:

**COMPLETED**

---

## Phase 125–134 — Repository Hardening Foundation

Completed capabilities:

- Repository normalization
- Stack-ownership inspection
- Runtime inspection
- Dependency mapping
- Controller validation
- Architecture enforcement

Status:

**COMPLETED**

---

## Phase 135 — Blind Production Readiness Audit

Phase 135 established an independent L7 verification system capable
of inspecting NeuroVest without assuming that the documented
architecture was correct.

Completed capabilities:

- Repository discovery
- Layer and stack mapping
- Import dependency analysis
- Runtime graph analysis
- Contract discovery
- Fintech capability grading
- AI capability grading
- Production-readiness grading
- Production-blocker grading
- Prioritized remediation planning
- Freeze verification

Phase 135 is the frozen software-verification baseline against which
future hardening changes must be compared.

Status:

**FROZEN AND VERIFIED**

---

## Phase 136 — Infrastructure Qualification

Phase 136 qualified the workstation and local NeuroVest runtime for
continued development and an early controlled user base.

### Hardware and thermal evidence

- AMD Ryzen 5 5600X
- 6 physical cores
- 12 logical processors
- Approximately 76 GiB usable memory
- NVMe primary storage
- AMD graphics hardware
- Controlled 120-second all-core stress test completed
- Peak CPU temperature remained within the defined safety envelope
- Cooling recovery completed successfully
- No thermal safety abort occurred

### Storage evidence

- Storage qualification grade: EXCELLENT
- Sequential read throughput exceeded 3 GiB/s
- Sequential write throughput exceeded 3 GiB/s
- Mixed random read/write performance exceeded 48,000 IOPS
- Temporary benchmark data was removed after qualification

### Runtime evidence

- Global architecture firewall remained active
- Firewall scope was corrected to govern internal NeuroVest imports
  without incorrectly blocking standard-library and third-party
  runtime modules
- FastAPI/Uvicorn backend launched successfully
- OpenAPI responded successfully on local port 8000

### Read-path load evidence

The following simultaneous read-user levels completed successfully:

- 10 users
- 20 users
- 30 users
- 40 users
- 50 users
- 75 users
- 100 users
- 150 users
- 200 users

At 200 simultaneous read users:

- Zero request failures
- Approximately 731 requests per second
- Approximately 166 ms p95 latency
- Approximately 221 ms p99 latency
- Approximately 14 percent average CPU use
- Approximately 68 GiB available memory
- Maximum observed CPU temperature remained below 57°C

### Capacity interpretation

The system demonstrated support for at least 200 simultaneous users
on the tested read-only API routes.

This does not certify 200 simultaneous users performing every possible
workload. Authenticated isolation, write-heavy traffic, paper-order
processing, long-context AI inference, WebSockets, streaming market
data, and external-provider latency require workload-specific
qualification.

The first expected scaling constraint is local AI inference rather
than ordinary read-only API traffic.

### Approval state

- Development use: QUALIFIED
- Controlled early-user testing: QUALIFIED
- Production deployment: NOT YET APPROVED
- Broker execution: NOT APPROVED
- Live trading: NOT APPROVED

Status:

**INFRASTRUCTURE QUALIFIED FOR CONTINUED DEVELOPMENT AND CONTROLLED EARLY-USER TESTING**

---

## Current Active Campaign

### Hardening Workstream 1 — Repository Connectivity Remediation

Pass 1:

**Active Import Resolution**

Pass 2:

**Dependency-Cycle Verification and Remediation**

Pass 3:

**Module Reachability Analysis**

Pass 4:

**Ownership Verification**

The workstream must follow this sequence:

```text
Inspect existing evidence
    ↓
Classify confirmed defects
    ↓
Apply the smallest contract-compliant repair
    ↓
Run focused verification
    ↓
Rerun Phase 135
    ↓
Compare with the frozen baseline
    ↓
Confirm no regression
    ↓
Freeze the completed workstream
Planned later workstreams
API contract validation
Persistence and transaction validation
Append-only decision and execution auditing
AI tool-registry and authorization hardening
AI input validation and safety governance
Confidence and uncertainty handling
Comprehensive L7 verification
Isolated paper-mode validation
Authentication integration
SnapTrade integration
Production certification
High availability
Horizontal scaling
