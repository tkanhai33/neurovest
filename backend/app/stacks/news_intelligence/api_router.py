from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.stacks.db_runtime.database import (
    async_session,
)

from backend.app.stacks.news_intelligence.repository import (
    NewsIntelligenceRepository,
)

from backend.app.stacks.news_intelligence.service import (
    NewsIntelligenceService,
)


router = APIRouter(
    prefix="/api/v1/news",
    tags=[
        "news-intelligence",
    ],
)


async def news_database_session() -> (
    AsyncIterator[AsyncSession]
):
    async with async_session() as session:
        yield session


@router.get("")
async def list_news_intelligence(
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
    symbol: str | None = Query(
        default=None,
        min_length=1,
        max_length=32,
    ),
    session: AsyncSession = Depends(
        news_database_session
    ),
) -> dict[str, object]:

    repository = NewsIntelligenceRepository(
        session
    )

    service = NewsIntelligenceService(
        repository
    )

    items = await service.list_recent(
        limit=limit,
        symbol=symbol,
    )

    return {
        "items":
            items,

        "count":
            len(
                items
            ),
    }
