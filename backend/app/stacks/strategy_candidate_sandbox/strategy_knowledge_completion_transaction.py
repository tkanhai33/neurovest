from __future__ import annotations
import asyncio

from collections.abc import Mapping
from typing import Any

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from backend.app.stacks.db_runtime.database import DATABASE_URL
from backend.app.stacks.db_runtime.database import (
    async_session,
)

from backend.app.stacks.strategy.strategy_knowledge_repository import (
    StrategyKnowledgeRepository,
)

from .strategy_knowledge_runtime_persistence import (
    persist_runtime_candidate_strategy_knowledge,
)


async def persist_best_runtime_candidate_at_completion(
    *,
    candidate: Mapping[str, Any],
):
    """
    Persist one already-selected best runtime candidate.

    This function owns the explicit completion transaction.

    Repository methods remain transaction-neutral.
    """

    async with async_session() as session:

        async with session.begin():

            repository = StrategyKnowledgeRepository(
                session
            )

            return await persist_runtime_candidate_strategy_knowledge(
                repository=repository,
                candidate=candidate,
            )

async def persist_best_runtime_candidate_at_completion_worker_local(
    *,
    candidate: Mapping[str, Any],
):
    """
    Persist an already-selected runtime winner using an AsyncEngine
    owned entirely by the adaptive-training worker event loop.
    """

    worker_engine = create_async_engine(
        DATABASE_URL,
        poolclass=NullPool,
    )

    worker_session = async_sessionmaker(
        bind=worker_engine,
        expire_on_commit=False,
    )

    try:

        async with worker_session() as session:

            async with session.begin():

                repository = StrategyKnowledgeRepository(
                    session
                )

                return await persist_runtime_candidate_strategy_knowledge(
                    repository=repository,
                    candidate=candidate,
                )

    finally:

        await worker_engine.dispose()


def persist_best_runtime_candidate_at_completion_sync(
    *,
    candidate: Mapping[str, Any],
):
    """
    Synchronous bridge for the dedicated adaptive-training worker.
    """

    try:

        asyncio.get_running_loop()

    except RuntimeError:

        return asyncio.run(
            persist_best_runtime_candidate_at_completion_worker_local(
                candidate=candidate,
            )
        )

    raise RuntimeError(
        "sync completion persistence bridge cannot run "
        "inside an active asyncio event loop"
    )
