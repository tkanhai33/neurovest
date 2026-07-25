from __future__ import annotations

import json
from decimal import (
    Decimal,
    InvalidOperation,
)
from pathlib import Path
from typing import Any

from backend.app.stacks.portfolio.read_models.readonly_portfolio_snapshot import (
    READONLY_PORTFOLIO_SCHEMA,
    READONLY_PORTFOLIO_SCHEMA_VERSION,
    ReadOnlyBalance,
    ReadOnlyPortfolioAccount,
    ReadOnlyPortfolioSnapshot,
    ReadOnlyPortfolioTotals,
    ReadOnlyPosition,
)


class ReadOnlyPortfolioIngestionError(
    ValueError
):
    pass


def _require_mapping(
    value: Any,
    *,
    label: str,
) -> dict[str, Any]:
    if not isinstance(
        value,
        dict,
    ):
        raise ReadOnlyPortfolioIngestionError(
            f"{label} must be a JSON object."
        )

    return value


def _require_list(
    value: Any,
    *,
    label: str,
) -> list[Any]:
    if not isinstance(
        value,
        list,
    ):
        raise ReadOnlyPortfolioIngestionError(
            f"{label} must be a JSON array."
        )

    return value


def _decimal_or_none(
    value: Any,
    *,
    label: str,
) -> Decimal | None:
    if value is None:
        return None

    if isinstance(
        value,
        bool,
    ):
        raise ReadOnlyPortfolioIngestionError(
            f"{label} cannot be boolean."
        )

    try:
        result = Decimal(
            str(
                value
            )
        )
    except (
        InvalidOperation,
        ValueError,
    ) as error:
        raise ReadOnlyPortfolioIngestionError(
            f"{label} must be numeric."
        ) from error

    if not result.is_finite():
        raise ReadOnlyPortfolioIngestionError(
            f"{label} must be finite."
        )

    return result


def _require_sha256(
    value: Any,
    *,
    label: str,
) -> str:
    if not isinstance(
        value,
        str,
    ) or len(
        value
    ) != 64:
        raise ReadOnlyPortfolioIngestionError(
            f"{label} must be a SHA-256 hash."
        )

    try:
        int(
            value,
            16,
        )
    except ValueError as error:
        raise ReadOnlyPortfolioIngestionError(
            f"{label} must be hexadecimal."
        ) from error

    return value


def _optional_text(
    value: Any,
) -> str | None:
    if value is None:
        return None

    if not isinstance(
        value,
        str,
    ):
        raise ReadOnlyPortfolioIngestionError(
            "Expected a text value."
        )

    candidate = value.strip()

    return candidate or None


def _require_text(
    value: Any,
    *,
    label: str,
) -> str:
    candidate = _optional_text(
        value
    )

    if candidate is None:
        raise ReadOnlyPortfolioIngestionError(
            f"{label} is required."
        )

    return candidate


def _validate_locked_boundary(
    document: dict[str, Any],
) -> None:
    if document.get(
        "schema"
    ) != READONLY_PORTFOLIO_SCHEMA:
        raise ReadOnlyPortfolioIngestionError(
            "Unsupported portfolio schema."
        )

    if document.get(
        "schema_version"
    ) != READONLY_PORTFOLIO_SCHEMA_VERSION:
        raise ReadOnlyPortfolioIngestionError(
            "Unsupported portfolio schema version."
        )

    if document.get(
        "read_only"
    ) is not True:
        raise ReadOnlyPortfolioIngestionError(
            "Portfolio must be read-only."
        )

    if document.get(
        "paper_only"
    ) is not True:
        raise ReadOnlyPortfolioIngestionError(
            "Portfolio must remain paper-only."
        )

    if document.get(
        "trading_enabled"
    ) is not False:
        raise ReadOnlyPortfolioIngestionError(
            "Trading must remain disabled."
        )

    if document.get(
        "order_operations_enabled"
    ) is not False:
        raise ReadOnlyPortfolioIngestionError(
            "Order operations must remain disabled."
        )

    if document.get(
        "database_persisted"
    ) is not False:
        raise ReadOnlyPortfolioIngestionError(
            "Database persistence is not authorized."
        )

    if document.get(
        "network_request_count"
    ) != 0:
        raise ReadOnlyPortfolioIngestionError(
            "Ingestion input must record zero network requests."
        )


