
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

