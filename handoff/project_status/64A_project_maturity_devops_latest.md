# NeuroVest Project Maturity DevOps Report

Generated: 2026-07-07T03:42:11.803009+00:00
Phase: 64A_PROJECT_MATURITY_DEVOPS_CONTROLLER

## Current Stage

**Late Alpha**

Next focus: Sandbox Runtime Activation / Research Engine Completion

Completion estimate: 70.64%

## Safety Posture

Safety posture OK: True
All critical locks false: True
Execution surface opened: False
Mutation surface opened: False

## Capability Status

- architecture_topology: CERTIFIED
- market_data: READY
- strategy_core: READY
- candidate_sandbox: READY
- historical_replay: READY
- risk_framework: READY
- execution_engine: LOCKED
- paper_trading: LOCKED
- broker_execution: LOCKED
- live_trading: LOCKED
- learning_research: IN_PROGRESS
- qwen_read_only: TERMINAL_FROZEN

## Certification Summary

- artifacts: 231
- certified: 161
- uncertified/historical: 70
- certified ratio: 69.7%

## Stack Readiness

- market_data: 100.0% (5/5)
- strategy: 100.0% (5/5)
- strategy_candidate_sandbox: 100.0% (5/5)
- risk: 100.0% (5/5)
- execution: 100.0% (5/5)
- portfolio: 100.0% (5/5)
- learning_research: 100.0% (5/5)
- chat_public: 100.0% (5/5)
- wolfden_ai: 100.0% (5/5)
- frontend: 100.0% (6/6)

## Machine JSON

