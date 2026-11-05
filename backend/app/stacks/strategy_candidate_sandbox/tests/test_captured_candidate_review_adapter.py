from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.app.stacks.strategy_candidate_sandbox.captured_candidate_review_adapter import (
    CandidateReviewRejectedError,
    build_reviewed_training_candidate_preview,
)


CANDIDATE_ID = (
    "candidate_20260826_123456_abcdef12"
)


def _candidate(
    *,
    owner_user_id: str = "owner-a",
    status: str = "captured_pending_review",
    origin: str = "chat_ollama_proposal",
) -> dict:

    return {
        "candidate_id":
            CANDIDATE_ID,

        "created_at":
            "2026-08-26T00:00:00+00:00",

        "status":
            status,

        "origin":
            origin,

        "intent":
            "trading_conversation",

        "symbol":
            "AAPL",

        "owner_user_id":
            owner_user_id,

        "requires_user_approval":
            True,

        "requires_sandbox_test":
            True,

        "requires_promotion_review":
            True,

        "user_message":
            "Create a strategy for AAPL.",

        "assistant_proposal":
            "A strategy proposal.",
    }


def _write_candidate(
    root: Path,
    payload: dict,
) -> Path:

    root.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = (
        root
        / f"{CANDIDATE_ID}.json"
    )

    path.write_text(
        json.dumps(
            payload,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    return path


def _preview(
    root: Path,
    **overrides,
):

    kwargs = {
        "candidate_id":
            CANDIDATE_ID,

        "authenticated_subject":
            "owner-a",

        "approved":
            True,

        "strategy_name":
            "Reviewed AAPL Strategy",

        "decision_rule":
            "moving_average_crossover",

        "short_lookback_rows":
            5,

        "long_lookback_rows":
            20,

        "minimum_signal_strength":
            0.0,

        "candidate_root":
            root,
    }

    kwargs.update(
        overrides
    )

    return (
        build_reviewed_training_candidate_preview(
            **kwargs
        )
    )


def test_owned_candidate_builds_preview_without_mutation(
    tmp_path: Path,
):

    candidate_root = (
        tmp_path
        / "strategy_candidates"
    )

    path = _write_candidate(
        candidate_root,
        _candidate(),
    )

    before = path.read_bytes()


    result = _preview(
        candidate_root
    )


    after = path.read_bytes()


    assert before == after

    assert (
        result["status"]
        == "qualified_preview_only"
    )

    assert (
        result["candidate_id"]
        == CANDIDATE_ID
    )

    assert (
        result[
            "training_candidate"
        ][
            "strategy_name"
        ]
        == "Reviewed AAPL Strategy"
    )

    assert (
        result[
            "training_candidate"
        ][
            "created_from"
        ]
        == "chat_candidate_review"
    )

    assert (
        "owner_user_id"
        not in result[
            "training_candidate"
        ]
    )

    assert (
        "user_message"
        not in result[
            "training_candidate"
        ]
    )

    assert (
        "assistant_proposal"
        not in result[
            "training_candidate"
        ]
    )

    assert (
        result[
            "candidate_mutated"
        ]
        is False
    )

    assert (
        result[
            "training_candidate_persisted"
        ]
        is False
    )

    assert (
        result[
            "training_started"
        ]
        is False
    )


def test_legacy_unowned_candidate_rejected(
    tmp_path: Path,
):

    candidate_root = (
        tmp_path
        / "strategy_candidates"
    )

    payload = _candidate()

    payload.pop(
        "owner_user_id"
    )

    _write_candidate(
        candidate_root,
        payload,
    )


    with pytest.raises(
        CandidateReviewRejectedError,
        match="candidate owner is missing",
    ):

        _preview(
            candidate_root
        )


def test_owner_mismatch_rejected(
    tmp_path: Path,
):

    candidate_root = (
        tmp_path
        / "strategy_candidates"
    )

    _write_candidate(
        candidate_root,
        _candidate(),
    )


    with pytest.raises(
        CandidateReviewRejectedError,
        match=(
            "candidate owner does not match "
            "authenticated subject"
        ),
    ):

        _preview(
            candidate_root,
            authenticated_subject="owner-b",
        )


def test_empty_authenticated_subject_rejected(
    tmp_path: Path,
):

    candidate_root = (
        tmp_path
        / "strategy_candidates"
    )

    _write_candidate(
        candidate_root,
        _candidate(),
    )


    with pytest.raises(
        CandidateReviewRejectedError,
        match="authenticated_subject is required",
    ):

        _preview(
            candidate_root,
            authenticated_subject="",
        )


def test_explicit_approval_required(
    tmp_path: Path,
):

    candidate_root = (
        tmp_path
        / "strategy_candidates"
    )

    _write_candidate(
        candidate_root,
        _candidate(),
    )


    with pytest.raises(
        CandidateReviewRejectedError,
        match="explicit user approval is required",
    ):

        _preview(
            candidate_root,
            approved=False,
        )


def test_wrong_status_rejected(
    tmp_path: Path,
):

    candidate_root = (
        tmp_path
        / "strategy_candidates"
    )

    _write_candidate(
        candidate_root,
        _candidate(
            status="approved",
        ),
    )


    with pytest.raises(
        CandidateReviewRejectedError,
        match="candidate status is not reviewable",
    ):

        _preview(
            candidate_root
        )


def test_wrong_origin_rejected(
    tmp_path: Path,
):

    candidate_root = (
        tmp_path
        / "strategy_candidates"
    )

    _write_candidate(
        candidate_root,
        _candidate(
            origin="manual",
        ),
    )


    with pytest.raises(
        CandidateReviewRejectedError,
        match="candidate origin is not reviewable",
    ):

        _preview(
            candidate_root
        )


def test_candidate_path_traversal_rejected(
    tmp_path: Path,
):

    candidate_root = (
        tmp_path
        / "strategy_candidates"
    )

    candidate_root.mkdir(
        parents=True,
        exist_ok=True,
    )


    with pytest.raises(
        CandidateReviewRejectedError,
        match="candidate_id is invalid",
    ):

        build_reviewed_training_candidate_preview(
            candidate_id="../../etc/passwd",
            authenticated_subject="owner-a",
            approved=True,
            strategy_name="Strategy",
            decision_rule=(
                "moving_average_crossover"
            ),
            short_lookback_rows=5,
            long_lookback_rows=20,
            minimum_signal_strength=0.0,
            candidate_root=candidate_root,
        )
