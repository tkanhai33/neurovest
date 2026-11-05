from __future__ import annotations

import asyncio
import hashlib

from datetime import (
    UTC,
    datetime,
)
from decimal import (
    Decimal,
    InvalidOperation,
)
from typing import (
    Any,
    Callable,
)

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.stacks.portfolio.read_models.readonly_portfolio_snapshot import (
    READONLY_PORTFOLIO_SCHEMA,
    READONLY_PORTFOLIO_SCHEMA_VERSION,
    ReadOnlyBalance,
    ReadOnlyPortfolioAccount,
    ReadOnlyPortfolioSnapshot,
    ReadOnlyPortfolioTotals,
    ReadOnlyPosition,
)

from backend.app.stacks.snaptrade.adapters.sdk_client_factory import (
    build_snaptrade_sdk_client,
)

from backend.app.stacks.snaptrade.persistence.credential_repository import (
    SnapTradeCredentialRepository,
)


class SnapTradeLivePortfolioSnapshotError(
    RuntimeError
):
    pass


def _unwrap(
    value: Any,
) -> Any:

    if hasattr(
        value,
        "actual_instance",
    ):
        return _unwrap(
            value.actual_instance
        )

    return value


def _extract(
    value: Any,
    *names: str,
) -> Any:

    value = _unwrap(
        value
    )

    if value is None:
        return None

    if isinstance(
        value,
        dict,
    ):

        for name in names:

            if name in value:
                return value[
                    name
                ]

    for container_name in (
        "parsed",
        "body",
        "data",
        "additional_properties",
    ):

        nested = getattr(
            value,
            container_name,
            None,
        )

        if (
            nested is not None
            and
            nested is not value
        ):

            found = _extract(
                nested,
                *names,
            )

            if found is not None:
                return found

    for name in names:

        try:
            found = getattr(
                value,
                name,
            )

        except Exception:
            continue

        if found is not None:
            return found

    return None


def _items(
    response: Any,
    *keys: str,
) -> list[Any]:

    value = _unwrap(
        response
    )

    for name in (
        "parsed",
        "body",
        "data",
    ):

        nested = getattr(
            value,
            name,
            None,
        )

        if nested is not None:
            value = _unwrap(
                nested
            )
            break

    if value is None:
        return []

    if isinstance(
        value,
        list,
    ):
        return value

    if isinstance(
        value,
        tuple,
    ):
        return list(
            value
        )

    if isinstance(
        value,
        dict,
    ):

        for key in (
            *keys,
            "results",
            "data",
        ):

            candidate = value.get(
                key
            )

            if isinstance(
                candidate,
                list,
            ):
                return candidate

        return []

    try:

        if not isinstance(
            value,
            (
                str,
                bytes,
            ),
        ):
            return list(
                value
            )

    except TypeError:
        pass

    return []


def _decimal(
    value: Any,
    *,
    label: str,
    required: bool = True,
) -> Decimal | None:

    if value is None:

        if required:
            raise SnapTradeLivePortfolioSnapshotError(
                f"{label} is required."
            )

        return None

    if isinstance(
        value,
        bool,
    ):
        raise SnapTradeLivePortfolioSnapshotError(
            f"{label} cannot be boolean."
        )

    try:

        result = Decimal(
            str(
                value
            ).strip()
        )

    except (
        InvalidOperation,
        ValueError,
    ) as exc:

        raise SnapTradeLivePortfolioSnapshotError(
            f"{label} is not numeric."
        ) from exc

    if not result.is_finite():
        raise SnapTradeLivePortfolioSnapshotError(
            f"{label} must be finite."
        )

    return result


def _text(
    value: Any,
    *,
    label: str,
    required: bool = True,
) -> str | None:

    if value is None:

        if required:
            raise SnapTradeLivePortfolioSnapshotError(
                f"{label} is required."
            )

        return None

    rendered = str(
        value
    ).strip()

    if not rendered:

        if required:
            raise SnapTradeLivePortfolioSnapshotError(
                f"{label} is required."
            )

        return None

    return rendered


