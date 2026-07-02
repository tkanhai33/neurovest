# Phase 9 Paper Trading Skeleton Contract

## Status

Phase 9 skeleton only.

## Purpose

Create the paper trading stack shape without implementing simulated fills, position mutation, PnL calculations, strategy integration, risk integration, broker interaction, or execution.

## Allowed

- paper account contract
- paper order contract
- paper fill contract
- paper position contract
- paper PnL contract
- skeleton rejection service
- status service
- API placeholder
- tests
- certification artifact

## Forbidden

- simulated order engine
- simulated fill engine
- position mutation
- PnL calculations
- strategy integration
- risk integration
- broker interaction
- execution
- business logic

## Default State

- paper account implemented: false
- simulated order engine implemented: false
- simulated fill engine implemented: false
- paper position logic implemented: false
- PnL logic implemented: false
- strategy integration implemented: false
- risk integration implemented: false
- broker integration implemented: false

## Exit Criteria

- tests pass
- paper_trading stack has contracts/services/api placeholders
- all paper orders rejected by skeleton
- no fill engine exists
- no strategy/risk/broker integration exists
