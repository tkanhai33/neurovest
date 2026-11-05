# Workstream 1 Implementation Disposition Ledger

Created: `2026-07-10T20:56:27.250654+00:00`

## Purpose

This ledger records the approved disposition of the 12 exact-source scaffold modules identified during Workstream 1.

These files are deferred implementation surfaces. They are not authorized for deletion, automatic consolidation, or runtime composition.

## Approved Rules

1. Cross-stack exact duplicates must remain separate.
2. Same-stack files with different responsibilities must be implemented separately.
3. Shared bases may be introduced only after common behavior is proven.
4. Scaffold health checks do not count as production implementation.
5. Runtime wiring requires a dedicated owning workstream.

## Module Dispositions

### `backend/app/stacks/chat_public/chat_memory.py`

- Stack: `chat_public`
- Cluster: `EXACT_CLUSTER_1`
- Current state: **DOCUMENTED_SCAFFOLD**
- Disposition: **PRESERVE_AND_IMPLEMENT_SEPARATELY**
- Implementation priority: **MEDIUM**
- Target workstream: AI Chat and Memory Hardening Workstream
- Responsibility: Own persistent or conversational memory behavior for the public chat stack.
- Runtime wiring authorized: **NO**
- Deletion authorized: **NO**
- Cross-stack consolidation authorized: **NO**

### `backend/app/stacks/learning_research/monte_carlo.py`

- Stack: `learning_research`
- Cluster: `EXACT_CLUSTER_1`
- Current state: **DOCUMENTED_SCAFFOLD**
- Disposition: **PRESERVE_AND_IMPLEMENT_SEPARATELY**
- Implementation priority: **MEDIUM**
- Target workstream: Learning and Research Implementation Workstream
- Responsibility: Perform Monte Carlo simulation and probability analysis.
- Runtime wiring authorized: **NO**
- Deletion authorized: **NO**
- Cross-stack consolidation authorized: **NO**

### `backend/app/stacks/learning_research/research_runtime.py`

- Stack: `learning_research`
- Cluster: `EXACT_CLUSTER_1`
- Current state: **DOCUMENTED_SCAFFOLD**
- Disposition: **PRESERVE_AND_IMPLEMENT_SEPARATELY**
- Implementation priority: **MEDIUM**
- Target workstream: Learning and Research Implementation Workstream
- Responsibility: Compose learning and research operations at runtime.
- Runtime wiring authorized: **NO**
- Deletion authorized: **NO**
- Cross-stack consolidation authorized: **NO**

### `backend/app/stacks/wolfden_ai/runtime.py`

- Stack: `wolfden_ai`
- Cluster: `EXACT_CLUSTER_1`
- Current state: **DOCUMENTED_SCAFFOLD**
- Disposition: **PRESERVE_AND_IMPLEMENT_SEPARATELY**
- Implementation priority: **MEDIUM**
- Target workstream: Wolfden AI Runtime Hardening Workstream
- Responsibility: Own runtime orchestration for its containing stack.
- Runtime wiring authorized: **NO**
- Deletion authorized: **NO**
- Cross-stack consolidation authorized: **NO**

### `backend/app/stacks/learning_research/backtest_engine.py`

- Stack: `learning_research`
- Cluster: `EXACT_CLUSTER_2`
- Current state: **DOCUMENTED_SCAFFOLD**
- Disposition: **DEFER_TO_OWNING_FEATURE_WORKSTREAM**
- Implementation priority: **MEDIUM**
- Target workstream: Learning and Research Implementation Workstream
- Responsibility: Execute historical strategy backtests.
- Runtime wiring authorized: **NO**
- Deletion authorized: **NO**
- Cross-stack consolidation authorized: **NO**

### `backend/app/stacks/learning_research/monte_carlo_mix.py`

- Stack: `learning_research`
- Cluster: `EXACT_CLUSTER_2`
- Current state: **DOCUMENTED_SCAFFOLD**
- Disposition: **DEFER_TO_OWNING_FEATURE_WORKSTREAM**
- Implementation priority: **MEDIUM**
- Target workstream: Learning and Research Implementation Workstream
- Responsibility: Combine Monte Carlo results or simulation variants.
- Runtime wiring authorized: **NO**
- Deletion authorized: **NO**
- Cross-stack consolidation authorized: **NO**

