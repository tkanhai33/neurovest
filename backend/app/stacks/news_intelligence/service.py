from __future__ import annotations

from backend.app.stacks.news_intelligence.repository import (
    NewsIntelligenceRepository,
)


class NewsIntelligenceService:

    def __init__(
        self,
        repository: NewsIntelligenceRepository,
    ) -> None:
        self._repository = repository

    async def list_recent(
        self,
        *,
        limit: int,
        symbol: str | None,
    ) -> list[dict[str, object]]:

        records = await self._repository.list_recent(
            limit=limit,
            symbol=symbol,
        )

        return [
            {
                "id":
                    record.id,

                "symbol":
                    record.symbol,

                "headline":
                    record.headline,

                "summary":
                    record.summary,

                "source_name":
                    record.source_name,

                "source_url":
                    record.source_url,

                "published_at":
                    (
                        record.published_at.isoformat()
                        if record.published_at
                        else
                        None
                    ),

                "created_at":
                    record.created_at.isoformat(),
            }
            for record in records
        ]