def _hash(
    value: str,
) -> str:

    return hashlib.sha256(
        value.encode(
            "utf-8"
        )
    ).hexdigest()


def _normalize_balance(
    raw: Any,
) -> ReadOnlyBalance:

    currency_raw = _extract(
        raw,
        "currency",
    )

    currency = (
        _extract(
            currency_raw,
            "code",
        )
        or
        currency_raw
    )

    return ReadOnlyBalance(
        currency=_text(
            currency,
            label="balance.currency",
            required=False,
        ),
        cash_amount=_decimal(
            _extract(
                raw,
                "cash",
            ),
            label="balance.cash",
            required=False,
        ),
        buying_power=_decimal(
            _extract(
                raw,
                "buying_power",
                "buyingPower",
            ),
            label="balance.buying_power",
            required=False,
        ),
        cash_available=None,
        settled_cash=None,
    )


def _normalize_position(
    raw: Any,
    *,
    account_id: str,
) -> ReadOnlyPosition:

    instrument = _extract(
        raw,
        "instrument",
    )

    if instrument is None:
        raise SnapTradeLivePortfolioSnapshotError(
            "Position instrument is required."
        )

    symbol = _text(
        _extract(
            instrument,
            "symbol",
        ),
        label="position.symbol",
    ).upper()

    quantity = _decimal(
        _extract(
            raw,
            "units",
        ),
        label="position.units",
    )

    price = _decimal(
        _extract(
            raw,
            "price",
        ),
        label="position.price",
    )

    average_entry = _decimal(
        _extract(
            raw,
            "cost_basis",
            "costBasis",
        ),
        label="position.cost_basis",
    )

    if quantity < 0:
        raise SnapTradeLivePortfolioSnapshotError(
            "Negative quantity is unsupported."
        )

    if price < 0:
        raise SnapTradeLivePortfolioSnapshotError(
            "Negative market price is invalid."
        )

    if average_entry < 0:
        raise SnapTradeLivePortfolioSnapshotError(
            "Negative average entry price is invalid."
        )

    total_cost_basis = (
        quantity
        *
        average_entry
    )

    market_value = (
        quantity
        *
        price
    )

    unrealized_gain = (
        market_value
        -
        total_cost_basis
    )

    provider_position_id = (
        _extract(
            instrument,
            "id",
        )
        or
        symbol
    )

    currency = _text(
        _extract(
            raw,
            "currency",
        ),
        label="position.currency",
        required=False,
    )

    instrument_kind = _text(
        _extract(
            instrument,
            "kind",
        ),
        label="position.instrument.kind",
        required=False,
    )

    return ReadOnlyPosition(
        position_id_hash=_hash(
            (
                account_id
                +
                ":"
                +
                str(
                    provider_position_id
                )
            )
        ),
        symbol=symbol,
        instrument_kind=instrument_kind,
        currency=currency,
        quantity=quantity,
        average_entry_price=(
            average_entry
        ),
        current_price=price,
        market_value=market_value,
        market_value_source=(
            "snaptrade_price_times_units"
        ),
        cost_basis=total_cost_basis,
        cost_basis_source=(
            "snaptrade_units_times_book_price"
        ),
        unrealized_gain=(
            unrealized_gain
        ),
        unrealized_gain_source=(
            "market_value_minus_total_cost_basis"
        ),
        source_provider=(
            "snaptrade"
        ),
        read_only=True,
    )


