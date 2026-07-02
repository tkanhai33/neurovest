
NeuroVest Forbidden Call Rules
Absolute Forbidden Calls
Frontend -> Broker Provider
Frontend -> Database
Frontend -> Risk Logic
Frontend -> Strategy Logic
Frontend -> Safety Unlock Logic

AI Chat -> Broker Provider
AI Chat -> Order Submission
AI Chat -> Live Mode Toggle
AI Chat -> Safety Unlock

Strategy -> Broker Provider
Strategy -> Order Submission
Strategy -> Portfolio Mutation
Strategy -> Safety Unlock

Risk -> Broker Provider
Risk -> Order Submission
Risk -> Strategy Generation

Runtime -> Broker Provider Directly
Runtime -> Safety Bypass
Runtime -> Risk Bypass
Runtime -> Hidden State Mutation

API Route -> Broker Provider Directly
API Route -> Strategy Math
API Route -> Risk Math
API Route -> Provider Adapter Directly

Domain Logic -> FastAPI
Domain Logic -> Frontend
Domain Logic -> Broker SDK
Domain Logic -> Database Session
Required Broker Order Path

Broker orders are forbidden during MVP.

Future allowed path only:

User Approval
-> API
-> Safety Governance
-> Risk
-> Broker Service
-> Broker Provider Adapter
Required AI Path
Frontend
-> AI Chat API
-> AI Chat Service
-> Approved Services
-> Response

AI can explain and recommend. AI cannot execute.
