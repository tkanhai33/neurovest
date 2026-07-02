# Phase 10 Broker Integration Skeleton Contract

## Status

Phase 10 skeleton only.

## Purpose

Create the broker integration stack shape without implementing real SnapTrade calls, authentication, token storage, account sync, order preview logic, order submission, live trading, or execution.

## Allowed

- broker provider enum
- broker account contract
- broker position contract
- broker order preview contract
- SnapTrade placeholder adapter
- status service
- API placeholder
- tests
- certification artifact

## Forbidden

- real SnapTrade API calls
- broker authentication
- token persistence
- account synchronization
- order preview implementation
- order submission
- live trading
- execution
- business logic

## Default State

- broker auth implemented: false
- token storage implemented: false
- account sync implemented: false
- read-only calls enabled: false
- order preview implemented: false
- order submission implemented: false
- live trading implemented: false

## Exit Criteria

- tests pass
- broker_integration stack has contracts/services/api/adapters placeholders
- no real broker calls exist
- no token storage exists
- no order submission exists
- no live trading exists
