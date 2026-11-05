
"""Check the real worker's dataset-reader boundary without training."""

from pathlib import Path
import pytest

from backend.app.stacks.strategy_candidate_sandbox.L4_runtime_orchestration import (
    bounded_training_runtime as runtime,
)


class ReaderReached(Exception):
    pass


@pytest.mark.parametrize(
    "selected,expected",
    [
        (["TD.TO"], {"TD.TO"}),
        (["BTE.TO", "WCP.TO"], {"BTE.TO", "WCP.TO"}),
        (
            ["BTE.TO", "TD.TO", "WCP.TO"],
            {"BTE.TO", "TD.TO", "WCP.TO"},
        ),
    ],
)
def test_worker_reads_only_selected_datasets(
    monkeypatch, selected, expected
):
    run_id = "isolated-owner-filter-test"
    symbols = ["BTE.TO", "TD.TO", "WCP.TO", "AAPL"]

    paths = {
        symbol: Path("/isolated") / (
            symbol.replace(".", "_") + ".csv"
        )
        for symbol in symbols
    }

    accessed = []

    def discover():
        return [
            {"symbol": symbol, "path": str(paths[symbol])}
            for symbol in symbols
        ]

    def read_rows(path, **kwargs):
        accessed.append(str(path))
        return []

    def update_run(*args, **kwargs):
        return None

    monkeypatch.setattr(
        runtime, "discover_canadian_datasets", discover
    )
    monkeypatch.setattr(
        runtime, "_read_close_rows", read_rows
    )
    monkeypatch.setattr(
        runtime, "_update_run", update_run
    )
    monkeypatch.setattr(
        runtime, "_RUNS",
        {
            run_id: {
                "duration_seconds": 1,
                "selected_symbols": selected,
                "training_window": {},
                "scope": "user",
                "owner_user_id": "isolated-test-owner",
                "owner_session_id": "isolated-test-session",
            }
        },
    )

    runtime._run_training(run_id)

    actual = {
        symbol
        for symbol, path in paths.items()
        if str(path) in accessed
    }

    assert actual == expected
    assert "AAPL" not in actual


def test_unfiltered_worker_keeps_discovery_behavior(monkeypatch):
    run_id = "isolated-unfiltered-test"
    accessed = []

    def read_rows(path, **kwargs):
        accessed.append(Path(path).name)
        return []

    monkeypatch.setattr(
        runtime, "discover_canadian_datasets",
        lambda: [
            {"symbol": "TD.TO", "path": "/isolated/TD_TO.csv"},
            {"symbol": "AAPL", "path": "/isolated/AAPL.csv"},
        ],
    )
    monkeypatch.setattr(
        runtime, "_read_close_rows", read_rows
    )
    monkeypatch.setattr(
        runtime, "_update_run", lambda *args, **kwargs: None
    )
    monkeypatch.setattr(
        runtime, "_RUNS",
        {
            run_id: {
                "duration_seconds": 1,
                "training_window": {},
                "scope": "system",
            }
        },
    )

    runtime._run_training(run_id)

    assert set(accessed) == {"TD_TO.csv", "AAPL.csv"}
