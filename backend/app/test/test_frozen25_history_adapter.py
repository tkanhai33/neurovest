from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import hashlib

import pytest

from backend.app.stacks.strategy.model_inference.frozen25_history_adapter import (
    FROZEN25_HISTORY_FIRST_TIMESTAMP,
    FROZEN25_HISTORY_LAST_TIMESTAMP,
    FROZEN25_HISTORY_ROW_COUNT,
    FROZEN25_HISTORY_SHA256,
    FROZEN25_HISTORY_SYMBOL,
    FROZEN25_STRATEGY_FINGERPRINT,
    FROZEN25_STRATEGY_ID,
    Frozen25HistoryIdentityError,
    Frozen25HistoryIntegrityError,
    Frozen25HistoryRow,
    _load_qualified_history_file,
    frozen25_history_contract,
    frozen25_history_path,
    load_frozen25_history,
)


def test_contract_is_canonical_and_dormant():

    contract = frozen25_history_contract()

    assert contract[
        "strategy_id"
    ] == FROZEN25_STRATEGY_ID

    assert contract[
        "strategy_fingerprint"
    ] == FROZEN25_STRATEGY_FINGERPRINT

    assert contract[
        "history_sha256"
    ] == FROZEN25_HISTORY_SHA256

    assert contract[
        "history_row_count"
    ] == 7930

    assert contract[
        "binding_mode"
    ] == "dormant_read_only"

    assert contract[
        "model_load"
    ] is False

    assert contract[
        "prediction"
    ] is False

    assert contract[
        "database_write"
    ] is False

    assert contract[
        "network_request"
    ] is False

    assert contract[
        "runtime_activation"
    ] is False

    assert contract[
        "execution"
    ] is False


def test_contract_mapping_is_immutable():

    contract = frozen25_history_contract()

    with pytest.raises(
        TypeError
    ):
        contract[
            "strategy_id"
        ] = "challenger_bad"


def test_history_path_is_exact_generation274_source():

    path = frozen25_history_path()

    assert path.name == "TD_TO.csv"

    assert (
        "generation274_isolated_history_extension_20260806_114523"
        in str(
            path
        )
    )

    assert (
        "/extended/TD_TO.csv"
        in str(
            path
        )
    )

    assert path.is_file()


def test_history_file_sha_matches_qualified_contract():

    path = frozen25_history_path()

    digest = hashlib.sha256(
        path.read_bytes()
    ).hexdigest()

    assert digest == FROZEN25_HISTORY_SHA256


def test_wrong_strategy_id_is_rejected_before_history_binding():

    with pytest.raises(
        Frozen25HistoryIdentityError
    ):
        load_frozen25_history(
            strategy_id="challenger_06627"
        )


def test_wrong_strategy_fingerprint_is_rejected():

    with pytest.raises(
        Frozen25HistoryIdentityError
    ):
        load_frozen25_history(
            strategy_id=FROZEN25_STRATEGY_ID,
            strategy_fingerprint="not-the-canonical-fingerprint",
        )


def test_wrong_expected_sha_is_rejected():

    with pytest.raises(
        Frozen25HistoryIntegrityError
    ):
        _load_qualified_history_file(
            path=frozen25_history_path(),
            expected_sha256="0" * 64,
        )


def test_exact_history_loads_for_canonical_identity():

    history = load_frozen25_history(
        strategy_id=FROZEN25_STRATEGY_ID,
        strategy_fingerprint=FROZEN25_STRATEGY_FINGERPRINT,
    )

    assert history.strategy_id == FROZEN25_STRATEGY_ID

    assert (
        history.strategy_fingerprint
        == FROZEN25_STRATEGY_FINGERPRINT
    )

    assert (
        history.source_sha256
        == FROZEN25_HISTORY_SHA256
    )

    assert history.row_count == FROZEN25_HISTORY_ROW_COUNT


def test_exact_history_boundaries_match_qualification():

    history = load_frozen25_history(
        strategy_id=FROZEN25_STRATEGY_ID
    )

    assert (
        history.first_timestamp.isoformat(
            sep=" "
        )
        == FROZEN25_HISTORY_FIRST_TIMESTAMP
    )

    assert (
        history.last_timestamp.isoformat(
            sep=" "
        )
        == FROZEN25_HISTORY_LAST_TIMESTAMP
    )


def test_every_row_is_td_to_and_timestamps_strictly_increase():

    history = load_frozen25_history(
        strategy_id=FROZEN25_STRATEGY_ID
    )

    assert all(
        row.symbol
        == FROZEN25_HISTORY_SYMBOL
        for row
        in history.rows
    )

    assert all(
        left.timestamp
        < right.timestamp
        for left, right
        in zip(
            history.rows,
            history.rows[
                1:
            ],
        )
    )


def test_rows_are_frozen():

    history = load_frozen25_history(
        strategy_id=FROZEN25_STRATEGY_ID
    )

    row = history.rows[
        0
    ]

    assert isinstance(
        row,
        Frozen25HistoryRow,
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        row.close = 0.0


def test_loaded_history_container_is_frozen():

    history = load_frozen25_history(
        strategy_id=FROZEN25_STRATEGY_ID
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        history.strategy_id = "different"
