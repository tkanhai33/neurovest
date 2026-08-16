from sqlalchemy import select

from backend.app.stacks.db_runtime.database import (
    async_session,
)
from backend.app.stacks.identity_auth.contracts import (
    AuthenticatedPrincipal,
)
from backend.app.stacks.journal_ledger.ledger import (
    PortfolioInventory,
)


def _principal_subject(
    principal: AuthenticatedPrincipal,
) -> str:
    subject = str(
        getattr(
            principal,
            "subject",
            "",
        )
    ).strip()

    if not subject:
        raise ValueError(
            "Authenticated portfolio principal subject cannot be empty"
        )

    return subject


async def get_portfolio_positions_for_api(
    principal: AuthenticatedPrincipal,
) -> dict[str, object]:
    """
    Return durable portfolio inventory belonging only to the
    authenticated NeuroVest principal.
    """

    user_id = _principal_subject(
        principal
    )

    async with async_session() as session:

        result = await session.execute(
            select(
                PortfolioInventory
            )
            .where(
                PortfolioInventory.user_id
                ==
                user_id
            )
            .order_by(
                PortfolioInventory.symbol.asc()
            )
        )

        rows = result.scalars().all()

    positions = [
        {
            "id":
                row.id,

            "symbol":
                str(
                    row.symbol
                ).strip().upper(),

            "shares_quantity":
                str(
                    row.shares_quantity
                ),

            "average_entry_price":
                str(
                    row.average_entry_price
                ),

            "total_cost_basis":
                str(
                    row.total_cost_basis
                ),

            "realized_pnl":
                str(
                    row.realized_pnl
                ),

            "last_updated":
                (
                    row.last_updated.isoformat()
                    if row.last_updated
                    is not None
                    else None
                ),
        }
        for row in rows
    ]

    return {
        "status":
            "ok",

        "positions":
            positions,

        "count":
            len(
                positions
            ),

        "provider":
            "portfolio_inventory",

        "scope":
            "authenticated_account",
    }
