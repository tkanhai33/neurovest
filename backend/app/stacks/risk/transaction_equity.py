from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any, Callable, Awaitable

from backend.app.stacks.portfolio.accounting import (
    calculate_cash_in_session,
)
from backend.app.stacks.journal_ledger.ledger import (
    read_inventory_in_session,
)
from backend.app.stacks.risk.portfolio_equity import (
    verify_portfolio_equity,
)


class TransactionEquityUnavailable(RuntimeError):
    pass


async def read_transaction_verified_equity(
    *,
    session: Any,
    user_id: str,
    cash_currency: str,
    quote_loader: Callable[[str], Awaitable[Mapping]],
    now: datetime,
    max_quote_age_seconds: int = 300,
) -> dict:
    """
    Assemble owner cash and inventory in the caller's transaction.

    Requires the caller to hold the ledger serialization lock.
    Quote timestamps must be genuine source observations.

    Never creates a session, commits, or authorizes orders.
    """
    if not isinstance(user_id, str) or not user_id.strip():
        raise TransactionEquityUnavailable("owner_unavailable")

    if (
        session is None
        or not callable(getattr(session, "in_transaction", None))
        or not session.in_transaction()
    ):
        raise TransactionEquityUnavailable("transaction_required")

    if (
        not isinstance(cash_currency, str)
        or len(cash_currency) != 3
        or not cash_currency.isascii()
        or not cash_currency.isalpha()
        or cash_currency != cash_currency.upper()
    ):
        raise TransactionEquityUnavailable("currency_unverified")

    if not callable(quote_loader):
        raise TransactionEquityUnavailable("quote_loader_unavailable")

    owner = user_id.strip()

    cash = await calculate_cash_in_session(
        session=session,
        user_id=owner,
    )

    if cash.get("scope") != "caller_database_session":
        raise TransactionEquityUnavailable("cash_scope_invalid")

    if cash.get("user_id") != owner:
        raise TransactionEquityUnavailable("cash_owner_mismatch")

    positions = await read_inventory_in_session(
        session=session,
        user_id=owner,
    )

    if not isinstance(positions, list):
        raise TransactionEquityUnavailable("inventory_invalid")

    quotes = {}
    for position in positions:
        symbol = position["symbol"]
        if symbol in quotes:
            raise TransactionEquityUnavailable("duplicate_symbol")

        quote = await quote_loader(symbol)

        if not isinstance(quote, Mapping):
            raise TransactionEquityUnavailable("quote_unavailable")

        # Do not supply missing timestamp, currency or price.
        quotes[symbol] = dict(quote)

    valuation = verify_portfolio_equity(
        cash=cash["current_cash_balance"],
        currency=cash_currency,
        positions=positions,
        quotes=quotes,
        now=now,
        max_quote_age_seconds=max_quote_age_seconds,
    )

    if not isinstance(valuation, dict):
        raise TransactionEquityUnavailable("valuation_invalid")

    if valuation.get("status") != "verified":
        raise TransactionEquityUnavailable("valuation_not_verified")

    return {
        **valuation,
        "owner": owner,
        "valuation_scope": "owner_scoped_caller_transaction",
        "cash_source": "executed_order_history",
        "inventory_source": "portfolio_inventory",
        "execution_authorized": False,
        "transaction_consistent": False,
    }
