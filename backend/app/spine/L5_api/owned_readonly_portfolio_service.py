from __future__ import annotations

from dataclasses import (
    asdict,
    replace,
)
from decimal import Decimal
from pathlib import Path
from typing import Any

from backend.app.stacks.portfolio.facades.readonly_portfolio_facade import (
    ReadOnlyPortfolioFacade,
    ReadOnlyPortfolioFacadeError,
)

from backend.app.stacks.portfolio.read_models.readonly_portfolio_snapshot import (
    ReadOnlyPortfolioSnapshot,
    ReadOnlyPortfolioTotals,
)

from backend.app.stacks.snaptrade.application.normalized_portfolio_ingestion import (
    ingest_normalized_portfolio,
)

from backend.app.stacks.snaptrade.application.portfolio_owner_binding import (
    DEFAULT_OWNER_BINDING_REGISTRY,
    PortfolioOwnerBindingError,
    PortfolioOwnerBindingNotFound,
    filter_owned_accounts,
)


class AuthenticatedPortfolioAccessDenied(
    PermissionError
):
    pass


class AuthenticatedPortfolioUnavailable(
    RuntimeError
):
    pass


def find_latest_normalized_portfolio() -> Path:
    candidates = sorted(
        Path(
            "runtime/snaptrade_integration"
        ).glob(
            (
                "portfolio_normalization_*/"
                "neurovest_snaptrade_portfolio_normalized.json"
            )
        ),
        key=lambda path:
            path.stat().st_mtime,
    )

    if not candidates:
        raise AuthenticatedPortfolioUnavailable(
            "No qualified normalized portfolio snapshot exists."
        )

    return candidates[-1]


def _sum_optional(
    values: list[
        Decimal | None
    ],
) -> tuple[
    Decimal | None,
    bool,
]:
    complete = all(
        value is not None
        for value in values
    )

    if not complete:
        return (
            None,
            False,
        )

    return (
        sum(
            (
                value
                for value in values
                if value is not None
            ),
            Decimal("0"),
        ),
        True,
    )


def build_owned_snapshot(
    *,
    neurovest_user_id: str,
    source_path: Path | str | None = None,
    registry_path: Path | str = (
        DEFAULT_OWNER_BINDING_REGISTRY
    ),
) -> ReadOnlyPortfolioSnapshot:
    normalized_user_id = str(
        neurovest_user_id
    ).strip()

    if not normalized_user_id:
        raise AuthenticatedPortfolioAccessDenied(
            "Authenticated principal subject is missing."
        )

    path = (
        Path(
            source_path
        )
        if source_path is not None
        else find_latest_normalized_portfolio()
    )

    snapshot = ingest_normalized_portfolio(
        path
    )

    available_hashes = tuple(
        account.account_id_hash
        for account in snapshot.accounts
    )

    try:
        owned_hashes = set(
            filter_owned_accounts(
                neurovest_user_id=(
                    normalized_user_id
                ),
                available_account_hashes=(
                    available_hashes
                ),
                registry_path=(
                    registry_path
                ),
            )
        )
    except PortfolioOwnerBindingNotFound as error:
        raise AuthenticatedPortfolioAccessDenied(
            "No portfolio is bound to the authenticated user."
        ) from error
    except PortfolioOwnerBindingError as error:
        raise AuthenticatedPortfolioUnavailable(
            "Portfolio ownership configuration is invalid."
        ) from error

    owned_accounts = tuple(
        account
        for account in snapshot.accounts
        if account.account_id_hash
        in owned_hashes
    )

    if not owned_accounts:
        raise AuthenticatedPortfolioAccessDenied(
            "The authenticated user owns no qualified portfolio accounts."
        )

    balance_count = sum(
        len(
            account.balances
        )
        for account in owned_accounts
    )

    position_count = sum(
        len(
            account.positions
        )
        for account in owned_accounts
    )

    symbols = tuple(
        sorted(
            {
                position.symbol
                for account in owned_accounts
                for position in account.positions
            }
        )
    )

    currencies = tuple(
        sorted(
            {
                currency
                for account in owned_accounts
                for currency in (
                    *(
                        balance.currency
                        for balance
                        in account.balances
                    ),
                    *(
                        position.currency
                        for position
                        in account.positions
                    ),
                )
                if currency
            }
        )
    )

    instrument_kinds = tuple(
        sorted(
            {
                position.instrument_kind
                for account in owned_accounts
                for position in account.positions
                if position.instrument_kind
            }
        )
    )

    cash, cash_complete = _sum_optional(
        [
            account.cash_total
            for account in owned_accounts
        ]
    )

    market_value, market_complete = (
        _sum_optional(
            [
                account.market_value_total
                for account in owned_accounts
            ]
        )
    )

    cost_basis, cost_complete = (
        _sum_optional(
            [
                account.cost_basis_total
                for account in owned_accounts
            ]
        )
    )

    unrealized, unrealized_complete = (
        _sum_optional(
            [
                account.unrealized_gain_total
                for account in owned_accounts
            ]
        )
    )

    totals = ReadOnlyPortfolioTotals(
        cash=(
            cash
            if cash_complete
            else None
        ),
        market_value=market_value,
        cost_basis=cost_basis,
        unrealized_gain=unrealized,
        market_value_complete=market_complete,
        cost_basis_complete=cost_complete,
        unrealized_gain_complete=(
            unrealized_complete
        ),
    )

    return replace(
        snapshot,
        account_count=len(
            owned_accounts
        ),
        balance_record_count=(
            balance_count
        ),
        position_count=position_count,
        symbols=symbols,
        currencies=currencies,
        instrument_kinds=(
            instrument_kinds
        ),
        totals=totals,
        accounts=owned_accounts,
    )