def build_live_readonly_snapshot(
    *,
    accounts: list[Any],
    positions_by_account: dict[
        str,
        list[Any],
    ],
    balances_by_account: dict[
        str,
        list[Any],
    ],
    network_request_count: int,
) -> ReadOnlyPortfolioSnapshot:

    normalized_accounts = []

    for raw_account in accounts:

        account_id = _text(
            _extract(
                raw_account,
                "id",
            ),
            label="account.id",
        )

        status = _text(
            _extract(
                raw_account,
                "status",
            ),
            label="account.status",
            required=False,
        )

        if (
            status
            and
            status.lower()
            ==
            "closed"
        ):
            continue

        positions = tuple(
            _normalize_position(
                item,
                account_id=(
                    account_id
                ),
            )
            for item
            in positions_by_account.get(
                account_id,
                [],
            )
        )

        balances = tuple(
            _normalize_balance(
                item
            )
            for item
            in balances_by_account.get(
                account_id,
                [],
            )
        )

        cash_values = [
            item.cash_amount
            for item in balances
            if item.cash_amount
            is not None
        ]

        cash_total = (
            sum(
                cash_values,
                Decimal(
                    "0"
                ),
            )
            if cash_values
            else None
        )

        market_value_total = sum(
            (
                item.market_value
                or
                Decimal(
                    "0"
                )
            )
            for item in positions
        )

        cost_basis_total = sum(
            (
                item.cost_basis
                or
                Decimal(
                    "0"
                )
            )
            for item in positions
        )

        unrealized_gain_total = sum(
            (
                item.unrealized_gain
                or
                Decimal(
                    "0"
                )
            )
            for item in positions
        )

        normalized_accounts.append(
            ReadOnlyPortfolioAccount(
                account_id_hash=_hash(
                    account_id
                ),
                institution_name=_text(
                    _extract(
                        raw_account,
                        "institution_name",
                        "institutionName",
                    ),
                    label="account.institution_name",
                    required=False,
                ),
                account_category=_text(
                    _extract(
                        raw_account,
                        "name",
                    ),
                    label="account.name",
                    required=False,
                ),
                is_paper=False,
                source_provider=(
                    "snaptrade"
                ),
                read_only=True,
                cash_total=(
                    cash_total
                ),
                market_value_total=(
                    market_value_total
                ),
                cost_basis_total=(
                    cost_basis_total
                ),
                unrealized_gain_total=(
                    unrealized_gain_total
                ),
                balances=balances,
                positions=positions,
            )
        )

    account_tuple = tuple(
        normalized_accounts
    )

    all_positions = tuple(
        position
        for account in account_tuple
        for position in account.positions
    )

    all_balances = tuple(
        balance
        for account in account_tuple
        for balance in account.balances
    )

    symbols = tuple(
        sorted(
            {
                position.symbol
                for position
                in all_positions
            }
        )
    )

    instrument_kinds = tuple(
        sorted(
            {
                position.instrument_kind
                for position
                in all_positions
                if position.instrument_kind
                is not None
            }
        )
    )

    currencies = tuple(
        sorted(
            {
                value
                for value in (
                    *(
                        position.currency
                        for position
                        in all_positions
                    ),
                    *(
                        balance.currency
                        for balance
                        in all_balances
                    ),
                )
                if value is not None
            }
        )
    )

    cash_total = sum(
        (
            account.cash_total
            or
            Decimal(
                "0"
            )
        )
        for account
        in account_tuple
    )

    market_value_total = sum(
        (
            account.market_value_total
            or
            Decimal(
                "0"
            )
        )
        for account
        in account_tuple
    )

    cost_basis_total = sum(
        (
            account.cost_basis_total
            or
            Decimal(
                "0"
            )
        )
        for account
        in account_tuple
    )

    unrealized_gain_total = sum(
        (
            account.unrealized_gain_total
            or
            Decimal(
                "0"
            )
        )
        for account
        in account_tuple
    )

    return ReadOnlyPortfolioSnapshot(
        schema=(
            READONLY_PORTFOLIO_SCHEMA
        ),
        schema_version=(
            READONLY_PORTFOLIO_SCHEMA_VERSION
        ),
        snapshot_type=(
            "snaptrade_live_readonly"
        ),
        generated_at=(
            datetime.now(
                UTC
            ).isoformat()
        ),
        source_provider=(
            "snaptrade"
        ),
        source_environment=(
            "external_readonly"
        ),
        read_only=True,
        paper_only=False,
        trading_enabled=False,
        order_operations_enabled=False,
        database_persisted=False,
        network_request_count=(
            int(
                network_request_count
            )
        ),
        account_count=(
            len(
                account_tuple
            )
        ),
        balance_record_count=(
            len(
                all_balances
            )
        ),
        position_count=(
            len(
                all_positions
            )
        ),
        symbols=symbols,
        instrument_kinds=(
            instrument_kinds
        ),
        currencies=currencies,
        totals=ReadOnlyPortfolioTotals(
            cash=cash_total,
            market_value=(
                market_value_total
            ),
            cost_basis=(
                cost_basis_total
            ),
            unrealized_gain=(
                unrealized_gain_total
            ),
            market_value_complete=True,
            cost_basis_complete=True,
            unrealized_gain_complete=True,
        ),
        calculated_fields={
            "account_count":
                len(
                    account_tuple
                ),

            "position_count":
                len(
                    all_positions
                ),

            "balance_record_count":
                len(
                    all_balances
                ),
        },
        source_evidence={},
        accounts=account_tuple,
    )


