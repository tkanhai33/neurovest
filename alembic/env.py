"""
Canonical NeuroVest Alembic environment.

Canonical ownership:

- Async engine:
  backend.app.stacks.db_runtime.database.engine

- ORM metadata:
  backend.app.stacks.db_runtime.database.Base.metadata

The isolated legacy db_model.market_schema.Base is intentionally excluded.
"""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.engine import Connection

from backend.app.stacks.db_runtime.database import (
    Base,
    engine,
)

# Register canonical runtime ORM models with Base.metadata.
from backend.app.stacks.journal_ledger.decision_event_model import (  # noqa: F401
    DecisionEventRecord,
)


config = context.config

if config.config_file_name:
    fileConfig(
        config.config_file_name
    )


target_metadata = Base.metadata


def canonical_database_url() -> str:
    return engine.url.render_as_string(
        hide_password=False
    )


def run_migrations_offline() -> None:
    context.configure(
        url=canonical_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
        },
        compare_type=True,
        compare_server_default=True,
        version_table="alembic_version",
    )

    with context.begin_transaction():
        context.run_migrations()


def run_sync_migrations(
    connection: Connection,
) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        version_table="alembic_version",
        transaction_per_migration=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    async with engine.connect() as connection:
        await connection.run_sync(
            run_sync_migrations
        )


def run_migrations_online() -> None:
    asyncio.run(
        run_async_migrations()
    )


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