```json
{
  "phase": "64A_PROJECT_MATURITY_DEVOPS_CONTROLLER",
  "created_at": "2026-07-07T03:42:11.803009+00:00",
  "mode": "READ_ONLY_DEVOPS_SCAN",
  "repo": {
    "total_files": 888,
    "python_files": 441,
    "typescript_files": 20,
    "json_files": 305,
    "markdown_files": 64,
    "test_files": 231,
    "script_files": 288,
    "backend_files": 159,
    "frontend_files": 36,
    "runtime_files": 316,
    "handoff_files": 43
  },
  "certifications": {
    "artifact_count": 231,
    "certified_count": 161,
    "uncertified_count": 70,
    "certified_ratio": 69.7,
    "latest_certified": [
      {
        "file": "runtime/strategy_candidate_sandbox/58A_qwen_read_only_final_context_package_stub_latest.json",
        "phase": "58A_QWEN_READ_ONLY_FINAL_CONTEXT_PACKAGE_STUB",
        "certified": true,
        "created_at": "2026-07-07T01:42:00.600060+00:00",
        "stage": null,
        "latest_confirmed_phase": null
      },
      {
        "file": "runtime/strategy_candidate_sandbox/58B_qwen_read_only_final_context_package_rollup_certification_latest.json",
        "phase": "58B_QWEN_READ_ONLY_FINAL_CONTEXT_PACKAGE_ROLLUP_CERTIFICATION",
        "certified": true,
        "created_at": "2026-07-07T01:50:46.052707+00:00",
        "stage": null,
        "latest_confirmed_phase": null
      },
      {
        "file": "runtime/strategy_candidate_sandbox/58C_handoff_bundle_refresh_latest.json",
        "phase": "58C_HANDOFF_BUNDLE_REFRESH",
        "certified": true,
        "created_at": "2026-07-07T01:55:54.520435+00:00",
        "stage": null,
        "latest_confirmed_phase": null
      },
      {
        "file": "runtime/strategy_candidate_sandbox/59A_qwen_read_only_final_handoff_certification_stub_latest.json",
        "phase": "59A_QWEN_READ_ONLY_FINAL_HANDOFF_CERTIFICATION_STUB",
        "certified": true,
        "created_at": "2026-07-07T01:57:58.019119+00:00",
        "stage": null,
        "latest_confirmed_phase": null
      },
      {
        "file": "runtime/strategy_candidate_sandbox/59B_qwen_read_only_final_handoff_certification_rollup_certification_latest.json",
        "phase": "59B_QWEN_READ_ONLY_FINAL_HANDOFF_CERTIFICATION_ROLLUP_CERTIFICATION",
        "certified": true,
        "created_at": "2026-07-07T02:03:49.659517+00:00",
        "stage": null,
        "latest_confirmed_phase": null
      },
      {
        "file": "runtime/strategy_candidate_sandbox/59C_handoff_bundle_refresh_latest.json",
        "phase": "59C_HANDOFF_BUNDLE_REFRESH",
        "certified": true,
        "created_at": "2026-07-07T02:07:59.342307+00:00",
        "stage": null,
        "latest_confirmed_phase": null
      },
      {
        "file": "runtime/strategy_candidate_sandbox/60A_qwen_read_only_terminal_freeze_stub_latest.json",
        "phase": "60A_QWEN_READ_ONLY_TERMINAL_FREEZE_STUB",
        "certified": true,
        "created_at": "2026-07-07T02:17:06.874264+00:00",
        "stage": null,
        "latest_confirmed_phase": null
      },
      {
        "file": "runtime/strategy_candidate_sandbox/60B_qwen_read_only_terminal_freeze_rollup_certification_latest.json",
        "phase": "60B_QWEN_READ_ONLY_TERMINAL_FREEZE_ROLLUP_CERTIFICATION",
        "certified": true,
        "created_at": "2026-07-07T02:21:23.020937+00:00",
        "stage": null,
        "latest_confirmed_phase": null
      },
      {
        "file": "runtime/strategy_candidate_sandbox/60C_handoff_bundle_refresh_latest.json",
        "phase": "60C_HANDOFF_BUNDLE_REFRESH",
        "certified": true,
        "created_at": "2026-07-07T02:26:36.247863+00:00",
        "stage": null,
        "latest_confirmed_phase": null
      },
      {
        "file": "runtime/strategy_candidate_sandbox/61A_archive_or_new_chat_handoff_summary_latest.json",
        "phase": "61A_ARCHIVE_OR_NEW_CHAT_HANDOFF_SUMMARY",
        "certified": true,
        "created_at": "2026-07-07T02:31:19.347342+00:00",
        "stage": null,
        "latest_confirmed_phase": null
      }
    ]
  },
  "stack_readiness": {
    "market_data": {
      "base_exists": true,
      "signals_found": [
        "bars.py",
        "market_data_service.py",
        "provider_registry.py",
        "provider_router.py",
        "yfinance_historical_bars_adapter.py"
      ],
      "signal_count": 5,
      "signal_total": 5,
      "readiness_score": 100.0
    },
    "strategy": {
      "base_exists": true,
      "signals_found": [
        "candidate_registry.py",
        "engine.py",
        "strategy_registry.py",
        "strategy_runtime.py",
        "strategy_service.py"
      ],
      "signal_count": 5,
      "signal_total": 5,
      "readiness_score": 100.0
    },
    "strategy_candidate_sandbox": {
      "base_exists": true,
      "signals_found": [
        "manual_promotion_gate.py",
        "replay_metrics_contract.py",
        "replay_metrics_generator.py",
        "risk_gate_contract.py",
        "trade_simulation_enablement_gate_contract.py"
      ],
      "signal_count": 5,
      "signal_total": 5,
      "readiness_score": 100.0
    },
    "risk": {
      "base_exists": true,
      "signals_found": [
        "drawdown_guard.py",
        "kill_switch.py",
        "loss_streak_guard.py",
        "risk_runtime_service.py",
        "risk_service.py"
      ],
      "signal_count": 5,
      "signal_total": 5,
      "readiness_score": 100.0
    },
    "execution": {
      "base_exists": true,
      "signals_found": [
        "broker.py",
        "executor.py",
        "paper_broker.py",
        "sandbox_runtime.py",
        "trade_ledger.py"
      ],
      "signal_count": 5,
      "signal_total": 5,
      "readiness_score": 100.0
    },
    "portfolio": {
      "base_exists": true,
      "signals_found": [
        "accounting.py",
        "allocator.py",
        "dashboard_service.py",
        "portfolio_runtime.py",
        "portfolio_service.py"
      ],
      "signal_count": 5,
      "signal_total": 5,
      "readiness_score": 100.0
    },
    "learning_research": {
      "base_exists": true,
      "signals_found": [
        "backtest_engine.py",
        "monte_carlo.py",
        "monte_carlo_mix.py",
        "research_runtime.py",
        "strategy_evaluator.py"
      ],
      "signal_count": 5,
      "signal_total": 5,
      "readiness_score": 100.0
    },
    "chat_public": {
      "base_exists": true,
      "signals_found": [
        "chat_api.py",
        "chat_runtime.py",
        "chat_service.py",
        "ollama_chat_client.py",
        "strategy_proposal_capture.py"
      ],
      "signal_count": 5,
      "signal_total": 5,
      "readiness_score": 100.0
    },
    "wolfden_ai": {
      "base_exists": true,
      "signals_found": [
        "agent_router.py",
        "memory.py",
        "orchestrator.py",
        "routing.py",
        "runtime.py"
      ],
      "signal_count": 5,
      "signal_total": 5,
      "readiness_score": 100.0
    },
    "frontend": {
      "base_exists": true,
      "signals_found": [
        "chatService.ts",
        "marketService.ts",
        "page.tsx",
        "portfolioService.ts",
        "riskService.ts",
        "strategyService.ts"
      ],
      "signal_count": 6,
      "signal_total": 6,
      "readiness_score": 100.0
    }
  },
  "safety_locks": {
    "archive_exists": true,
    "archive_certified": true,
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
    "all_critical_locks_false": true
  },
  "capabilities": {
    "architecture_topology": "CERTIFIED",
    "market_data": "READY",
    "strategy_core": "READY",
    "candidate_sandbox": "READY",
    "historical_replay": "READY",
    "risk_framework": "READY",
    "execution_engine": "LOCKED",
    "paper_trading": "LOCKED",
    "broker_execution": "LOCKED",
    "live_trading": "LOCKED",
    "learning_research": "IN_PROGRESS",
    "qwen_read_only": "TERMINAL_FROZEN"
  },
  "stage": {
    "current_stage": "Late Alpha",
    "next_stage_focus": "Sandbox Runtime Activation / Research Engine Completion",
    "completion_estimate_percent": 70.64,
    "ready_capability_count": 7,
    "capability_total": 12,
    "safety_posture_ok": true
  },
  "certified": true
}
```
