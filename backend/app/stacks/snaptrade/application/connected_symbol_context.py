"""
Authenticated, read-only connected SnapTrade symbol context.

Never accepts a user ID from chat text or model output.
The caller must provide the server-authenticated principal subject.
No provider calls, credentials, or paper inventory are involved.
"""

from sqlalchemy import select

from backend.app.stacks.db_runtime.database import async_session
from backend.app.stacks.snaptrade.persistence.external_portfolio_models import (
    SnapTradeExternalPortfolioPosition,
)


async def get_connected_symbols_for_owner(
    *,
    authenticated_owner_user_id: str,
) -> list[str]:
    owner = str(authenticated_owner_user_id or "").strip()

    if not owner:
        raise ValueError("Authenticated owner identity is required")

    async with async_session() as session:
        result = await session.execute(
            select(SnapTradeExternalPortfolioPosition.symbol)
            .where(
                SnapTradeExternalPortfolioPosition.neurovest_user_id
                == owner
            )
            .order_by(SnapTradeExternalPortfolioPosition.symbol)
        )

        symbols = result.scalars().all()

    return sorted({
        str(symbol).strip().upper()
        for symbol in symbols
        if symbol and str(symbol).strip()
    })
