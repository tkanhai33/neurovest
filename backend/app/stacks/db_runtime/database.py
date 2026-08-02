"""
134B1_CHAT_DATABASE_OWNERSHIP_NORMALIZATION

Canonical asynchronous SQLAlchemy ownership for NeuroVest runtime data.

Environment precedence:
1. NEUROVEST_DATABASE_URL
2. DATABASE_URL
3. Existing ledger-compatible fallback

Synchronous PostgreSQL driver names are normalized to asyncpg because
the runtime uses SQLAlchemy's asynchronous engine and sessions.
"""

from __future__ import annotations

from backend.app.core.runtime_trace import (
    create_trace_id,
    emit_runtime_step,
)


import os

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


DEFAULT_DATABASE_URL = (
    "postgresql+asyncpg://"
    "postgres:postgres@localhost:5432/neurovest"
)


def normalize_async_database_url(
    database_url: str,
) -> str:
    clean_url = database_url.strip()

    replacements = {
        "postgresql+psycopg://": "postgresql+asyncpg://",
        "postgresql+psycopg2://": "postgresql+asyncpg://",
        "postgresql://": "postgresql+asyncpg://",
        "postgres://": "postgresql+asyncpg://",
    }

    for source, destination in replacements.items():
        if clean_url.startswith(source):
            return destination + clean_url[len(source):]

    return clean_url


def resolve_database_url() -> str:
    configured_url = (
        os.getenv("NEUROVEST_DATABASE_URL")
        or os.getenv("DATABASE_URL")
        or DEFAULT_DATABASE_URL
    )

    return normalize_async_database_url(
        configured_url
    )


DATABASE_URL = resolve_database_url()


class Base(DeclarativeBase):
    """Canonical runtime ORM metadata owner."""


engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

async_session: async_sessionmaker[AsyncSession] = (
    async_sessionmaker(
        engine,
        expire_on_commit=False,
    )
)


async def init_db() -> None:
    """
    Create missing tables for models already registered on Base.

    Runtime model discovery belongs to the application composition
    root and must complete before this function is called.
    """

    trace_id = create_trace_id(
        "database-runtime"
    )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="DATABASE_RUNTIME_INITIALIZATION",
        node="db_runtime",
        status="active",
        message=(
            "Database runtime initialization began"
        ),
        layer="L0",
        stack="db_runtime",
    )


    # Runtime ORM models are registered by the application
    # composition root before this function is called.
    # Database infrastructure does not import domain stacks.

    async with engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.create_all
        )


def database_runtime_status() -> dict[str, object]:
    return {
        "status": "configured",
        "driver": engine.url.drivername,
        "database": engine.url.database,
        "host": engine.url.host,
        "port": engine.url.port,
        "username": engine.url.username,
        "async_driver": (
            engine.url.drivername
            == "postgresql+asyncpg"
        ),
        "password_exposed": False,
    }
