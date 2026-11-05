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
