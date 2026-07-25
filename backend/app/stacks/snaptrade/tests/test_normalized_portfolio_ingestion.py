from __future__ import annotations

import json
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from backend.app.stacks.snaptrade.application.normalized_portfolio_ingestion import (
    ReadOnlyPortfolioIngestionError,
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
            "No qualified normalized SnapTrade snapshot exists."
        )

    return candidates[-1]


def load_source() -> dict:
    return json.loads(
        qualified_snapshot_path().read_text(
            encoding="utf-8",
        )
    )


def write_mutated(
    tmp_path: Path,
    document: dict,
) -> Path:
    target = (
        tmp_path
        / "mutated_portfolio.json"
    )

    target.write_text(
        json.dumps(
            document,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    return target


def test_ingests_qualified_snapshot() -> None:
    snapshot = ingest_normalized_portfolio(
        qualified_snapshot_path()
    )

    assert snapshot.schema == (
        "neurovest.readonly_portfolio"
    )

    assert snapshot.schema_version == 1
    assert snapshot.read_only is True
    assert snapshot.paper_only is True
    assert snapshot.trading_enabled is False
    assert snapshot.order_operations_enabled is False
    assert snapshot.database_persisted is False
    assert snapshot.network_request_count == 0
    assert snapshot.account_count == 2
    assert snapshot.balance_record_count == 2
    assert snapshot.position_count == 5

    assert set(
        snapshot.symbols
    ) == {
        "AAPL",
        "GOOGL",
        "MSFT",
        "NVDA",
        "TSLA",
    }

    assert all(
        account.read_only
        for account in snapshot.accounts
    )

    assert all(
        account.is_paper
        for account in snapshot.accounts
    )

    assert all(
        position.read_only
        for account in snapshot.accounts
        for position in account.positions
    )

    assert all(
        position.source_provider
        == "snaptrade"
        for account in snapshot.accounts
        for position in account.positions
    )


def test_contract_is_immutable() -> None:
    snapshot = ingest_normalized_portfolio(
        qualified_snapshot_path()
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        snapshot.account_count = 999  # type: ignore[misc]


@pytest.mark.parametrize(
    (
        "field",
        "unsafe_value",
    ),
    (
        (
            "read_only",
            False,
        ),
        (
            "paper_only",
            False,
        ),
        (
            "trading_enabled",
            True,
        ),
        (
            "order_operations_enabled",
            True,
        ),
        (
            "database_persisted",
            True,
        ),
        (
            "network_request_count",
            1,
        ),
    ),
)
def test_rejects_unsafe_top_level_flags(
    tmp_path: Path,
    field: str,
    unsafe_value: object,
) -> None:
    document = load_source()

    document[
        field
    ] = unsafe_value

    with pytest.raises(
        ReadOnlyPortfolioIngestionError
    ):
        ingest_normalized_portfolio(
            write_mutated(
                tmp_path,
                document,
            )
        )


def test_rejects_wrong_schema(
    tmp_path: Path,
) -> None:
    document = load_source()

    document[
        "schema"
    ] = "snaptrade.raw.sdk.object"

    with pytest.raises(
        ReadOnlyPortfolioIngestionError
    ):
        ingest_normalized_portfolio(
            write_mutated(
                tmp_path,
                document,
            )
        )


def test_rejects_wrong_schema_version(
    tmp_path: Path,
) -> None:
    document = load_source()

    document[
        "schema_version"
    ] = 2

    with pytest.raises(
        ReadOnlyPortfolioIngestionError
    ):
        ingest_normalized_portfolio(
            write_mutated(
                tmp_path,
                document,
            )
        )


def test_rejects_raw_account_identifier(
    tmp_path: Path,
) -> None:
    document = load_source()

    document[
        "accounts"
    ][0][
        "account_id_hash"
    ] = "raw-account-id"

    with pytest.raises(
        ReadOnlyPortfolioIngestionError
    ):
        ingest_normalized_portfolio(
            write_mutated(
                tmp_path,
                document,
            )
        )


def test_rejects_position_count_drift(
    tmp_path: Path,
) -> None:
    document = load_source()

    document[
        "position_count"
    ] += 1

    with pytest.raises(
        ReadOnlyPortfolioIngestionError
    ):
        ingest_normalized_portfolio(
            write_mutated(
                tmp_path,
                document,
            )
        )


def test_does_not_import_snaptrade_sdk() -> None:
    import backend.app.stacks.snaptrade.application.normalized_portfolio_ingestion as adapter

    source = Path(
        adapter.__file__
    ).read_text(
        encoding="utf-8",
    )

    assert "from snaptrade_client" not in source
    assert "import snaptrade_client" not in source
