

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
