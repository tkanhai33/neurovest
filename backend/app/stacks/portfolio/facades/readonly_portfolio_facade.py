from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from types import MappingProxyType
from typing import Mapping, Sequence

from backend.app.stacks.portfolio.read_models.readonly_portfolio_snapshot import (
    ReadOnlyBalance,
    ReadOnlyPortfolioAccount,
    ReadOnlyPortfolioSnapshot,
    ReadOnlyPortfolioTotals,
    ReadOnlyPosition,
)


class ReadOnlyPortfolioFacadeError(
    ValueError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class ReadOnlyPortfolioAccountSummary:
    account_id_hash: str
    institution_name: str | None
    account_category: str | None
    is_paper: bool
    source_provider: str
    currency_codes: tuple[str, ...]
    balance_count: int
    position_count: int
    cash_total: Decimal | None
    market_value_total: Decimal | None
    cost_basis_total: Decimal | None
    unrealized_gain_total: Decimal | None


@dataclass(
    frozen=True,
    slots=True,
)
class ReadOnlySymbolPosition:
    account_id_hash: str
    institution_name: str | None
    position: ReadOnlyPosition


@dataclass(
    frozen=True,
    slots=True,
)
class ReadOnlyPortfolioOverview:
    source_provider: str
    source_environment: str
    generated_at: str
    account_count: int
    balance_record_count: int
    position_count: int
    symbols: tuple[str, ...]
    currencies: tuple[str, ...]
    instrument_kinds: tuple[str, ...]
    totals: ReadOnlyPortfolioTotals
    read_only: bool
    paper_only: bool
    trading_enabled: bool
    order_operations_enabled: bool


class ReadOnlyPortfolioFacade:
    __slots__ = (
        "_snapshot",
        "_accounts_by_hash",
        "_positions_by_symbol",
    )

    def __init__(
        self,
        snapshot: ReadOnlyPortfolioSnapshot,
    ) -> None:
        self._validate_snapshot(
            snapshot
        )

        accounts_by_hash: dict[
            str,
            ReadOnlyPortfolioAccount,
        ] = {}

        positions_by_symbol: dict[
            str,
            list[ReadOnlySymbolPosition],
        ] = {}

        for account in snapshot.accounts:
            if (
                account.account_id_hash
                in accounts_by_hash
            ):
                raise ReadOnlyPortfolioFacadeError(
                    "Duplicate account hash detected."
                )

            accounts_by_hash[
                account.account_id_hash
            ] = account

            for position in account.positions:
                symbol = position.symbol.upper()

                positions_by_symbol.setdefault(
                    symbol,
                    [],
                ).append(
                    ReadOnlySymbolPosition(
                        account_id_hash=(
                            account.account_id_hash
                        ),
                        institution_name=(
                            account.institution_name
                        ),
                        position=position,
                    )
                )

        frozen_symbol_index = {
            symbol:
                tuple(
                    sorted(
                        positions,
                        key=lambda item: (
                            item.account_id_hash,
                            item.position.position_id_hash
                            or "",
                        ),
                    )
                )
            for symbol, positions
            in positions_by_symbol.items()
        }

        object.__setattr__(
            self,
            "_snapshot",
            snapshot,
        )

        object.__setattr__(
            self,
            "_accounts_by_hash",
            MappingProxyType(
                accounts_by_hash
            ),
        )

        object.__setattr__(
            self,
            "_positions_by_symbol",
            MappingProxyType(
                frozen_symbol_index
            ),
        )

    @staticmethod
    def _validate_snapshot(
        snapshot: ReadOnlyPortfolioSnapshot,
    ) -> None:
        if not isinstance(
            snapshot,
            ReadOnlyPortfolioSnapshot,
        ):
            raise ReadOnlyPortfolioFacadeError(
                "Facade requires a ReadOnlyPortfolioSnapshot."
            )

        if snapshot.read_only is not True:
            raise ReadOnlyPortfolioFacadeError(
                "Snapshot must remain read-only."
            )

        if snapshot.paper_only is not True:
            raise ReadOnlyPortfolioFacadeError(
                "Snapshot must remain paper-only."
            )

        if snapshot.trading_enabled is not False:
            raise ReadOnlyPortfolioFacadeError(
                "Trading must remain disabled."
            )

        if (
            snapshot.order_operations_enabled
            is not False
        ):
            raise ReadOnlyPortfolioFacadeError(
                "Order operations must remain disabled."
            )

        if snapshot.database_persisted is not False:
            raise ReadOnlyPortfolioFacadeError(
                "Database persistence is not authorized."
            )

        if snapshot.network_request_count != 0:
            raise ReadOnlyPortfolioFacadeError(
                "Facade input must record zero network requests."
            )

        if snapshot.account_count != len(
            snapshot.accounts
        ):
            raise ReadOnlyPortfolioFacadeError(
                "Snapshot account count is inconsistent."
            )

        counted_balances = sum(
            len(
                account.balances
            )
            for account in snapshot.accounts
        )

        counted_positions = sum(
            len(
                account.positions
            )
            for account in snapshot.accounts
        )

        if (
            snapshot.balance_record_count
            != counted_balances
        ):
            raise ReadOnlyPortfolioFacadeError(
                "Snapshot balance count is inconsistent."
            )

        if (
            snapshot.position_count
            != counted_positions
        ):
            raise ReadOnlyPortfolioFacadeError(
                "Snapshot position count is inconsistent."
            )

        for account in snapshot.accounts:
            if account.read_only is not True:
                raise ReadOnlyPortfolioFacadeError(
                    "Every account must remain read-only."
                )

            if account.is_paper is not True:
                raise ReadOnlyPortfolioFacadeError(
                    "Every account must remain paper-only."
                )

            for position in account.positions:
                if position.read_only is not True:
                    raise ReadOnlyPortfolioFacadeError(
                        "Every position must remain read-only."
                    )

    @property
    def snapshot(
        self,
    ) -> ReadOnlyPortfolioSnapshot:
        return self._snapshot

    def get_overview(
        self,
    ) -> ReadOnlyPortfolioOverview:
        snapshot = self._snapshot

        return ReadOnlyPortfolioOverview(
            source_provider=(
                snapshot.source_provider
            ),
            source_environment=(
                snapshot.source_environment
            ),
            generated_at=(
                snapshot.generated_at
            ),
            account_count=(
                snapshot.account_count
            ),
            balance_record_count=(
                snapshot.balance_record_count
            ),
            position_count=(
                snapshot.position_count
            ),
            symbols=tuple(
                snapshot.symbols
            ),
            currencies=tuple(
                snapshot.currencies
            ),
            instrument_kinds=tuple(
                snapshot.instrument_kinds
            ),
            totals=snapshot.totals,
            read_only=True,
            paper_only=True,
            trading_enabled=False,
            order_operations_enabled=False,
        )

    def list_accounts(
        self,
    ) -> tuple[
        ReadOnlyPortfolioAccountSummary,
        ...,
    ]:
        summaries: list[
            ReadOnlyPortfolioAccountSummary
        ] = []

        for account in sorted(
            self._snapshot.accounts,
            key=lambda item:
                item.account_id_hash,
        ):
            currency_codes = tuple(
                sorted(
                    {
                        balance.currency
                        for balance
                        in account.balances
                        if balance.currency
                    }
                    | {
                        position.currency
                        for position
                        in account.positions
                        if position.currency
                    }
                )
            )

            summaries.append(
                ReadOnlyPortfolioAccountSummary(
                    account_id_hash=(
                        account.account_id_hash
                    ),
                    institution_name=(
                        account.institution_name
                    ),
                    account_category=(
                        account.account_category
                    ),
                    is_paper=(
                        account.is_paper
                    ),
                    source_provider=(
                        account.source_provider
                    ),
                    currency_codes=(
                        currency_codes
                    ),
                    balance_count=len(
                        account.balances
                    ),
                    position_count=len(
                        account.positions
                    ),
                    cash_total=(
                        account.cash_total
                    ),
                    market_value_total=(
                        account.market_value_total
                    ),
                    cost_basis_total=(
                        account.cost_basis_total
                    ),
                    unrealized_gain_total=(
                        account.unrealized_gain_total
                    ),
                )
            )

        return tuple(
            summaries
        )

    def get_account(
        self,
        account_id_hash: str,
    ) -> ReadOnlyPortfolioAccount:
        normalized_hash = (
            account_id_hash.strip().lower()
        )

        account = self._accounts_by_hash.get(
            normalized_hash
        )

        if account is None:
            raise ReadOnlyPortfolioFacadeError(
                "Portfolio account was not found."
            )

        return account

    def list_positions(
        self,
    ) -> tuple[
        ReadOnlySymbolPosition,
        ...,
    ]:
        positions: list[
            ReadOnlySymbolPosition
        ] = []

        for symbol in sorted(
            self._positions_by_symbol
        ):
            positions.extend(
                self._positions_by_symbol[
                    symbol
                ]
            )

        return tuple(
            positions
        )

    def find_positions_by_symbol(
        self,
        symbol: str,
    ) -> tuple[
        ReadOnlySymbolPosition,
        ...,
    ]:
        normalized_symbol = (
            symbol.strip().upper()
        )

        if not normalized_symbol:
            raise ReadOnlyPortfolioFacadeError(
                "Symbol is required."
            )

        return self._positions_by_symbol.get(
            normalized_symbol,
            (),
        )

    def list_balances(
        self,
    ) -> tuple[
        tuple[
            str,
            ReadOnlyBalance,
        ],
        ...,
    ]:
        balances: list[
            tuple[
                str,
                ReadOnlyBalance,
            ]
        ] = []

        for account in sorted(
            self._snapshot.accounts,
            key=lambda item:
                item.account_id_hash,
        ):
            for balance in sorted(
                account.balances,
                key=lambda item:
                    item.currency or "",
            ):
                balances.append(
                    (
                        account.account_id_hash,
                        balance,
                    )
                )

        return tuple(
            balances
        )

    def get_totals(
        self,
    ) -> ReadOnlyPortfolioTotals:
        return self._snapshot.totals

    def get_symbol_index(
        self,
    ) -> Mapping[
        str,
        Sequence[
            ReadOnlySymbolPosition
        ],
    ]:
        return self._positions_by_symbol
