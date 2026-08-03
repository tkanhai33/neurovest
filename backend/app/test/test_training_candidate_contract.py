from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from backend.app.stacks.strategy_candidate_sandbox.training_candidate_contract import (
    TrainingCandidateContract,
    build_training_candidate_contract,
    training_candidate_contract_status,
    validate_training_candidate_contract,
)


def test_candidate_contract_is_deterministic() -> None:
    first = build_training_candidate_contract(
        decision_rule=(
            "moving_average_crossover"
        ),
        short_lookback_rows=5,
        long_lookback_rows=20,
        minimum_signal_strength=0.15,
        created_from="qualification",
    )

    second = build_training_candidate_contract(
        decision_rule=(
            "moving_average_crossover"
        ),
        short_lookback_rows=5,
        long_lookback_rows=20,
        minimum_signal_strength=0.15,
        created_from="qualification",
    )

    assert first == second

    assert (
        first.candidate_id
        == second.candidate_id
    )

    assert (
        first.contract_hash
        == second.contract_hash
    )


def test_candidate_change_produces_new_identity() -> None:
    first = build_training_candidate_contract(
        short_lookback_rows=5,
        long_lookback_rows=20,
        minimum_signal_strength=0.10,
    )

    second = build_training_candidate_contract(
        short_lookback_rows=8,
        long_lookback_rows=30,
        minimum_signal_strength=0.10,
    )

    assert (
        first.candidate_id
        != second.candidate_id
    )

    assert (
        first.contract_hash
        != second.contract_hash
    )


def test_candidate_contract_is_immutable() -> None:
    candidate = build_training_candidate_contract()

    assert isinstance(
        candidate,
        TrainingCandidateContract,
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        candidate.short_lookback_rows = 10  # type: ignore[misc]


def test_candidate_contract_rejects_invalid_windows() -> None:
    with pytest.raises(
        ValueError
    ):
        build_training_candidate_contract(
            short_lookback_rows=20,
            long_lookback_rows=5,
        )

    with pytest.raises(
        ValueError
    ):
        build_training_candidate_contract(
            short_lookback_rows=1,
            long_lookback_rows=20,
        )


def test_candidate_contract_rejects_invalid_strength() -> None:
    with pytest.raises(
        ValueError
    ):
        build_training_candidate_contract(
            minimum_signal_strength=-0.1
        )

    with pytest.raises(
        ValueError
    ):
        build_training_candidate_contract(
            minimum_signal_strength=1.1
        )


def test_validator_detects_candidate_tampering() -> None:
    candidate = (
        build_training_candidate_contract(
            short_lookback_rows=5,
            long_lookback_rows=20,
            minimum_signal_strength=0.25,
        )
        .to_dict()
    )

    assert (
        validate_training_candidate_contract(
            candidate
        )
        is True
    )

    candidate[
        "long_lookback_rows"
    ] = 25

    assert (
        validate_training_candidate_contract(
            candidate
        )
        is False
    )


def test_validator_rejects_extra_identity_fields() -> None:
    candidate = (
        build_training_candidate_contract()
        .to_dict()
    )

    candidate[
        "owner_user_id"
    ] = "private-user"

    assert (
        validate_training_candidate_contract(
            candidate
        )
        is False
    )


def test_contract_status_preserves_safety_boundary() -> None:
    status = (
        training_candidate_contract_status()
    )

    assert status[
        "immutable"
    ] is True

    for field in (
        "execution_enabled",
        "strategy_promotion_enabled",
        "model_mutation_enabled",
        "database_writes_enabled",
        "paper_execution_enabled",
        "broker_execution_enabled",
        "live_execution_enabled",
        "customer_identity_allowed",
        "session_identity_allowed",
        "authentication_data_allowed",
        "portfolio_data_allowed",
        "order_data_allowed",
    ):
        assert status[field] is False
