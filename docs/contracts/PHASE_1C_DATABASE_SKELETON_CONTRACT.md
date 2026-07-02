# Phase 1C Database Skeleton Contract

## Decision

PostgreSQL is installed and used as the primary local database.

## Scope

Allowed in Phase 1C:

```text
PostgreSQL service
local database
local database user
database connection test
settings loader
Alembic placeholder
no schema migrations yet

Forbidden in Phase 1C:

business tables
trading tables
broker tables
strategy tables
risk engine tables
AI memory tables
runtime tables
Safety

Database exists only as infrastructure.

No application business state is created yet.
