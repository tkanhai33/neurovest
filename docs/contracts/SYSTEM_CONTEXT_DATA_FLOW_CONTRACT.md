
NeuroVest System Context & Data Flow Contract
Core Flow
Frontend
-> API
-> Service
-> Domain / Safety / Provider
-> Service
-> API
-> Frontend

No shortcut paths are allowed.

AI Chat Flow
User
-> Frontend Chat
-> AI Chat API
-> AI Chat Service
-> Approved Services
-> AI Response
-> Frontend
Market Data Flow
Frontend
-> Market Data API
-> Market Data Service
-> Provider Adapter
-> yfinance / Finnhub
-> Normalized Data
-> Frontend
Strategy Flow
Market Data
-> Research
-> Strategy Candidates
-> Risk
-> Paper Trading
Paper Trading Flow
Approved Candidate
-> Paper Trading Service
-> Simulated Order
-> Simulated Fill
-> Paper Portfolio
Source Of Truth Rule

Frontend is not source of truth.

AI is not source of truth.

Backend services, stores, contracts, and certified state are source of truth.