class SnapTradeLivePortfolioSnapshotService:

    def __init__(
        self,
        session: AsyncSession,
        *,
        client_factory: Callable[
            [],
            Any,
        ] = build_snaptrade_sdk_client,
    ) -> None:

        self._credentials = (
            SnapTradeCredentialRepository(
                session
            )
        )

        self._client_factory = (
            client_factory
        )


    async def fetch_snapshot(
        self,
        *,
        neurovest_user_id: str,
    ) -> ReadOnlyPortfolioSnapshot:

        owner = str(
            neurovest_user_id
        ).strip()

        if not owner:
            raise SnapTradeLivePortfolioSnapshotError(
                "Authenticated NeuroVest owner is required."
            )

        try:

            (
                provider_user,
                user_secret,
            ) = (
                await self._credentials
                .load_provider_identity(
                    neurovest_user_id=owner
                )
            )

        except LookupError as exc:

            raise SnapTradeLivePortfolioSnapshotError(
                "SnapTrade registration is required."
            ) from exc

        client = (
            self._client_factory()
        )

        account_response = (
            await asyncio.to_thread(
                client.list_user_accounts,
                user_id=provider_user,
                user_secret=user_secret,
            )
        )

        request_count = 1

        accounts = _items(
            account_response,
            "accounts",
        )

        positions_by_account = {}
        balances_by_account = {}

        for account in accounts:

            account_id = _text(
                _extract(
                    account,
                    "id",
                ),
                label="account.id",
            )

            status = _text(
                _extract(
                    account,
                    "status",
                ),
                label="account.status",
                required=False,
            )

            if (
                status
                and
                status.lower()
                ==
                "closed"
            ):
                continue

            position_response = (
                await asyncio.to_thread(
                    client
                    .get_all_account_positions,
                    account_id=(
                        account_id
                    ),
                    user_id=provider_user,
                    user_secret=user_secret,
                )
            )

            request_count += 1

            balance_response = (
                await asyncio.to_thread(
                    client
                    .get_user_account_balance,
                    account_id=(
                        account_id
                    ),
                    user_id=provider_user,
                    user_secret=user_secret,
                )
            )

            request_count += 1

            positions_by_account[
                account_id
            ] = _items(
                position_response,
                "positions",
            )

            balances_by_account[
                account_id
            ] = _items(
                balance_response,
                "balances",
            )

        return build_live_readonly_snapshot(
            accounts=accounts,
            positions_by_account=(
                positions_by_account
            ),
            balances_by_account=(
                balances_by_account
            ),
            network_request_count=(
                request_count
            ),
        )
