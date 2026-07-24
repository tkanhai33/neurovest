"""DOMAIN_LOGIC_V1 asynchronous portfolio audit and ledger reconciliation daemon."""

import asyncio

from sqlalchemy import select

from backend.app.stacks.journal_ledger.ledger import (
    OrderHistory,
    PortfolioInventory,
    async_session,
)


def _normalize_reconciliation_user_id(
    user_id: str,
) -> str:
    normalized_user_id = str(
        user_id
    ).strip()

    if not normalized_user_id:
        raise ValueError(
            "Reconciliation ownership user_id cannot be empty"
        )

    return normalized_user_id


async def resolve_reconciliation_owner_id() -> str | None:
    """
    Resolve the sole controlled portfolio owner for the legacy
    periodic reconciliation daemon.

    NeuroVest now supports multiple authenticated portfolio owners.
    The daemon must never select an arbitrary account. When exactly
    one owner exists, return that owner. When zero or multiple owners
    exist, return None and require explicit owner-scoped reconciliation.
    """

    async with async_session() as session:
        inventory_result = await session.execute(
            select(
                PortfolioInventory.user_id
            )
            .where(
                PortfolioInventory.user_id.is_not(
                    None
                )
            )
            .distinct()
        )

        order_result = await session.execute(
            select(
                OrderHistory.user_id
            )
            .where(
                OrderHistory.user_id.is_not(
                    None
                )
            )
            .distinct()
        )

        inventory_owner_ids = {
            str(owner_id).strip()
            for owner_id
            in inventory_result.scalars().all()
            if owner_id is not None
            and str(owner_id).strip()
        }

        order_owner_ids = {
            str(owner_id).strip()
            for owner_id
            in order_result.scalars().all()
            if owner_id is not None
            and str(owner_id).strip()
        }

    owner_ids = (
        inventory_owner_ids
        | order_owner_ids
    )

    if len(owner_ids) == 1:
        return next(
            iter(owner_ids)
        )

    return None


async def run_reconciliation_audit(
    *,
    user_id: str,
    trace_id: str | None = None,
) -> dict:
    """
    Audit one authenticated owner's executed transaction totals
    against that same owner's portfolio inventory.

    Reconciliation is prohibited from reading or changing another
    owner's rows.
    """

    normalized_user_id = (
        _normalize_reconciliation_user_id(
            user_id
        )
    )

    if trace_id:
        from backend.app.core.runtime_trace import (
            emit_runtime_step,
        )

        await emit_runtime_step(
            trace_id=trace_id,
            event_type="RECONCILIATION_STARTED",
            node="portfolio_reconciliation",
            source="portfolio_accounting",
            destination="portfolio_reconciliation",
            status="active",
            message=(
                "Portfolio reconciliation audit started"
            ),
            layer="L4",
            stack="portfolio",
            details={
                "user_id":
                    normalized_user_id,
            },
        )

    audit_results = {
        "status": "success",
        "user_id": normalized_user_id,
        "corrections_applied": 0,
        "details": [],
    }

    try:
        async with async_session() as session:
            async with session.begin():
                inventory_statement = (
                    select(
                        PortfolioInventory
                    )
                    .where(
                        PortfolioInventory.user_id
                        == normalized_user_id
                    )
                )

                inventory_result = (
                    await session.execute(
                        inventory_statement
                    )
                )

                warehouse_positions = (
                    inventory_result
                    .scalars()
                    .all()
                )

                for position in warehouse_positions:
                    order_statement = (
                        select(
                            OrderHistory
                        )
                        .where(
                            OrderHistory.user_id
                            == normalized_user_id,
                            OrderHistory.symbol
                            == position.symbol,
                            OrderHistory.status
                            == "executed",
                        )
                    )

                    order_result = (
                        await session.execute(
                            order_statement
                        )
                    )

                    executed_orders = (
                        order_result
                        .scalars()
                        .all()
                    )

                    recalculated_shares = 0.0

                    for order in executed_orders:
                        if (
                            order.allocated_capital
                            and order.slippage_price
                        ):
                            quantity = (
                                float(
                                    order.allocated_capital
                                )
                                / float(
                                    order.slippage_price
                                )
                            )

                            signal = str(
                                order.signal
                            ).lower()

                            if signal in {
                                "buy",
                                "long",
                            }:
                                recalculated_shares += (
                                    quantity
                                )

                            elif signal in {
                                "sell",
                                "short",
                            }:
                                recalculated_shares -= (
                                    quantity
                                )

                    corrected_shares = max(
                        0.0,
                        recalculated_shares,
                    )

                    variance = abs(
                        float(
                            position.shares_quantity
                        )
                        - corrected_shares
                    )

                    if variance > 0.0001:
                        audit_results[
                            "corrections_applied"
                        ] += 1

                        audit_results[
                            "details"
                        ].append(
                            {
                                "user_id":
                                    normalized_user_id,
                                "symbol":
                                    position.symbol,
                                "old_shares":
                                    position.shares_quantity,
                                "corrected_shares":
                                    corrected_shares,
                                "drift_variance":
                                    variance,
                            }
                        )

                        position.shares_quantity = (
                            corrected_shares
                        )

                        position.total_cost_basis = (
                            float(
                                position.shares_quantity
                            )
                            * float(
                                position.average_entry_price
                            )
                        )

                await session.flush()

        if trace_id:
            from backend.app.core.runtime_trace import (
                emit_runtime_step,
            )

            await emit_runtime_step(
                trace_id=trace_id,
                event_type="RECONCILIATION_COMPLETE",
                node="portfolio_reconciliation",
                status="completed",
                message=(
                    "Portfolio reconciliation audit completed"
                ),
                layer="L4",
                stack="portfolio",
                details={
                    "user_id":
                        normalized_user_id,
                    "corrections_applied":
                        audit_results[
                            "corrections_applied"
                        ],
                },
            )

        return audit_results

    except Exception as error:
        if trace_id:
            from backend.app.core.runtime_trace import (
                emit_runtime_step,
            )

            await emit_runtime_step(
                trace_id=trace_id,
                event_type="RECONCILIATION_FAILED",
                node="portfolio_reconciliation",
                status="failed",
                message=str(error),
                layer="L4",
                stack="portfolio",
                details={
                    "user_id":
                        normalized_user_id,
                },
            )

        return {
            "status": "error",
            "user_id": normalized_user_id,
            "message": str(error),
        }


async def start_periodic_reconciliation_daemon(
    *,
    user_id: str,
    interval_seconds: int = 3600,
) -> None:
    """
    Periodically reconcile one explicitly identified owner.

    The owner is normalized before the loop begins so an invalid
    daemon configuration fails immediately rather than silently.
    """

    normalized_user_id = (
        _normalize_reconciliation_user_id(
            user_id
        )
    )

    while True:
        await asyncio.sleep(
            interval_seconds
        )

        print(
            "Audit Triggered: Executing portfolio ledger "
            "reconciliation daemon pass..."
        )

        await run_reconciliation_audit(
            user_id=normalized_user_id,
        )
