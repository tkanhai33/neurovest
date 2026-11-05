from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from backend.app.stacks.db_model.strategy_knowledge import (
    StrategyKnowledge,
)

from backend.app.stacks.strategy.strategy_knowledge_repository import (
    StrategyKnowledgeRepository,
)

from .strategy_knowledge_runtime_mapper import (
    map_runtime_candidate_to_strategy_knowledge,
)


async def persist_runtime_candidate_strategy_knowledge(
    *,
    repository: StrategyKnowledgeRepository,
    candidate: Mapping[str, Any],
) -> StrategyKnowledge:
    """
    Map one proven runtime strategy candidate into StrategyKnowledge
    and pass it through the repository.

    Transaction ownership intentionally remains outside this helper.

    This helper MUST NOT commit, rollback, open a session, or open
    a transaction.
    """

    record = map_runtime_candidate_to_strategy_knowledge(
        candidate
    )

    return await repository.insert_candidate(
        record
    )