def build_owned_facade(
    *,
    neurovest_user_id: str,
    source_path: Path | str | None = None,
    registry_path: Path | str = (
        DEFAULT_OWNER_BINDING_REGISTRY
    ),
) -> ReadOnlyPortfolioFacade:
    return ReadOnlyPortfolioFacade(
        build_owned_snapshot(
            neurovest_user_id=(
                neurovest_user_id
            ),
            source_path=source_path,
            registry_path=registry_path,
        )
    )


def _json_safe(
    value: Any,
) -> Any:
    if isinstance(
        value,
        Decimal,
    ):
        return format(
            value,
            "f",
        )

    if isinstance(
        value,
        dict,
    ):
        return {
            str(key):
                _json_safe(
                    item
                )
            for key, item
            in value.items()
        }

    if isinstance(
        value,
        (
            list,
            tuple,
        ),
    ):
        return [
            _json_safe(
                item
            )
            for item in value
        ]

    return value


def serialize_overview(
    facade: ReadOnlyPortfolioFacade,
) -> dict[str, Any]:
    return _json_safe(
        asdict(
            facade.get_overview()
        )
    )


def serialize_accounts(
    facade: ReadOnlyPortfolioFacade,
) -> list[dict[str, Any]]:
    return [
        _json_safe(
            asdict(
                account
            )
        )
        for account in facade.list_accounts()
    ]


def serialize_positions(
    facade: ReadOnlyPortfolioFacade,
) -> list[dict[str, Any]]:
    return [
        _json_safe(
            asdict(
                item
            )
        )
        for item in facade.list_positions()
    ]


def serialize_symbol_positions(
    facade: ReadOnlyPortfolioFacade,
    symbol: str,
) -> list[dict[str, Any]]:
    return [
        _json_safe(
            asdict(
                item
            )
        )
        for item in facade.find_positions_by_symbol(
            symbol
        )
    ]


def serialize_balances(
    facade: ReadOnlyPortfolioFacade,
) -> list[dict[str, Any]]:
    return [
        {
            "account_id_hash":
                account_id_hash,
            "balance":
                _json_safe(
                    asdict(
                        balance
                    )
                ),
        }
        for account_id_hash, balance
        in facade.list_balances()
    ]


def serialize_totals(
    facade: ReadOnlyPortfolioFacade,
) -> dict[str, Any]:
    return _json_safe(
        asdict(
            facade.get_totals()
        )
    )
