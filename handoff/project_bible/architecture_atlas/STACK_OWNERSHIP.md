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
