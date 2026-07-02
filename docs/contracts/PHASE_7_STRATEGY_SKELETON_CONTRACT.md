# Phase 7 Strategy Skeleton Contract

## Status

Phase 7 skeleton only.

## Purpose

Create the strategy stack shape without implementing signal generation, candidate scoring, optimization, risk approval, paper trading, broker interaction, or execution.

## Allowed

- strategy signal contract
- strategy candidate contract
- strategy version contract
- status service
- API placeholder
- tests
- certification artifact

## Forbidden

- signal generation
- candidate scoring
- strategy optimization
- strategy promotion implementation
- risk approval
- paper trading
- broker interaction
- execution
- business logic

## Default State

- signal generation implemented: false
- candidate scoring implemented: false
- promotion logic implemented: false
- risk integration implemented: false
- paper trading integration implemented: false
- broker integration implemented: false

## Exit Criteria

- tests pass
- strategy stack has contracts/services/api placeholders
- no signal generation exists
- no scoring exists
- no risk/paper/broker execution exists
