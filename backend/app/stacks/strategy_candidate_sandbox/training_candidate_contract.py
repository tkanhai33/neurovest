"""
Immutable bounded-training candidate contract.

This module defines the single canonical meaning of ``candidate_id`` for
bounded and adaptive training.

The contract is:

- deterministic;
- immutable after construction;
- free of user/session/customer identity;
- free of portfolio, order, broker, and authentication data;
- incapable of executing, promoting, or mutating strategies;
- suitable for persistence as sanitized training provenance.
"""

from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from typing import Any
import hashlib
import json
import math
import re


TRAINING_CANDIDATE_CONTRACT_VERSION = 1

_ALLOWED_DECISION_RULES = {
    "moving_average_crossover",
}

_ALLOWED_CREATED_FROM = {
    "manual",
    "qualification",
    "adaptive_training",
    "replay_metrics",
}

_FORBIDDEN_KEYS = {
    "owner_user_id",
    "owner_session_id",
    "user_id",
    "session_id",
    "requested_by",
    "requested_by_role",
    "email",
    "password",
    "access_token",
    "refresh_token",
    "credential",
    "credentials",
    "prompt",
    "message",
    "chat",
    "portfolio",
    "positions",
    "holdings",
    "orders",
    "account",
    "account_id",
    "broker",
    "broker_token",
    "live_order",
}

_CANDIDATE_ID_PATTERN = re.compile(
    r"^training_candidate_[0-9a-f]{24}$"
)

_CONTRACT_HASH_PATTERN = re.compile(
    r"^[0-9a-f]{64}$"
)


@dataclass(
    frozen=True,
    slots=True,
)
class TrainingCandidateContract:
    candidate_id: str
    candidate_version: int
    decision_rule: str
    short_lookback_rows: int
    long_lookback_rows: int
    minimum_signal_strength: float
    created_from: str
    contract_hash: str

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return asdict(
            self
        )


def _finite_float(
    value: Any,
) -> float:
    try:
        resolved = float(
            value
        )
    except (
        TypeError,
        ValueError,
    ) as error:
        raise ValueError(
            "minimum_signal_strength must be numeric"
        ) from error

    if not math.isfinite(
        resolved
    ):
        raise ValueError(
            "minimum_signal_strength must be finite"
        )

    return resolved


def _canonical_payload(
    *,
    candidate_version: int,
    decision_rule: str,
    short_lookback_rows: int,
    long_lookback_rows: int,
    minimum_signal_strength: float,
    created_from: str,
) -> dict[str, Any]:
    return {
        "candidate_version":
            candidate_version,

        "decision_rule":
            decision_rule,

        "short_lookback_rows":
            short_lookback_rows,

        "long_lookback_rows":
            long_lookback_rows,

        "minimum_signal_strength":
            round(
                minimum_signal_strength,
                12,
            ),

        "created_from":
            created_from,
    }


def _canonical_json(
    payload: dict[str, Any],
) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=False,
        allow_nan=False,
    )


def _contains_forbidden_key(
    value: Any,
) -> str | None:
    if isinstance(
        value,
        dict,
    ):
        for key, child in value.items():
            normalized = str(
                key
            ).strip().lower()

            if normalized in _FORBIDDEN_KEYS:
                return normalized

            nested = _contains_forbidden_key(
                child
            )

            if nested:
                return nested

    elif isinstance(
        value,
        list,
    ):
        for child in value:
            nested = _contains_forbidden_key(
                child
            )

            if nested:
                return nested

    return None


def build_training_candidate_contract(
    *,
    decision_rule: str = (
        "moving_average_crossover"
    ),
    short_lookback_rows: int = 5,
    long_lookback_rows: int = 20,
    minimum_signal_strength: float = 0.0,
    created_from: str = "manual",
    candidate_version: int = (
        TRAINING_CANDIDATE_CONTRACT_VERSION
    ),
) -> TrainingCandidateContract:
    normalized_rule = str(
        decision_rule
        or ""
    ).strip().lower()

    normalized_source = str(
        created_from
        or ""
    ).strip().lower()

    if not isinstance(
        candidate_version,
        int,
    ):
        raise ValueError(
            "candidate_version must be an integer"
        )

    if candidate_version != (
        TRAINING_CANDIDATE_CONTRACT_VERSION
    ):
        raise ValueError(
            "unsupported training candidate version"
        )

    if normalized_rule not in (
        _ALLOWED_DECISION_RULES
    ):
        raise ValueError(
            "unsupported decision_rule"
        )

    if normalized_source not in (
        _ALLOWED_CREATED_FROM
    ):
        raise ValueError(
            "unsupported created_from value"
        )

    if not isinstance(
        short_lookback_rows,
        int,
    ):
        raise ValueError(
            "short_lookback_rows must be an integer"
        )

    if not isinstance(
        long_lookback_rows,
        int,
    ):
        raise ValueError(
            "long_lookback_rows must be an integer"
        )

    if short_lookback_rows < 2:
        raise ValueError(
            "short_lookback_rows must be at least 2"
        )

    if long_lookback_rows < 3:
        raise ValueError(
            "long_lookback_rows must be at least 3"
        )

    if (
        short_lookback_rows
        >= long_lookback_rows
    ):
        raise ValueError(
            "short_lookback_rows must be smaller "
            "than long_lookback_rows"
        )

    if long_lookback_rows > 5000:
        raise ValueError(
            "long_lookback_rows exceeds the "
            "bounded maximum"
        )

    normalized_strength = (
        _finite_float(
            minimum_signal_strength
        )
    )

    if not (
        0.0
        <= normalized_strength
        <= 1.0
    ):
        raise ValueError(
            "minimum_signal_strength must be "
            "between 0 and 1"
        )

    payload = _canonical_payload(
        candidate_version=(
            candidate_version
        ),
        decision_rule=(
            normalized_rule
        ),
        short_lookback_rows=(
            short_lookback_rows
        ),
        long_lookback_rows=(
            long_lookback_rows
        ),
        minimum_signal_strength=(
            normalized_strength
        ),
        created_from=(
            normalized_source
        ),
    )

    forbidden = _contains_forbidden_key(
        payload
    )

    if forbidden:
        raise ValueError(
            "training candidate contains "
            f"forbidden key: {forbidden}"
        )

    contract_hash = hashlib.sha256(
        _canonical_json(
            payload
        ).encode(
            "utf-8"
        )
    ).hexdigest()

    candidate_id = (
        "training_candidate_"
        + contract_hash[:24]
    )

    contract = TrainingCandidateContract(
        candidate_id=(
            candidate_id
        ),
        candidate_version=(
            candidate_version
        ),
        decision_rule=(
            normalized_rule
        ),
        short_lookback_rows=(
            short_lookback_rows
        ),
        long_lookback_rows=(
            long_lookback_rows
        ),
        minimum_signal_strength=(
            round(
                normalized_strength,
                12,
            )
        ),
        created_from=(
            normalized_source
        ),
        contract_hash=(
            contract_hash
        ),
    )

    if not validate_training_candidate_contract(
        contract.to_dict()
    ):
        raise ValueError(
            "generated training candidate contract "
            "failed validation"
        )

    return contract


