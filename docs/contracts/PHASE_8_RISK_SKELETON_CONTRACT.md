# Phase 8 Risk Skeleton Contract

## Status

Phase 8 skeleton only.

## Purpose

Create the risk stack shape without implementing position sizing, exposure calculations, drawdown calculations, trade approval, paper trading, broker interaction, or execution.

## Allowed

- risk limit contract
- position sizing contract
- risk decision contract
- risk status service
- skeleton denial service
- API placeholder
- tests
- certification artifact

## Forbidden

- position sizing math
- exposure calculations
- drawdown calculations
- daily trade counter implementation
- real trade approval
- paper trading
- broker interaction
- execution
- business logic

## Default State

- position sizing implemented: false
- exposure limits implemented: false
- drawdown limits implemented: false
- daily trade limits implemented: false
- approval engine implemented: false
- broker integration implemented: false
- paper trading integration implemented: false

## Exit Criteria

- tests pass
- risk stack has contracts/services/api placeholders
- all approvals denied
- no risk math exists
- no paper/broker/execution logic exists