def _parse_balance(
    value: Any,
    *,
    account_index: int,
    balance_index: int,
) -> ReadOnlyBalance:
    item = _require_mapping(
        value,
        label=(
            f"accounts[{account_index}]"
            f".balances[{balance_index}]"
        ),
    )

    return ReadOnlyBalance(
        currency=_optional_text(
            item.get(
                "currency"
            )
        ),
        cash_amount=_decimal_or_none(
            item.get(
                "cash_amount"
            ),
            label=(
                f"accounts[{account_index}]"
                f".balances[{balance_index}]"
                ".cash_amount"
            ),
        ),
        buying_power=_decimal_or_none(
            item.get(
                "buying_power"
            ),
            label=(
                f"accounts[{account_index}]"
                f".balances[{balance_index}]"
                ".buying_power"
            ),
        ),
        cash_available=_decimal_or_none(
            item.get(
                "cash_available"
            ),
            label=(
                f"accounts[{account_index}]"
                f".balances[{balance_index}]"
                ".cash_available"
            ),
        ),
        settled_cash=_decimal_or_none(
            item.get(
                "settled_cash"
            ),
            label=(
                f"accounts[{account_index}]"
                f".balances[{balance_index}]"
                ".settled_cash"
            ),
        ),
    )


def _parse_position(
    value: Any,
    *,
    account_index: int,
    position_index: int,
) -> ReadOnlyPosition:
    item = _require_mapping(
        value,
        label=(
            f"accounts[{account_index}]"
            f".positions[{position_index}]"
        ),
    )

    position_hash = item.get(
        "position_id_hash"
    )

    if position_hash is not None:
        position_hash = _require_sha256(
            position_hash,
            label=(
                f"accounts[{account_index}]"
                f".positions[{position_index}]"
                ".position_id_hash"
            ),
        )

    read_only = item.get(
        "read_only"
    )

    if read_only is not True:
        raise ReadOnlyPortfolioIngestionError(
            "Every position must remain read-only."
        )

    source_provider = _require_text(
        item.get(
            "source_provider"
        ),
        label="position source_provider",
    )

    if source_provider != "snaptrade":
        raise ReadOnlyPortfolioIngestionError(
            "Unexpected position source provider."
        )

    quantity = _decimal_or_none(
        item.get(
            "quantity"
        ),
        label=(
            f"accounts[{account_index}]"
            f".positions[{position_index}]"
            ".quantity"
        ),
    )

    if quantity is None:
        raise ReadOnlyPortfolioIngestionError(
            "Position quantity is required."
        )

    return ReadOnlyPosition(
        position_id_hash=position_hash,
        symbol=_require_text(
            item.get(
                "symbol"
            ),
            label="position symbol",
        ).upper(),
        instrument_kind=_optional_text(
            item.get(
                "instrument_kind"
            )
        ),
        currency=_optional_text(
            item.get(
                "currency"
            )
        ),
        quantity=quantity,
        average_entry_price=_decimal_or_none(
            item.get(
                "average_entry_price"
            ),
            label="average_entry_price",
        ),
        current_price=_decimal_or_none(
            item.get(
                "current_price"
            ),
            label="current_price",
        ),
        market_value=_decimal_or_none(
            item.get(
                "market_value"
            ),
            label="market_value",
        ),
        market_value_source=_optional_text(
            item.get(
                "market_value_source"
            )
        ),
        cost_basis=_decimal_or_none(
            item.get(
                "cost_basis"
            ),
            label="cost_basis",
        ),
        cost_basis_source=_optional_text(
            item.get(
                "cost_basis_source"
            )
        ),
        unrealized_gain=_decimal_or_none(
            item.get(
                "unrealized_gain"
            ),
            label="unrealized_gain",
        ),
        unrealized_gain_source=_optional_text(
            item.get(
                "unrealized_gain_source"
            )
        ),
        source_provider=source_provider,
        read_only=True,
    )


