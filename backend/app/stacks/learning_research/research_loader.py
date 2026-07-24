from backend.app.stacks.db_runtime.transaction_guard import transaction_guard
from backend.app.stacks.db_model.market_schema import ResearchData
from backend.app.stacks.journal_ledger.ledger import async_session


async def add_research(category: str, title: str, content: dict, tags: str):

    async with async_session() as session:

        async with transaction_guard(session):
            record = ResearchData(
                category=category,
                title=title,
                content=content,
                tags=tags
            )

            session.add(record)
            await session.commit()
