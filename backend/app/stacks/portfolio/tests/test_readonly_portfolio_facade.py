from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from backend.app.stacks.portfolio.facades.readonly_portfolio_facade import (
    ReadOnlyPortfolioFacade,
    ReadOnlyPortfolioFacadeError,
)

from backend.app.stacks.snaptrade.application.normalized_portfolio_ingestion import (
    ingest_normalized_portfolio,
)


def qualified_snapshot_path() -> Path:
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
        pytest.skip(
            "No qualified normalized snapshot exists."
        )

    return candidates[-1]


def build_facade() -> ReadOnlyPortfolioFacade:
    snapshot = ingest_normalized_portfolio(
        qualified_snapshot_path()
    )

    return ReadOnlyPortfolioFacade(
        snapshot
    )


def test_facade_overview() -> None:
    overview = build_facade().get_overview()

    assert overview.source_provider == "snaptrade"
    assert overview.source_environment == "sandbox"
    assert overview.account_count == 2
    assert overview.balance_record_count == 2
    assert overview.position_count == 5
    assert overview.read_only is True
    assert overview.paper_only is True
    assert overview.trading_enabled is False
    assert overview.order_operations_enabled is False

    assert set(
        overview.symbols
    ) == {
        "AAPL",
        "GOOGL",
        "MSFT",
        "NVDA",
        "TSLA",
    }


def test_lists_account_summaries() -> None:
    facade = build_facade()

    accounts = facade.list_accounts()

    assert len(accounts) == 2

    assert sum(
        account.position_count
        for account in accounts
    ) == 5

    assert sum(
        account.balance_count
        for account in accounts
    ) == 2

    assert all(
        account.is_paper
        for account in accounts
    )

    assert all(
        account.source_provider
        == "snaptrade"
        for account in accounts
    )


def test_get_account_by_hash() -> None:
    facade = build_facade()

    summary = facade.list_accounts()[0]

    account = facade.get_account(
        summary.account_id_hash
    )

    assert (
        account.account_id_hash
        == summary.account_id_hash
    )

    assert account.read_only is True
    assert account.is_paper is True


def test_unknown_account_is_rejected() -> None:
    facade = build_facade()

    with pytest.raises(
        ReadOnlyPortfolioFacadeError
    ):
        facade.get_account(
            "0" * 64
        )


def test_lists_all_positions() -> None:
    positions = (
        build_facade()
        .list_positions()
    )

    assert len(positions) == 5

    assert {
        item.position.symbol
        for item in positions
    } == {
        "AAPL",
        "GOOGL",
        "MSFT",
        "NVDA",
        "TSLA",
    }

    assert all(
        item.position.read_only
        for item in positions
    )


@pytest.mark.parametrize(
    "symbol",
    (
        "aapl",
        " AAPL ",
        "AaPl",
    ),
)
def test_symbol_lookup_is_normalized(
    symbol: str,
) -> None:
    positions = (
        build_facade()
        .find_positions_by_symbol(
            symbol
        )
    )

    assert positions

    assert all(
        item.position.symbol == "AAPL"
        for item in positions
    )


def test_unknown_symbol_returns_empty_tuple() -> None:
    positions = (
        build_facade()
        .find_positions_by_symbol(
            "DOES-NOT-EXIST"
        )
    )

    assert positions == ()


def test_empty_symbol_is_rejected() -> None:
    with pytest.raises(
        ReadOnlyPortfolioFacadeError
    ):
        (
            build_facade()
            .find_positions_by_symbol(
                "   "
            )
        )


def test_lists_balances() -> None:
    balances = (
        build_facade()
        .list_balances()
    )

    assert len(balances) == 2

    assert all(
        len(account_hash) == 64
        for account_hash, _balance
        in balances
    )


def test_totals_are_provider_neutral() -> None:
    facade = build_facade()

    totals = facade.get_totals()

    assert totals is facade.snapshot.totals


def test_overview_is_immutable() -> None:
    overview = build_facade().get_overview()

    with pytest.raises(
        FrozenInstanceError
    ):
        overview.account_count = 999  # type: ignore[misc]


def test_account_summary_is_immutable() -> None:
    summary = build_facade().list_accounts()[0]

    with pytest.raises(
        FrozenInstanceError
    ):
        summary.position_count = 999  # type: ignore[misc]


def test_symbol_result_is_immutable() -> None:
    result = (
        build_facade()
        .find_positions_by_symbol(
            "AAPL"
        )[0]
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        result.account_id_hash = "x"  # type: ignore[misc]


def test_symbol_index_is_not_mutable() -> None:
    index = build_facade().get_symbol_index()

    with pytest.raises(
        TypeError
    ):
        index["FAKE"] = ()  # type: ignore[index]


def test_facade_has_no_mutation_methods() -> None:
    forbidden_names = {
        "add",
        "create",
        "delete",
        "execute",
        "insert",
        "mutate",
        "order",
        "persist",
        "place",
        "remove",
        "save",
        "submit",
        "trade",
        "update",
        "write",
    }

    public_methods = {
        name.lower()
        for name in dir(
            ReadOnlyPortfolioFacade
        )
        if not name.startswith("_")
    }

    assert (
        forbidden_names
        & public_methods
    ) == set()


def test_facade_source_has_no_provider_import() -> None:
    import ast

    import backend.app.stacks.portfolio.facades.readonly_portfolio_facade as module

    source_path = Path(
        module.__file__
    )

    tree = ast.parse(
        source_path.read_text(
            encoding="utf-8",
        ),
        filename=str(
            source_path
        ),
    )

    forbidden_roots = {
        "snaptrade_client",
        "sqlalchemy",
        "httpx",
        "requests",
        "urllib3",
        "aiohttp",
        "socket",
    }

    forbidden_prefixes = (
        "backend.app.stacks.snaptrade",
    )

    violations: list[str] = []

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            ast.Import,
        ):
            modules = [
                alias.name
                for alias in node.names
            ]

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            modules = [
                node.module or ""
            ]

        else:
            continue

        for imported_module in modules:
            root = imported_module.split(
                ".",
                1,
            )[0]

            if root in forbidden_roots:
                violations.append(
                    imported_module
                )

            if imported_module.startswith(
                forbidden_prefixes
            ):
                violations.append(
                    imported_module
                )

    assert violations == []