def validate_training_candidate_contract(
    candidate: dict[str, Any],
) -> bool:
    if not isinstance(
        candidate,
        dict,
    ):
        return False

    expected_keys = {
        "candidate_id",
        "candidate_version",
        "decision_rule",
        "short_lookback_rows",
        "long_lookback_rows",
        "minimum_signal_strength",
        "created_from",
        "contract_hash",
    }

    if set(candidate) != expected_keys:
        return False

    forbidden = _contains_forbidden_key(
        candidate
    )

    if forbidden:
        return False

    candidate_id = candidate.get(
        "candidate_id"
    )

    contract_hash = candidate.get(
        "contract_hash"
    )

    if not isinstance(
        candidate_id,
        str,
    ):
        return False

    if not _CANDIDATE_ID_PATTERN.fullmatch(
        candidate_id
    ):
        return False

    if not isinstance(
        contract_hash,
        str,
    ):
        return False

    if not _CONTRACT_HASH_PATTERN.fullmatch(
        contract_hash
    ):
        return False

    candidate_version = candidate.get(
        "candidate_version"
    )

    if candidate_version != (
        TRAINING_CANDIDATE_CONTRACT_VERSION
    ):
        return False

    decision_rule = candidate.get(
        "decision_rule"
    )

    if decision_rule not in (
        _ALLOWED_DECISION_RULES
    ):
        return False

    created_from = candidate.get(
        "created_from"
    )

    if created_from not in (
        _ALLOWED_CREATED_FROM
    ):
        return False

    short_rows = candidate.get(
        "short_lookback_rows"
    )

    long_rows = candidate.get(
        "long_lookback_rows"
    )

    if not isinstance(
        short_rows,
        int,
    ):
        return False

    if not isinstance(
        long_rows,
        int,
    ):
        return False

    if short_rows < 2:
        return False

    if long_rows < 3:
        return False

    if short_rows >= long_rows:
        return False

    if long_rows > 5000:
        return False

    strength = candidate.get(
        "minimum_signal_strength"
    )

    if not isinstance(
        strength,
        (
            int,
            float,
        ),
    ):
        return False

    if not math.isfinite(
        float(
            strength
        )
    ):
        return False

    if not (
        0.0
        <= float(
            strength
        )
        <= 1.0
    ):
        return False

    payload = _canonical_payload(
        candidate_version=(
            candidate_version
        ),
        decision_rule=(
            decision_rule
        ),
        short_lookback_rows=(
            short_rows
        ),
        long_lookback_rows=(
            long_rows
        ),
        minimum_signal_strength=(
            float(
                strength
            )
        ),
        created_from=(
            created_from
        ),
    )

    expected_hash = hashlib.sha256(
        _canonical_json(
            payload
        ).encode(
            "utf-8"
        )
    ).hexdigest()

    if contract_hash != expected_hash:
        return False

    if candidate_id != (
        "training_candidate_"
        + expected_hash[:24]
    ):
        return False

    return True


def training_candidate_contract_status() -> dict[str, Any]:
    return {
        "contract_version":
            TRAINING_CANDIDATE_CONTRACT_VERSION,

        "candidate_identity":
            "deterministic_sha256",

        "immutable":
            True,

        "execution_enabled":
            False,

        "strategy_promotion_enabled":
            False,

        "model_mutation_enabled":
            False,

        "database_writes_enabled":
            False,

        "paper_execution_enabled":
            False,

        "broker_execution_enabled":
            False,

        "live_execution_enabled":
            False,

        "customer_identity_allowed":
            False,

        "session_identity_allowed":
            False,

        "authentication_data_allowed":
            False,

        "portfolio_data_allowed":
            False,

        "order_data_allowed":
            False,
    }


__all__ = [
    "TRAINING_CANDIDATE_CONTRACT_VERSION",
    "TrainingCandidateContract",
    "build_training_candidate_contract",
    "training_candidate_contract_status",
    "validate_training_candidate_contract",
]