### `backend/app/stacks/learning_research/probability_engine.py`

- Stack: `learning_research`
- Cluster: `EXACT_CLUSTER_2`
- Current state: **DOCUMENTED_SCAFFOLD**
- Disposition: **DEFER_TO_OWNING_FEATURE_WORKSTREAM**
- Implementation priority: **MEDIUM**
- Target workstream: Learning and Research Implementation Workstream
- Responsibility: Calculate probability, confidence, or outcome distributions.
- Runtime wiring authorized: **NO**
- Deletion authorized: **NO**
- Cross-stack consolidation authorized: **NO**

### `backend/app/stacks/learning_research/strategy_evaluator.py`

- Stack: `learning_research`
- Cluster: `EXACT_CLUSTER_2`
- Current state: **DOCUMENTED_SCAFFOLD**
- Disposition: **DEFER_TO_OWNING_FEATURE_WORKSTREAM**
- Implementation priority: **MEDIUM**
- Target workstream: Learning and Research Implementation Workstream
- Responsibility: Evaluate strategy performance and acceptance criteria.
- Runtime wiring authorized: **NO**
- Deletion authorized: **NO**
- Cross-stack consolidation authorized: **NO**

### `backend/app/stacks/market_data/market_session.py`

- Stack: `market_data`
- Cluster: `EXACT_CLUSTER_3`
- Current state: **DOCUMENTED_SCAFFOLD**
- Disposition: **DEFER_TO_OWNING_FEATURE_WORKSTREAM**
- Implementation priority: **HIGH**
- Target workstream: Market Data Runtime and Provider Composition Workstream
- Responsibility: Represent or determine current market-session state.
- Runtime wiring authorized: **NO**
- Deletion authorized: **NO**
- Cross-stack consolidation authorized: **NO**

### `backend/app/stacks/market_data/provider_cache.py`

- Stack: `market_data`
- Cluster: `EXACT_CLUSTER_3`
- Current state: **DOCUMENTED_SCAFFOLD**
- Disposition: **DEFER_TO_OWNING_FEATURE_WORKSTREAM**
- Implementation priority: **HIGH**
- Target workstream: Market Data Runtime and Provider Composition Workstream
- Responsibility: Cache provider results and control freshness.
- Runtime wiring authorized: **NO**
- Deletion authorized: **NO**
- Cross-stack consolidation authorized: **NO**

### `backend/app/stacks/market_data/provider_registry.py`

- Stack: `market_data`
- Cluster: `EXACT_CLUSTER_3`
- Current state: **DOCUMENTED_SCAFFOLD**
- Disposition: **DEFER_TO_OWNING_FEATURE_WORKSTREAM**
- Implementation priority: **HIGH**
- Target workstream: Market Data Runtime and Provider Composition Workstream
- Responsibility: Register and resolve approved market-data providers.
- Runtime wiring authorized: **NO**
- Deletion authorized: **NO**
- Cross-stack consolidation authorized: **NO**

### `backend/app/stacks/market_data/provider_router.py`

- Stack: `market_data`
- Cluster: `EXACT_CLUSTER_3`
- Current state: **DOCUMENTED_SCAFFOLD**
- Disposition: **DEFER_TO_OWNING_FEATURE_WORKSTREAM**
- Implementation priority: **HIGH**
- Target workstream: Market Data Runtime and Provider Composition Workstream
- Responsibility: Route market-data requests to an approved provider.
- Runtime wiring authorized: **NO**
- Deletion authorized: **NO**
- Cross-stack consolidation authorized: **NO**

## Implementation Sequence

1. Market Data Runtime and Provider Composition Workstream
2. Learning and Research Implementation Workstream
3. AI Chat and Memory Hardening Workstream
4. Wolfden AI Runtime Hardening Workstream

## Safety State

- Source modified by Pass 4D: **NO**
- Runtime wiring changed: **NO**
- Files deleted: **NO**
- Files moved: **NO**
- Broker execution enabled: **NO**
- Live trading enabled: **NO**
