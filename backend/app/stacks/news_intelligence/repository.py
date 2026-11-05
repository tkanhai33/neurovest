from __future__ import annotations

from sqlalchemy import (
    desc,
    select,
)

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.stacks.news_intelligence.models import (
    NewsIntelligenceRecord,
)


class NewsIntelligenceRepository:

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def list_recent(
        self,
        *,
        limit: int = 50,
        symbol: str | None = None,
    ) -> list[NewsIntelligenceRecord]:

        statement = select(
            NewsIntelligenceRecord
        )

        if symbol:
            statement = statement.where(
                NewsIntelligenceRecord.symbol
                ==
                symbol.upper()
            )

        statement = (
            statement
            .order_by(
                desc(
                    NewsIntelligenceRecord.published_at
                ),
                desc(
                    NewsIntelligenceRecord.id
                ),
            )
            .limit(
                max(
                    1,
                    min(
                        limit,
                        200,
                    ),
                )
            )
        )

        result = await self._session.execute(
            statement
        )

        return list(
            result.scalars().all()
        )
