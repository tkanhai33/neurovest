from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Mapping, Sequence


READONLY_PORTFOLIO_SCHEMA = (
    "neurovest.readonly_portfolio"
)

READONLY_PORTFOLIO_SCHEMA_VERSION = 1


@dataclass(
    frozen=True,
    slots=True,
)
class ReadOnlyBalance:
    currency: str | None
    cash_amount: Decimal | None
    buying_power: Decimal | None
    cash_available: Decimal | None
    settled_cash: Decimal | None


@dataclass(
    frozen=True,
    slots=True,
)
class ReadOnlyPosition:
    position_id_hash: str | None
    symbol: str
    instrument_kind: str | None
    currency: str | None
    quantity: Decimal
    average_entry_price: Decimal | None
    current_price: Decimal | None
    market_value: Decimal | None
    market_value_source: str | None
    cost_basis: Decimal | None
    cost_basis_source: str | None
    unrealized_gain: Decimal | None
    unrealized_gain_source: str | None
    source_provider: str
    read_only: bool


@dataclass(
    frozen=True,
    slots=True,
)
class ReadOnlyPortfolioAccount:
    account_id_hash: str
    institution_name: str | None
    account_category: str | None
    is_paper: bool
    source_provider: str
    read_only: bool
    cash_total: Decimal | None
    market_value_total: Decimal | None
    cost_basis_total: Decimal | None
    unrealized_gain_total: Decimal | None
    balances: Sequence[ReadOnlyBalance]
    positions: Sequence[ReadOnlyPosition]


@dataclass(
    frozen=True,
    slots=True,
)
class ReadOnlyPortfolioTotals:
    cash: Decimal | None
    market_value: Decimal | None
    cost_basis: Decimal | None
    unrealized_gain: Decimal | None
    market_value_complete: bool
    cost_basis_complete: bool
    unrealized_gain_complete: bool


@dataclass(
    frozen=True,
    slots=True,
)
class ReadOnlyPortfolioSnapshot:
    schema: str
    schema_version: int
    snapshot_type: str
    generated_at: str
    source_provider: str
    source_environment: str
    read_only: bool
    paper_only: bool
    trading_enabled: bool
    order_operations_enabled: bool
    database_persisted: bool
    network_request_count: int
    account_count: int
    balance_record_count: int
    position_count: int
    symbols: Sequence[str]
    instrument_kinds: Sequence[str]
    currencies: Sequence[str]
    totals: ReadOnlyPortfolioTotals
    calculated_fields: Mapping[str, int]
    source_evidence: Mapping[str, str]
    accounts: Sequence[ReadOnlyPortfolioAccount]
