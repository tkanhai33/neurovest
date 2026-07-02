#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p docs/contracts

cat > docs/contracts/MASTER_ARCHITECTURE_CONTRACT.md <<'EOF'
# NeuroVest Master Architecture Contract

## Purpose

NeuroVest is a local-first fintech, AI, research, portfolio analysis, and paper-trading platform.

It must be built top-down, stack-first, layer-isolated, contract-driven, test-certified, and safety-locked.

## Starting Mode

NeuroVest starts as:

```text
Research + portfolio analysis + paper trading only

Forbidden at start:

No live trading
No broker orders
No autonomous real-money execution
No AI self-mutation
No hidden runtime writes
No frontend-to-broker calls
No AI-to-broker calls
No paid AI dependency
No public deployment
Layer Model
L0 External Providers
L1 Security / Safety
L2 Domain Logic
L3 Services / Facades
L4 Runtime Orchestration
L5 API Presentation
L6 Frontend
L7 Tests / Certification
Build Rule

Every feature must follow:

Design
Contract
Skeleton
Test Plan
Implementation
Certification
Lock

Execution comes last.
EOF

cat > docs/contracts/STACK_OWNERSHIP_MAP.md <<'EOF'

NeuroVest Stack Ownership Map

Every file must belong to one stack, one layer, and one purpose.

Backend Stacks
identity_auth
safety_governance
market_data
portfolio
research
strategy
risk
ai_chat
runtime
paper_trading
broker_integration
admin_control
Stack Responsibilities
identity_auth

Owns users, roles, permissions, sessions, account identity.

safety_governance

Owns kill switches, mode locks, approval gates, policy state, audit rules.

market_data

Owns symbols, quotes, candles, exchange status, asset universe, provider normalization.

portfolio

Owns holdings, balances, transactions, performance, allocation snapshots.

research

Owns indicators, screeners, backtests, market summaries, historical comparison.

strategy

Owns signals, trade ideas, candidate scoring, strategy versions, strategy lineage.

risk

Owns position sizing, exposure limits, drawdown limits, daily limits, approval/rejection.

ai_chat

Owns conversation, explanations, research assistance, portfolio explanation, strategy explanation.

runtime

Owns workflow orchestration, schedulers, state transitions, manual workflow coordination.

paper_trading

Owns simulated orders, simulated fills, paper portfolio, paper P/L.

broker_integration

Owns future broker connection, read-only snapshots, order preview, locked execution boundary.

admin_control

Owns system state visibility, certification reports, diagnostics, mode visibility.

Shared Code Rule

Allowed shared folders:

shared/contracts
shared/errors
shared/logging
shared/config
shared/db

Forbidden dumping-ground folders:

utils
helpers
misc
common
temp
old

EOF

cat > docs/contracts/FORBIDDEN_CALL_RULES.md <<'EOF'

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
EOF

cat > docs/contracts/BUILD_ORDER_PHASE_GATE_CONTRACT.md <<'EOF'

NeuroVest Build Order & Phase Gate Contract
Build Order
Phase 0  Architecture Contracts
Phase 1  Repository Skeleton
Phase 2  Identity / Auth
Phase 3  Safety / Governance
Phase 4  Market Data
Phase 5  Portfolio
Phase 6  Research
Phase 7  Strategy
Phase 8  Risk
Phase 9  AI / Chat
Phase 10 Runtime
Phase 11 Paper Trading
Phase 12 Broker Read-Only Integration
Phase 13 Frontend
Phase 14 Admin / Dev Control Center
Phase 15 Canary Trading Review
Phase 16 Live Trading Review
Universal Phase Lifecycle
Design
Contract
Skeleton
Test Plan
Implementation
Certification
Lock
Next Phase
Stop Conditions

Development stops if any appear:

Circular dependency
Ownership unclear
Forbidden import
Broker leak
Safety bypass
Runtime bypass
Hidden execution path
Architecture drift
Locked Features
Broker orders
Canary trading
Live trading
AI self-mutation
Self-modifying strategies
Autonomous execution

EOF

cat > docs/contracts/FREE_PROVIDER_PRODUCT_DIRECTION_CONTRACT.md <<'EOF'

NeuroVest Free Provider & Product Direction Contract
Core Philosophy

NeuroVest must be:

Local-first
Free-provider-first
Simple
Safe
Replaceable
Maintainable
AI Runtime

Primary local AI runtime:

Ollama

Approved starting models:

qwen3:8b
qwen2.5-coder:14b
qwen3-coder:30b

No paid cloud LLM is required for MVP.

Market Data

Primary:

yfinance

Secondary:

Finnhub free tier
Broker

MVP broker state:

No broker

Future path:

No broker
Read-only
Order preview
Canary review
Live review
UI Direction

The UI must be:

Elegant
Professional
Attainable
Readable
Maintainable

The UI must not be:

Overly sci-fi
Over-animated
Shader-heavy
Hard to maintain
Cluttered

EOF

cat > docs/contracts/SYSTEM_CONTEXT_DATA_FLOW_CONTRACT.md <<'EOF'

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
EOF

cat > docs/contracts/REPOSITORY_BLUEPRINT_CONTRACT.md <<'EOF'

NeuroVest Repository Blueprint Contract
Root Shape
Neurovest/
  backend/
  frontend/
  docs/
  scripts/
  certification/
  data/
  .env.example
  README.md
Backend Shape
backend/
  app/
    main.py
    api/
    shared/
      contracts/
      errors/
      logging/
      config/
      db/
    stacks/
      identity_auth/
      safety_governance/
      market_data/
      portfolio/
      research/
      strategy/
      risk/
      ai_chat/
      runtime/
      paper_trading/
      broker_integration/
      admin_control/
  tests/
Stack Folder Shape
stack_name/
  contracts/
  domain/
  services/
  adapters/
  api/
  tests/
  README.md
Frontend Shape
frontend/src/
  app/
  components/
  features/
  lib/
Naming Rules

Use lowercase snake_case for backend folders and files.

No vague folders:

utils
helpers
misc
common
random
old
temp

EOF

cat > docs/contracts/LOCAL_SYSTEM_RESOURCE_CONTRACT.md <<'EOF'

NeuroVest Local System Resource Contract
Current Development Machine
CPU: AMD Ryzen 5 5600X / 12 threads
RAM: 76 GB
Disk: 654 GB free at inspection time
GPU: AMD Radeon RX 9060 XT
Ollama: installed
Approved Local Model Roles
qwen3:8b
- default chat
- quick explanations
- lightweight reasoning

qwen2.5-coder:14b
- coding assistant
- repo analysis
- implementation support

qwen3-coder:30b
- heavy coding
- deeper reasoning
- slower local assistant
Python Runtime Rule

Project backend must use:

Python 3.12

System Python may be newer, but the project virtual environment must target Python 3.12.
EOF

cat > docs/contracts/MVP_DEFAULTS_CONTRACT.md <<'EOF'

NeuroVest MVP Defaults Contract
Core Default

When uncertain, choose:

Simple
Local
Free
Safe
Testable
Replaceable
Backend
Python 3.12
FastAPI
PostgreSQL
Alembic
SQLAlchemy or SQLModel placeholder
pytest
Frontend
Next.js
TypeScript
Clean fintech UI
Left sidebar
Top safety/status bar
Cards
Tables
Simple charts later
Database

Primary:

PostgreSQL

SQLite allowed only for scratch tests.

Security
Local-only
Developer machine only
No public deployment
No live broker orders
No autonomous real-money trading
Legal Boundary

NeuroVest starts as:

Personal research tool
Educational assistant
Paper-trading simulator
Portfolio analysis helper

NeuroVest is not:

Financial advice
Public broker
Licensed advisor
Guaranteed profit system

EOF

cat > docs/contracts/DATABASE_DEFAULT_UPDATE.md <<'EOF'

NeuroVest Database Default Update
Decision

Use PostgreSQL as the primary database from Phase 1 onward.

Reason

NeuroVest will eventually store:

Users
Sessions
Portfolio snapshots
Market data cache
Research outputs
Strategy candidates
Risk approvals/rejections
Paper trades
Audit logs
AI memory metadata
Broker read-only snapshots
SQLite Rule

SQLite is allowed only for:

Temporary scratch tests
Tiny throwaway experiments
Standalone scripts

SQLite is not the main application database.
EOF

cat > docs/contracts/FINAL_CONTRACT_CHECKLIST.md <<'EOF'

NeuroVest Final Contract Checklist
Confirmed Contract Set
1. Master Architecture Contract
2. Stack Ownership Map
3. Forbidden Call Rules
4. Build Order & Phase Gate Contract
5. Free Provider & Product Direction Contract
6. System Context & Data Flow Contract
7. Repository Blueprint Contract
8. Local System Resource Contract
9. MVP Defaults Contract
10. Database Default Update
11. Final Contract Checklist
Confirmed MVP Defaults
Backend: Python 3.12 + FastAPI
Frontend: Next.js + TypeScript
Database: PostgreSQL
Migrations: Alembic
AI Runtime: Ollama
Market Data: yfinance first, Finnhub free tier second
Broker: none for MVP
Runtime: manual only at start
Deployment: local-only
Final Start Decision

NeuroVest is approved to enter Phase 1 — Repository Skeleton.

Phase 1 is skeleton-only.

No business logic yet.
EOF

cat > scripts/phase_1a_verify_contract_docs.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

required=(
docs/contracts/MASTER_ARCHITECTURE_CONTRACT.md
docs/contracts/STACK_OWNERSHIP_MAP.md
docs/contracts/FORBIDDEN_CALL_RULES.md
docs/contracts/BUILD_ORDER_PHASE_GATE_CONTRACT.md
docs/contracts/FREE_PROVIDER_PRODUCT_DIRECTION_CONTRACT.md
docs/contracts/SYSTEM_CONTEXT_DATA_FLOW_CONTRACT.md
docs/contracts/REPOSITORY_BLUEPRINT_CONTRACT.md
docs/contracts/LOCAL_SYSTEM_RESOURCE_CONTRACT.md
docs/contracts/MVP_DEFAULTS_CONTRACT.md
docs/contracts/DATABASE_DEFAULT_UPDATE.md
docs/contracts/FINAL_CONTRACT_CHECKLIST.md
)

for file in "${required[@]}"; do
test -f "$file"
done

grep -q "PostgreSQL" docs/contracts/MVP_DEFAULTS_CONTRACT.md
grep -q "Ollama" docs/contracts/FREE_PROVIDER_PRODUCT_DIRECTION_CONTRACT.md
grep -q "No live trading" docs/contracts/MASTER_ARCHITECTURE_CONTRACT.md
grep -q "Phase 1 is skeleton-only" docs/contracts/FINAL_CONTRACT_CHECKLIST.md

echo "PASS: Phase 1A full contract documents written and verified."
EOF

chmod +x scripts/phase_1a_verify_contract_docs.sh
bash scripts/phase_1a_verify_contract_docs.sh