def _parse_account(
    value: Any,
    *,
    account_index: int,
) -> ReadOnlyPortfolioAccount:
    item = _require_mapping(
        value,
        label=f"accounts[{account_index}]",
    )

    account_hash = _require_sha256(
        item.get(
            "account_id_hash"
        ),
        label=(
            f"accounts[{account_index}]"
            ".account_id_hash"
        ),
    )

    if item.get(
        "read_only"
    ) is not True:
        raise ReadOnlyPortfolioIngestionError(
            "Every account must remain read-only."
        )

    source_provider = _require_text(
        item.get(
            "source_provider"
        ),
        label="account source_provider",
    )

    if source_provider != "snaptrade":
        raise ReadOnlyPortfolioIngestionError(
            "Unexpected account source provider."
        )

    balances_raw = _require_list(
        item.get(
            "balances"
        ),
        label=(
            f"accounts[{account_index}]"
            ".balances"
        ),
    )

    positions_raw = _require_list(
        item.get(
            "positions"
        ),
        label=(
            f"accounts[{account_index}]"
            ".positions"
        ),
    )

    balances = tuple(
        _parse_balance(
            balance,
            account_index=account_index,
            balance_index=balance_index,
        )
        for balance_index, balance
        in enumerate(
            balances_raw
        )
    )

    positions = tuple(
        _parse_position(
            position,
            account_index=account_index,
            position_index=position_index,
        )
        for position_index, position
        in enumerate(
            positions_raw
        )
    )

    if item.get(
        "balance_count"
    ) != len(
        balances
    ):
        raise ReadOnlyPortfolioIngestionError(
            "Account balance count mismatch."
        )

    if item.get(
        "position_count"
    ) != len(
        positions
    ):
        raise ReadOnlyPortfolioIngestionError(
            "Account position count mismatch."
        )

    return ReadOnlyPortfolioAccount(
        account_id_hash=account_hash,
        institution_name=_optional_text(
            item.get(
                "institution_name"
            )
        ),
        account_category=_optional_text(
            item.get(
                "account_category"
            )
        ),
        is_paper=bool(
            item.get(
                "is_paper"
            )
        ),
        source_provider=source_provider,
        read_only=True,
        cash_total=_decimal_or_none(
            item.get(
                "cash_total"
            ),
            label="cash_total",
        ),
        market_value_total=_decimal_or_none(
            item.get(
                "market_value_total"
            ),
            label="market_value_total",
        ),
        cost_basis_total=_decimal_or_none(
            item.get(
                "cost_basis_total"
            ),
            label="cost_basis_total",
        ),
        unrealized_gain_total=_decimal_or_none(
            item.get(
                "unrealized_gain_total"
            ),
            label="unrealized_gain_total",
        ),
        balances=balances,
        positions=positions,
    )


