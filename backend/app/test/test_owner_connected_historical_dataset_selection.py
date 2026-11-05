
"""Real historical dataset selection; no training sessions launched."""

import csv
from pathlib import Path

import pytest

from backend.app.stacks.db_runtime.owner_ai_scope import (
    OwnerAIScope,
    OwnerScopeDenied,
    select_owner_symbols,
)
from backend.app.stacks.strategy_candidate_sandbox.L4_runtime_orchestration.bounded_training_runtime import (
    discover_canadian_datasets,
)


SYMBOLS = ("BTE.TO", "TD.TO", "WCP.TO")


def scope(owner):
    return OwnerAIScope(
        owner_user_id=owner,
        owner_session_id=f"session-{owner}",
        role="user",
    )


def filtered_datasets(symbols):
    permitted = set(symbols)
    return [
        dataset
        for dataset in discover_canadian_datasets()
        if str(dataset.get("symbol", "")).strip().upper()
        in permitted
    ]


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_real_historical_dataset_exists_and_is_readable(symbol):
    datasets = filtered_datasets((symbol,))
    assert datasets, f"Missing historical data for {symbol}"

    for dataset in datasets:
        path = Path(dataset["path"])
        assert path.is_file()
        assert dataset["symbol"].upper() == symbol

        with path.open(
            encoding="utf-8-sig",
            newline="",
        ) as handle:
            reader = csv.DictReader(handle)
            assert reader.fieldnames
            assert {"date", "close"}.issubset(
                {name.lower() for name in reader.fieldnames}
            )

            rows = list(reader)

        assert len(rows) >= 100
        assert all(float(row["close"]) > 0 for row in rows)


def test_owner_selects_all_three_real_datasets():
    selected = select_owner_symbols(
        scope=scope("owner-a"),
        connected_symbols=SYMBOLS,
    )

    datasets = filtered_datasets(selected)

    actual = {item["symbol"].upper() for item in datasets}

    assert actual == set(SYMBOLS)
    assert all(item["symbol"].upper() in selected for item in datasets)


def test_two_owners_have_separate_selections():
    first = select_owner_symbols(
        scope=scope("owner-a"),
        connected_symbols=("TD.TO", "WCP.TO"),
        requested_symbols=("TD.TO",),
    )

    second = select_owner_symbols(
        scope=scope("owner-b"),
        connected_symbols=("BTE.TO",),
    )

    first_data = filtered_datasets(first)
    second_data = filtered_datasets(second)

    assert {x["symbol"] for x in first_data} == {"TD.TO"}
    assert {x["symbol"] for x in second_data} == {"BTE.TO"}

    assert not (
        {x["symbol"] for x in first_data}
        & {x["symbol"] for x in second_data}
    )


def test_unconnected_symbol_rejected():
    with pytest.raises(OwnerScopeDenied):
        select_owner_symbols(
            scope=scope("owner-a"),
            connected_symbols=("TD.TO",),
            requested_symbols=("WCP.TO",),
        )


def test_global_training_not_authorized_for_user():
    with pytest.raises(OwnerScopeDenied):
        scope("owner-a").authorize("global_training")
