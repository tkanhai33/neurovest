# Neurovest Fintech Architecture Governance Manual

## Core Coding Constraints
1. **Zero Domain Logic in Routers**: Routers ONLY parse HTTP inputs and delegate immediately to the `services/` layer.
2. **Immutable Financial Calculations**: All balances, transaction allocations, and asset evaluations must be calculated using exact fixed-point or precise decimal arithmetic in dedicated isolation blocks.
3. **Data Protection & Sanitization**: Personal financial data must pass strict input verification (via Pydantic schemas) before entering system computation routines.
4. **Idempotency Standards**: Transaction endpoints must enforce tracking keys to prevent accidental duplicate balance mutations.
