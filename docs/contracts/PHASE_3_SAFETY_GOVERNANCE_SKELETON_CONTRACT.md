# Phase 3 Safety / Governance Skeleton Contract

## Status

Phase 3 skeleton only.

## Purpose

Create the safety/governance stack shape without implementing real mode changes or unlock behavior.

## Allowed

- system mode enum
- safety state contract
- execution-denial skeleton
- status service
- API placeholder
- tests
- certification artifact

## Forbidden

- broker unlock implementation
- live trading unlock implementation
- canary unlock implementation
- runtime unlock implementation
- AI mutation unlock implementation
- real permission enforcement
- business logic

## Default State

- system mode: research_only
- kill switch: enabled
- broker orders: disabled
- live trading: disabled
- canary trading: disabled
- autonomous runtime: disabled
- AI mutation: disabled

## Exit Criteria

- tests pass
- safety_governance stack has contracts/services/api placeholders
- all execution paths denied
- no real unlock implementation exists
