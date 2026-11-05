import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, UniqueConstraint, func, select, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.stacks.db_runtime.database import (
    Base,
    async_session,
)

class OrderHistory(Base):
    __tablename__ = "order_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(
        ForeignKey(
            "identity_users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    symbol: Mapped[str] = mapped_column(nullable=False)
    signal: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)
    timestamp: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow)
    allocated_capital: Mapped[float] = mapped_column(nullable=True)
    slippage_price: Mapped[float] = mapped_column(nullable=True)
    commission_paid: Mapped[float] = mapped_column(nullable=True)

class PortfolioInventory(Base):
    __tablename__ = "portfolio_inventory"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "symbol",
            name="uq_portfolio_inventory_user_id_symbol",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(
        ForeignKey(
            "identity_users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    symbol: Mapped[str] = mapped_column(nullable=False)
    shares_quantity: Mapped[Decimal] = mapped_column(
        Numeric(46, 28),
        default=Decimal("0"),
    )
    average_entry_price: Mapped[Decimal] = mapped_column(
        Numeric(46, 28),
        default=Decimal("0"),
    )
    total_cost_basis: Mapped[Decimal] = mapped_column(
        Numeric(46, 28),
        default=Decimal("0"),
    )
    realized_pnl: Mapped[Decimal] = mapped_column(
        Numeric(46, 28),
        default=Decimal("0"),
    )
    last_updated: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


async def lookup_paper_order_request(
    *,
    user_id: str,
    request_id: str,
    request_fingerprint: str,
):
    """Read a committed owner-scoped paper order."""
    from sqlalchemy import text as sql_text
    from backend.app.stacks.execution.paper_order_identity import (
        normalize_request_id,
        assert_matching_fingerprint,
    )
    import re

    owner = str(user_id).strip()
    if not owner:
        raise ValueError("Paper-order owner is required")

    request_id = normalize_request_id(request_id)

    if (
        not isinstance(request_fingerprint, str)
        or re.fullmatch(
            r"[0-9a-f]{64}",
            request_fingerprint,
        ) is None
    ):
        raise ValueError("Invalid paper-order fingerprint")

    async with async_session() as session:
        result = await session.execute(
            sql_text(
                "SELECT id, symbol, signal, status, "
                "request_fingerprint FROM order_history "
                "WHERE user_id = :owner "
                "AND request_id = :request_id"
            ),
            {
                "owner": owner,
                "request_id": request_id,
            },
        )
        existing = result.mappings().first()

    if existing is None:
        return None

    assert_matching_fingerprint(
        existing_fingerprint=existing["request_fingerprint"],
        incoming_fingerprint=request_fingerprint,
    )

    return {
        "replayed": True,
        "order_id": existing["id"],
        "status": existing["status"],
        "symbol": existing["symbol"],
        "signal": existing["signal"],
        "request_id": request_id,
    }


async def read_inventory_in_session(
    *,
    session,
    user_id: str,
) -> list[dict]:
    """
    Return owner-scoped, validated long inventory within
    the caller's existing transaction.

    Caller must hold the ledger serialization lock.
    Does not fetch quotes, commit, or authorize execution.
    """
    owner = str(user_id).strip() if isinstance(user_id, str) else ""
    if not owner:
        raise ValueError("inventory_owner_unavailable")

    if session is None or not callable(
        getattr(session, "execute", None)
    ):
        raise ValueError("inventory_session_unavailable")

    result = await session.execute(
        select(PortfolioInventory).where(
            PortfolioInventory.user_id == owner
        )
    )
    records = result.scalars().all()
    seen = set()
    positions = []

    for record in records:
        raw_symbol = getattr(record, "symbol", None)
        if not isinstance(raw_symbol, str):
            raise ValueError("inventory_symbol_invalid")

        symbol = raw_symbol.strip().upper()
        if not symbol or symbol in seen:
            raise ValueError("inventory_symbol_invalid_or_duplicate")
        seen.add(symbol)

        try:
            quantity = Decimal(str(record.shares_quantity))
            cost = Decimal(str(record.total_cost_basis))
            entry = Decimal(str(record.average_entry_price))
        except (AttributeError, TypeError, ValueError, ArithmeticError):
            raise ValueError("inventory_decimal_invalid") from None

        if (
            not quantity.is_finite()
            or not cost.is_finite()
            or not entry.is_finite()
            or quantity < 0
            or cost < 0
            or entry < 0
        ):
            raise ValueError("inventory_values_invalid")

        if quantity > 0 and entry <= 0:
            raise ValueError("inventory_entry_price_invalid")

        if quantity == 0 and cost != 0:
            raise ValueError("inventory_zero_quantity_with_cost")

        if quantity > 0 and cost <= 0:
            raise ValueError("inventory_positive_quantity_without_cost")

        if quantity == 0:
            continue

        positions.append({
            "symbol": symbol,
            "shares_quantity": str(quantity),
            "total_cost_basis": str(cost),
            "average_entry_price": str(entry),
        })

    return positions


async def save_log(
    trade_result: dict,
    *,
    user_id: str,
    trace_id: str | None = None,
    request_id: str | None = None,
    request_fingerprint: str | None = None,
):
    normalized_user_id = str(
        user_id
    ).strip()

    if not normalized_user_id:
        raise ValueError(
            "Ledger ownership user_id cannot be empty"
        )

    if not trade_result:
        return

    # Legacy calls without request identity retain existing behavior.
    # Keyed calls require both parts of the idempotency contract.
    keyed = (
        request_id is not None
        or request_fingerprint is not None
    )

    if keyed:
        from backend.app.stacks.execution.paper_order_identity import (
            normalize_request_id,
        )
        import re

        request_id = normalize_request_id(request_id)

        if (
            not isinstance(request_fingerprint, str)
            or re.fullmatch(
                r"[0-9a-f]{64}", request_fingerprint
            ) is None
        ):
            raise ValueError(
                "Valid paper-order request_fingerprint required"
            )

    symbol = trade_result.get("symbol", "UNKNOWN")
    status = trade_result.get("status", "UNKNOWN")

    # Executed fills MUST use one canonical status.
    # Reject alternate spellings and malformed forms before
    # any transaction or idempotency replay can proceed.
    if not isinstance(status, str) or not status.strip():
        raise ValueError("paper_trade_status_invalid")

    if status != "executed" and "executed" in status.casefold():
        raise ValueError("paper_executed_status_noncanonical")


    raw_signal = trade_result.get("signal", "UNKNOWN")
    signal_str = raw_signal.get("action", "UNKNOWN") if isinstance(raw_signal, dict) else str(raw_signal)

    allocated_capital = trade_result.get("allocated_capital")
    slippage_price = trade_result.get("slippage_price")
    commission_paid = trade_result.get("commission_paid")

    from sqlalchemy import text as sql_text
    from backend.app.stacks.execution.execution_control import (
        execution_control,
    )

    async with async_session() as session:
        async with session.begin():
            await session.execute(
                sql_text("SELECT pg_advisory_xact_lock(742618390125)")
            )
            execution_control.assert_paper_execution_allowed()

            if keyed:
                # The advisory transaction lock serializes keyed writes.
                # Missing migration columns raise a database error:
                # never silently fall back to an unprotected write.
                existing = (
                    await session.execute(
                        sql_text(
                            "SELECT id, symbol, signal, status, "
                            "request_fingerprint "
                            "FROM order_history "
                            "WHERE user_id = :owner "
                            "AND request_id = :request_id"
                        ),
                        {
                            "owner": normalized_user_id,
                            "request_id": request_id,
                        },
                    )
                ).mappings().first()

                if existing is not None:
                    from backend.app.stacks.execution.paper_order_identity import (
                        assert_matching_fingerprint,
                    )

                    assert_matching_fingerprint(
                        existing_fingerprint=existing[
                            "request_fingerprint"
                        ],
                        incoming_fingerprint=request_fingerprint,
                    )
                    return {
                        "replayed": True,
                        "order_id": existing["id"],
                        "status": existing["status"],
                        "symbol": existing["symbol"],
                        "signal": existing["signal"],
                        "request_id": request_id,
                    }

            # P0 authoritative account snapshot.
            # These reads share the session and advisory lock
            # used for order history and inventory writes.
            # Do not reopen an independent database session.
            if status == "executed":
                from backend.app.stacks.portfolio.accounting import (
                    calculate_cash_in_session,
                )

                authoritative_cash = await calculate_cash_in_session(
                    session=session,
                    user_id=normalized_user_id,
                )

                authoritative_inventory = await read_inventory_in_session(
                    session=session,
                    user_id=normalized_user_id,
                )

                if (
                    authoritative_cash.get("scope")
                    != "caller_database_session"
                    or authoritative_cash.get("user_id")
                    != normalized_user_id
                    or not isinstance(authoritative_inventory, list)
                ):
                    raise RuntimeError(
                        "paper_account_snapshot_unavailable"
                    )

                # Cash and positions alone do NOT establish
                # equity, quote freshness, account currency,
                # drawdown compliance, or execution permission.
                # The blockade below must remain until all
                # requirements are enforced in this transaction.

            # Read the persistent owner/account currency.
            # Neither ticker currency nor an assumed default can
            # establish the denomination of cash balances.
            if status == "executed":
                from datetime import datetime, timezone

                from backend.app.stacks.market_data.risk_valuation_quotes import (
                    get_risk_valuation_quote,
                )
                from backend.app.stacks.risk.transaction_equity import (
                    read_transaction_verified_equity,
                )

                currency_result = await session.execute(
                    sql_text(
                        "SELECT currency "
                        "FROM paper_equity_high_water "
                        "WHERE user_id = :owner "
                        "FOR UPDATE"
                    ),
                    {"owner": normalized_user_id},
                )

                currency_rows = currency_result.scalars().all()

                if len(currency_rows) != 1:
                    raise RuntimeError(
                        "paper_account_currency_unverified"
                    )

                account_currency = currency_rows[0]

                # Current yfinance quote paths generally lack
                # a genuine exchange observation timestamp.
                # The verifier must reject those quotes.
                from backend.app.stacks.risk.transaction_quote_cache import (
                    make_transaction_quote_loader,
                )

                # One source observation per symbol per transaction.
                # No global cache or reuse across orders.
                transaction_quote_loader = make_transaction_quote_loader(
                    get_risk_valuation_quote
                )

                transaction_valuation = (
                    await read_transaction_verified_equity(
                        session=session,
                        user_id=normalized_user_id,
                        cash_currency=account_currency,
                        quote_loader=transaction_quote_loader,
                        now=datetime.now(timezone.utc),
                    )
                )

                if (
                    transaction_valuation.get("status")
                    != "verified"
                    or transaction_valuation.get("owner")
                    != normalized_user_id
                    or transaction_valuation.get(
                        "execution_authorized"
                    ) is not False
                ):
                    raise RuntimeError(
                        "paper_transaction_valuation_unverified"
                    )

                # Verified valuation alone cannot grant an
                # execution. Persistent peak, actual limits,
                # fill-price and share checks still require
                # atomic enforcement. Blockade retained below.

            # P0 persistent financial policy.
            # Use ONLY explicitly configured server-side limits.
            # Missing or malformed configuration fails closed.
            #
            # This runs under the existing ledger advisory lock
            # and database transaction, after owner valuation.
            if status == "executed":
                import os

                from backend.app.stacks.risk.transactional_policy import (
                    evaluate_transactional_financial_policy,
                )

                limit_names = {
                    "max_order_value":
                        "NEUROVEST_PAPER_MAX_ORDER_VALUE",
                    "max_gross_exposure":
                        "NEUROVEST_PAPER_MAX_GROSS_EXPOSURE",
                    "max_drawdown_fraction":
                        "NEUROVEST_PAPER_MAX_DRAWDOWN_FRACTION",
                }

                configured_limits = {
                    key: os.environ.get(name)
                    for key, name in limit_names.items()
                }

                if any(
                    not isinstance(value, str)
                    or not value.strip()
                    for value in configured_limits.values()
                ):
                    raise RuntimeError(
                        "paper_financial_limits_unconfigured"
                    )

                action = signal_str.strip().lower()

                # Long is an opening buy. Short-selling remains
                # unsupported by the long-only financial policy.
                if action == "long":
                    action = "buy"

                if action not in ("buy", "sell"):
                    raise RuntimeError(
                        "paper_financial_action_unsupported"
                    )

                # P0: validate the proposed execution fill using
                # the owner-scoped inventory already read under
                # this transaction's ledger serialization lock.
                from backend.app.stacks.risk.transaction_fill import (
                    validate_transaction_fill,
                )

                configured_slippage_bps = os.environ.get(
                    "NEUROVEST_PAPER_MAX_SLIPPAGE_BPS"
                )

                if (
                    not isinstance(configured_slippage_bps, str)
                    or not configured_slippage_bps.strip()
                ):
                    raise RuntimeError(
                        "paper_slippage_limit_unconfigured"
                    )

                execution_quote = await transaction_quote_loader(
                    symbol
                )

                transaction_fill_decision = validate_transaction_fill(
                    symbol=symbol,
                    action=action,
                    allocated_capital=allocated_capital,
                    fill_price=slippage_price,
                    commission=commission_paid,
                    account_currency=account_currency,
                    execution_quote=execution_quote,
                    positions=authoritative_inventory,
                    now=datetime.now(timezone.utc),
                    max_slippage_bps=configured_slippage_bps,
                )

                if (
                    transaction_fill_decision.get("status")
                    != "validated"
                    or transaction_fill_decision.get(
                        "execution_authorized"
                    ) is not False
                ):
                    raise RuntimeError(
                        "paper_transaction_fill_unverified"
                    )

                # Advisory only. The unconditional executed-order
                # blockade below remains authoritative.

                transaction_risk_decision = (
                    await evaluate_transactional_financial_policy(
                        session=session,
                        owner=normalized_user_id,
                        currency=account_currency,
                        action=action,
                        order_value=allocated_capital,
                        commission=commission_paid,
                        verified_equity=transaction_valuation,
                        limits=configured_limits,
                    )
                )

                if (
                    transaction_risk_decision.get("approved")
                    is not True
                ):
                    raise RuntimeError(
                        "paper_financial_policy_rejected"
                    )

                if (
                    transaction_risk_decision.get(
                        "execution_authorized"
                    ) is not False
                ):
                    raise RuntimeError(
                        "paper_financial_policy_contract_invalid"
                    )

                # A positive risk decision is NOT permission
                # to execute. The unconditional blockade
                # immediately below remains authoritative.

            if status == "executed":
                from backend.app.stacks.risk.final_transaction_quote_freshness import (
                    validate_final_transaction_quote_freshness,
                )

                # Recheck original observations after awaited
                # financial-policy work. No timestamp renewal.
                final_quote_decision = (
                    validate_final_transaction_quote_freshness(
                        positions=authoritative_inventory,
                        marks=transaction_valuation["marks"],
                        execution_quote=execution_quote,
                        symbol=symbol,
                        account_currency=account_currency,
                        now=datetime.now(timezone.utc),
                    )
                )

                if (
                    final_quote_decision.get("status") != "validated"
                    or final_quote_decision.get(
                        "execution_authorized"
                    ) is not False
                ):
                    raise RuntimeError(
                        "paper_final_quote_freshness_unverified"
                    )

            # P0 FINANCIAL COMMIT GATE — fail closed.
            # The legacy pre-transaction cash/drawdown checks
            # do not qualify as atomic financial authorization.
            #
            # This deliberate temporary blockade must be
            # replaced by transaction-consistent valuation,
            # persistent high-water evaluation, and verified
            # exposure/price policy BEFORE production rollout.
            #
            # Idempotent replay above remains available.
            if status == "executed":
                raise RuntimeError(
                    "paper_execution_financial_risk_not_qualified"
                )

            new_order = OrderHistory(
                user_id=normalized_user_id,
                symbol=symbol,
                signal=signal_str,
                status=status,
                allocated_capital=allocated_capital,
                slippage_price=slippage_price,
                commission_paid=commission_paid,
            )
            session.add(new_order)

            if status == "executed":
                signal_action = signal_str.strip().lower()

                if signal_action not in (
                    "buy",
                    "long",
                    "sell",
                    "short",
                ):
                    raise ValueError(
                        "Unsupported executed trade action"
                    )

                if allocated_capital is None or slippage_price is None:
                    raise ValueError(
                        "Executed trade requires capital and fill price"
                    )

                allocated_value = Decimal(str(allocated_capital))
                fill_price_value = Decimal(str(slippage_price))

                if (
                    not allocated_value.is_finite()
                    or not fill_price_value.is_finite()
                    or allocated_value <= 0
                    or fill_price_value <= 0
                ):
                    raise ValueError(
                        "Executed trade requires positive finite "
                        "capital and fill price"
                    )

                stmt = select(
                    PortfolioInventory
                ).where(
                    PortfolioInventory.user_id
                    == normalized_user_id,
                    PortfolioInventory.symbol
                    == symbol,
                )
                res = await session.execute(stmt)
                position = res.scalar()

                allocated_capital_decimal = Decimal(
                    str(allocated_capital)
                )
                slippage_price_decimal = Decimal(
                    str(slippage_price)
                )

                if slippage_price_decimal == 0:
                    raise ValueError(
                        "slippage_price cannot be zero"
                    )

                shares_filled = (
                    allocated_capital_decimal
                    /
                    slippage_price_decimal
                )

                if signal_action in ("sell", "short"):
                    if position is None:
                        raise ValueError(
                            "Cannot sell without an existing position"
                        )

                    if position.shares_quantity < shares_filled:
                        raise ValueError(
                            "Sell quantity exceeds available shares"
                        )

                if not position:
                    position = PortfolioInventory(
                        user_id=normalized_user_id,
                        symbol=symbol,
                        shares_quantity=shares_filled,
                        average_entry_price=(
                            slippage_price_decimal
                        ),
                        total_cost_basis=(
                            allocated_capital_decimal
                        ),
                    )
                    session.add(position)
                else:
                    if signal_str.lower() in ["buy", "long"]:
                        new_total_capital = (
                            position.total_cost_basis
                            +
                            allocated_capital_decimal
                        )
                        new_total_shares = (
                            position.shares_quantity
                            +
                            shares_filled
                        )
                        position.shares_quantity = new_total_shares
                        position.total_cost_basis = new_total_capital
                        position.average_entry_price = new_total_capital / new_total_shares
                    elif signal_str.lower() in ["sell", "short"]:
                        # Calculate profit differences based on entry pricing vs current slippage fill prices
                        pnl_delta = (
                            shares_filled
                            *
                            (
                                slippage_price_decimal
                                -
                                position.average_entry_price
                            )
                        )
                        position.realized_pnl = (
                            position.realized_pnl
                            +
                            pnl_delta
                        )

                        position.shares_quantity = max(
                            Decimal("0"),
                            position.shares_quantity
                            -
                            shares_filled,
                        )
                        position.total_cost_basis = (
                            position.shares_quantity
                            *
                            position.average_entry_price
                        )

            # Flush pending rows within the open database transaction.
            # Flush is not a commit.
            await session.flush()

            if keyed:
                # Persist identity inside the same transaction as
                # the history row and inventory mutation.
                await session.execute(
                    sql_text(
                        "UPDATE order_history SET "
                        "request_id = :request_id, "
                        "request_fingerprint = :fingerprint "
                        "WHERE id = :order_id "
                        "AND user_id = :owner"
                    ),
                    {
                        "request_id": request_id,
                        "fingerprint": request_fingerprint,
                        "order_id": new_order.id,
                        "owner": normalized_user_id,
                    },
                )

            # Recheck operating mode after all awaited inventory work.
            # An activated stop rolls back this still-open transaction.
            # This narrows, but does not eliminate, the commit race.
            execution_control.assert_paper_execution_allowed()
    if trace_id:
        from backend.app.core.runtime_trace import emit_runtime_step

        await emit_runtime_step(
            trace_id=trace_id,
            event_type="LEDGER_WRITE_COMPLETE",
            node="journal_ledger",
            source="execution",
            destination="journal_ledger",
            status="completed",
            symbol=symbol,
            message="Order history and portfolio inventory transaction committed",
            layer="L2",
            stack="journal_ledger",
            details={
                "signal": signal_str,
                "trade_status": status,
                "ownership_scope":
                    "authenticated_account",
            },
        )

        await emit_runtime_step(
            trace_id=trace_id,
            event_type="PORTFOLIO_INVENTORY_UPDATED",
            node="portfolio_accounting",
            source="journal_ledger",
            destination="portfolio_accounting",
            status="completed",
            symbol=symbol,
            message="Portfolio inventory update completed",
            layer="L2",
            stack="portfolio",
        )

    print(f"Database Log & Inventory Saved: {symbol} - {signal_str} - {status}")

    if keyed:
        return {
            "replayed": False,
            "order_id": new_order.id,
            "status": status,
            "symbol": symbol,
            "signal": signal_str,
            "request_id": request_id,
        }

def _normalize_portfolio_read_user_id(
    user_id: str,
) -> str:
    normalized_user_id = str(
        user_id
    ).strip()

    if not normalized_user_id:
        raise ValueError(
            "Authenticated portfolio user_id cannot be empty"
        )

    return normalized_user_id



async def read_portfolio_positions(
    *,
    user_id: str,
) -> list[dict[str, str]]:
    normalized_user_id = _normalize_portfolio_read_user_id(
        user_id
    )

    async with async_session() as session:
        result = await session.execute(
            select(PortfolioInventory)
            .where(
                PortfolioInventory.user_id
                == normalized_user_id
            )
            .order_by(PortfolioInventory.symbol)
        )
        positions = result.scalars().all()

    return [
        {
            "symbol": str(position.symbol),
            "shares_quantity": str(
                position.shares_quantity
            ),
            "average_entry_price": str(
                position.average_entry_price
            ),
            "total_cost_basis": str(
                position.total_cost_basis
            ),
            "realized_pnl": str(
                position.realized_pnl
            ),
        }
        for position in positions
    ]


async def read_max_allocated_capital(
    *,
    user_id: str,
) -> float | None:
    normalized_user_id = (
        _normalize_portfolio_read_user_id(
            user_id
        )
    )

    """
    Return the highest allocated capital through a
    journal-ledger-owned read-only query boundary.

    Consumers receive only a scalar value. Database
    sessions, ORM models, transactions, and mutation
    capabilities remain internal to journal_ledger.
    """

    async with async_session() as session:
        result = await session.execute(
            select(
                    func.max(
                        OrderHistory.allocated_capital
                    )
                ).where(
                    OrderHistory.user_id
                    == normalized_user_id
                )
        )

        value = result.scalar_one_or_none()

    if value is None:
        return None

    return float(value)