def ingest_normalized_portfolio(
    source: Path | str,
) -> ReadOnlyPortfolioSnapshot:
    path = Path(
        source
    )

    document = _require_mapping(
        json.loads(
            path.read_text(
                encoding="utf-8",
            )
        ),
        label="portfolio",
    )

    _validate_locked_boundary(
        document
    )

    accounts_raw = _require_list(
        document.get(
            "accounts"
        ),
        label="accounts",
    )

    accounts = tuple(
        _parse_account(
            account,
            account_index=account_index,
        )
        for account_index, account
        in enumerate(
            accounts_raw
        )
    )

    if document.get(
        "account_count"
    ) != len(
        accounts
    ):
        raise ReadOnlyPortfolioIngestionError(
            "Portfolio account count mismatch."
        )

    counted_balances = sum(
        len(
            account.balances
        )
        for account in accounts
    )

    counted_positions = sum(
        len(
            account.positions
        )
        for account in accounts
    )

    if document.get(
        "balance_record_count"
    ) != counted_balances:
        raise ReadOnlyPortfolioIngestionError(
            "Portfolio balance count mismatch."
        )

    if document.get(
        "position_count"
    ) != counted_positions:
        raise ReadOnlyPortfolioIngestionError(
            "Portfolio position count mismatch."
        )

    seen_accounts: set[str] = set()

    for account in accounts:
        if account.account_id_hash in seen_accounts:
            raise ReadOnlyPortfolioIngestionError(
                "Duplicate account hash detected."
            )

        seen_accounts.add(
            account.account_id_hash
        )

    totals_raw = _require_mapping(
        document.get(
            "totals"
        ),
        label="totals",
    )

    calculated_fields_raw = _require_mapping(
        document.get(
            "calculated_fields"
        ),
        label="calculated_fields",
    )

    source_evidence_raw = _require_mapping(
        document.get(
            "source_evidence"
        ),
        label="source_evidence",
    )

    calculated_fields = {
        str(key):
            int(
                value
            )
        for key, value
        in calculated_fields_raw.items()
    }

    source_evidence = {
        str(key):
            _require_sha256(
                value,
                label=(
                    "source_evidence."
                    + str(
                        key
                    )
                ),
            )
        for key, value
        in source_evidence_raw.items()
    }

    return ReadOnlyPortfolioSnapshot(
        schema=READONLY_PORTFOLIO_SCHEMA,
        schema_version=(
            READONLY_PORTFOLIO_SCHEMA_VERSION
        ),
        snapshot_type=_require_text(
            document.get(
                "snapshot_type"
            ),
            label="snapshot_type",
        ),
        generated_at=_require_text(
            document.get(
                "generated_at"
            ),
            label="generated_at",
        ),
        source_provider=_require_text(
            document.get(
                "source_provider"
            ),
            label="source_provider",
        ),
        source_environment=_require_text(
            document.get(
                "source_environment"
            ),
            label="source_environment",
        ),
        read_only=True,
        paper_only=True,
        trading_enabled=False,
        order_operations_enabled=False,
        database_persisted=False,
        network_request_count=0,
        account_count=len(
            accounts
        ),
        balance_record_count=counted_balances,
        position_count=counted_positions,
        symbols=tuple(
            str(
                symbol
            )
            for symbol in _require_list(
                document.get(
                    "symbols"
                ),
                label="symbols",
            )
        ),
        instrument_kinds=tuple(
            str(
                kind
            )
            for kind in _require_list(
                document.get(
                    "instrument_kinds"
                ),
                label="instrument_kinds",
            )
        ),
        currencies=tuple(
            str(
                currency
            )
            for currency in _require_list(
                document.get(
                    "currencies"
                ),
                label="currencies",
            )
        ),
        totals=ReadOnlyPortfolioTotals(
            cash=_decimal_or_none(
                totals_raw.get(
                    "cash"
                ),
                label="totals.cash",
            ),
            market_value=_decimal_or_none(
                totals_raw.get(
                    "market_value"
                ),
                label="totals.market_value",
            ),
            cost_basis=_decimal_or_none(
                totals_raw.get(
                    "cost_basis"
                ),
                label="totals.cost_basis",
            ),
            unrealized_gain=_decimal_or_none(
                totals_raw.get(
                    "unrealized_gain"
                ),
                label="totals.unrealized_gain",
            ),
            market_value_complete=bool(
                totals_raw.get(
                    "market_value_complete"
                )
            ),
            cost_basis_complete=bool(
                totals_raw.get(
                    "cost_basis_complete"
                )
            ),
            unrealized_gain_complete=bool(
                totals_raw.get(
                    "unrealized_gain_complete"
                )
            ),
        ),
        calculated_fields=calculated_fields,
        source_evidence=source_evidence,
        accounts=accounts,
    )
