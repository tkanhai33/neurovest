
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
