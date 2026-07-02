# Phase 4 Market Data Skeleton Contract

## Status

Phase 4 skeleton only.

## Purpose

Create the market data stack shape without implementing real provider calls.

## Allowed

- symbol contract
- quote contract
- candle contract
- provider enum
- exchange status enum
- yfinance placeholder adapter
- Finnhub placeholder adapter
- status service
- API placeholder
- tests
- certification artifact

## Forbidden

- real yfinance calls
- real Finnhub calls
- network requests
- strategy logic
- risk logic
- broker interaction
- portfolio mutation
- business logic

## Default State

- yfinance adapter implemented: false
- Finnhub adapter implemented: false
- live provider calls enabled: false
- strategy logic implemented: false
- risk logic implemented: false

## Exit Criteria

- tests pass
- market_data stack has contracts/services/api/adapters placeholders
- no real provider implementation exists
- no strategy/risk/broker logic exists
