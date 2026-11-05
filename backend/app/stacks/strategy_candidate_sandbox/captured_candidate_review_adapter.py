from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from backend.app.stacks.strategy_candidate_sandbox.training_candidate_contract import (
    build_training_candidate_contract,
    validate_training_candidate_contract,
)


_REPOSITORY_ROOT = Path(__file__).resolve().parents[4]

_DEFAULT_CANDIDATE_ROOT = (
    _REPOSITORY_ROOT
    / "runtime"
    / "strategy_candidates"
)

_CANDIDATE_ID_PATTERN = re.compile(
    r"^candidate_[0-9]{8}_[0-9]{6}_[0-9a-f]{8}$"
)

_EXPECTED_STATUS = (
    "captured_pending_review"
)

_EXPECTED_ORIGIN = (
    "chat_ollama_proposal"
)

_REVIEW_CREATED_FROM = (
    "chat_candidate_review"
)


class CandidateReviewRejectedError(
    ValueError
):
    pass


def _reject(
    reason: str,
) -> None:

    raise CandidateReviewRejectedError(
        reason
    )


def _normalize_required_text(
    value: Any,
    *,
    field: str,
) -> str:

    normalized = str(
        value
        or ""
    ).strip()

    if not normalized:

        _reject(
            f"{field} is required"
        )

    return normalized


def _resolve_candidate_path(
    *,
    candidate_id: str,
    candidate_root: Path,
) -> Path:

    normalized_id = (
        _normalize_required_text(
            candidate_id,
            field="candidate_id",
        )
    )

    if (
        _CANDIDATE_ID_PATTERN.fullmatch(
            normalized_id
        )
        is None
    ):

        _reject(
            "candidate_id is invalid"
        )


    root = candidate_root.resolve()

    candidate_path = (
        root
        / f"{normalized_id}.json"
    ).resolve()


    if candidate_path.parent != root:

        _reject(
            "candidate path is invalid"
        )


    return candidate_path


def _load_candidate(
    *,
    candidate_id: str,
    candidate_root: Path,
) -> dict[str, Any]:

    candidate_path = (
        _resolve_candidate_path(
            candidate_id=candidate_id,
            candidate_root=candidate_root,
        )
    )


    if not candidate_path.is_file():

        _reject(
            "candidate not found"
        )


    try:

        payload = json.loads(
            candidate_path.read_text(
                encoding="utf-8"
            )
        )

    except Exception as exc:

        raise CandidateReviewRejectedError(
            "candidate is not valid JSON"
        ) from exc


    if not isinstance(
        payload,
        dict,
    ):

        _reject(
            "candidate payload is invalid"
        )


    if (
        payload.get(
            "candidate_id"
        )
        != candidate_id
    ):

        _reject(
            "candidate identity mismatch"
        )


    return payload


def build_reviewed_training_candidate_preview(
    *,
    candidate_id: str,
    authenticated_subject: str,
    approved: bool,
    strategy_name: str,
    decision_rule: str,
    short_lookback_rows: int,
    long_lookback_rows: int,
    minimum_signal_strength: float,
    candidate_root: Path | None = None,
) -> dict[str, Any]:
    """
    Build a validated TrainingCandidateContract preview from an owned,
    captured Chat strategy candidate.

    This function is intentionally side-effect free with respect to:
    - candidate state;
    - candidate files;
    - training candidate persistence;
    - training runtime;
    - database state;
    - strategy registration or promotion.
    """

    subject = (
        _normalize_required_text(
            authenticated_subject,
            field="authenticated_subject",
        )
    )

    root = (
        Path(candidate_root)
        if candidate_root is not None
        else _DEFAULT_CANDIDATE_ROOT
    )


    candidate = _load_candidate(
        candidate_id=candidate_id,
        candidate_root=root,
    )


    if (
        candidate.get(
            "status"
        )
        != _EXPECTED_STATUS
    ):

        _reject(
            "candidate status is not reviewable"
        )


    if (
        candidate.get(
            "origin"
        )
        != _EXPECTED_ORIGIN
    ):

        _reject(
            "candidate origin is not reviewable"
        )


    owner_user_id = str(
        candidate.get(
            "owner_user_id"
        )
        or ""
    ).strip()


    if not owner_user_id:

        _reject(
            "candidate owner is missing"
        )


    if owner_user_id != subject:

        _reject(
            "candidate owner does not match authenticated subject"
        )


    if (
        candidate.get(
            "requires_user_approval"
        )
        is not True
    ):

        _reject(
            "candidate approval contract is invalid"
        )


    if (
        candidate.get(
            "requires_sandbox_test"
        )
        is not True
    ):

        _reject(
            "candidate sandbox contract is invalid"
        )


    if (
        candidate.get(
            "requires_promotion_review"
        )
        is not True
    ):

        _reject(
            "candidate promotion-review contract is invalid"
        )


    if approved is not True:

        _reject(
            "explicit user approval is required"
        )


    normalized_strategy_name = (
        _normalize_required_text(
            strategy_name,
            field="strategy_name",
        )
    )

    normalized_decision_rule = (
        _normalize_required_text(
            decision_rule,
            field="decision_rule",
        )
    )


    training_candidate = (
        build_training_candidate_contract(
            strategy_name=(
                normalized_strategy_name
            ),
            decision_rule=(
                normalized_decision_rule
            ),
            short_lookback_rows=(
                short_lookback_rows
            ),
            long_lookback_rows=(
                long_lookback_rows
            ),
            minimum_signal_strength=(
                minimum_signal_strength
            ),
            created_from=(
                _REVIEW_CREATED_FROM
            ),
        )
        .to_dict()
    )


    if not validate_training_candidate_contract(
        training_candidate
    ):

        _reject(
            "reviewed training candidate contract is invalid"
        )


    return {
        "status":
            "qualified_preview_only",

        "candidate_id":
            candidate_id,

        "training_candidate":
            training_candidate,

        "candidate_mutated":
            False,

        "training_candidate_persisted":
            False,

        "training_started":
            False,
    }
