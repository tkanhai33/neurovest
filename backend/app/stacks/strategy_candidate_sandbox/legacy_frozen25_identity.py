"""
Legacy Frozen25 identity compatibility boundary.

Frozen25 challenger_02952 predates the modern
TrainingCandidateContract. Its historical modern contract inputs do not
exist and MUST NOT be fabricated.

This module therefore defines a separate deterministic identity contract
using only immutable lineage facts that have been independently proven.

This module:

* does not load the model;
* does not execute inference;
* does not access the database;
* does not perform training;
* does not activate runtime behavior;
* does not reinterpret model_sha256 as contract_hash.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from typing import Any


LEGACY_FROZEN25_IDENTITY_TYPE = (
    "legacy_frozen25"
)

LEGACY_FROZEN25_IDENTITY_VERSION = (
    1
)

LEGACY_FROZEN25_CANDIDATE_ID = (
    "challenger_02952"
)

LEGACY_FROZEN25_STRATEGY_NAME = (
    "Frozen25 / challenger_02952"
)

LEGACY_FROZEN25_MODEL_SHA256 = (
    "a77199c7306afdc2d2b5cd0a956312aef34b555ea1b50001b4ed6f6679b5e9cf"
)

LEGACY_FROZEN25_STRATEGY_FINGERPRINT = (
    "40a6c489519db0c9f4408ee14759d827c2aad56ceda62a2bcbd074f04ccc9131"
)


_SHA256_PATTERN = re.compile(
    r"^[0-9a-f]{64}$"
)


def _canonical_identity_payload(
    *,
    identity_version: int,
    identity_type: str,
    candidate_id: str,
    strategy_name: str,
    model_sha256: str,
) -> dict[str, Any]:

    return {
        "identity_version":
            identity_version,

        "identity_type":
            identity_type,

        "candidate_id":
            candidate_id,

        "strategy_name":
            strategy_name,

        "model_sha256":
            model_sha256,
    }


def _canonical_json(
    payload: Mapping[str, Any],
) -> str:

    return json.dumps(
        dict(
            payload
        ),
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
    )


def build_legacy_frozen25_fingerprint(
    *,
    identity_version: int,
    identity_type: str,
    candidate_id: str,
    strategy_name: str,
    model_sha256: str,
) -> str:

    payload = _canonical_identity_payload(
        identity_version=
            identity_version,

        identity_type=
            identity_type,

        candidate_id=
            candidate_id,

        strategy_name=
            strategy_name,

        model_sha256=
            model_sha256,
    )

    return hashlib.sha256(
        _canonical_json(
            payload
        ).encode(
            "utf-8"
        )
    ).hexdigest()


def validate_legacy_frozen25_identity(
    candidate: Mapping[str, Any],
) -> bool:
    """
    Validate the one proven legacy Frozen25 identity.

    contract_hash is intentionally not accepted as part of this legacy
    identity contract.
    """

    if not isinstance(
        candidate,
        Mapping,
    ):
        return False


    if candidate.get(
        "identity_type"
    ) != LEGACY_FROZEN25_IDENTITY_TYPE:
        return False


    identity_version = candidate.get(
        "identity_version"
    )


    if (
        not isinstance(
            identity_version,
            int,
        )
        or isinstance(
            identity_version,
            bool,
        )
        or identity_version
        != LEGACY_FROZEN25_IDENTITY_VERSION
    ):
        return False


    candidate_id = candidate.get(
        "candidate_id"
    )

    strategy_name = candidate.get(
        "strategy_name"
    )

    model_sha256 = candidate.get(
        "model_sha256"
    )


    if candidate_id != (
        LEGACY_FROZEN25_CANDIDATE_ID
    ):
        return False


    if strategy_name != (
        LEGACY_FROZEN25_STRATEGY_NAME
    ):
        return False


    if not isinstance(
        model_sha256,
        str,
    ):
        return False


    normalized_sha = (
        model_sha256
        .strip()
        .lower()
    )


    if not _SHA256_PATTERN.fullmatch(
        normalized_sha
    ):
        return False


    if normalized_sha != (
        LEGACY_FROZEN25_MODEL_SHA256
    ):
        return False


    # A modern contract_hash on this legacy identity would blur two
    # intentionally separate identity contracts.
    if candidate.get(
        "contract_hash"
    ) not in (
        None,
        "",
    ):
        return False


    computed = build_legacy_frozen25_fingerprint(
        identity_version=
            identity_version,

        identity_type=
            str(
                candidate.get(
                    "identity_type"
                )
            ),

        candidate_id=
            str(
                candidate_id
            ),

        strategy_name=
            str(
                strategy_name
            ),

        model_sha256=
            normalized_sha,
    )


    if computed != (
        LEGACY_FROZEN25_STRATEGY_FINGERPRINT
    ):
        return False


    supplied_fingerprint = candidate.get(
        "strategy_fingerprint"
    )


    if supplied_fingerprint not in (
        None,
        "",
        LEGACY_FROZEN25_STRATEGY_FINGERPRINT,
    ):
        return False


    return True


def legacy_frozen25_strategy_fingerprint(
    candidate: Mapping[str, Any],
) -> str:

    if not validate_legacy_frozen25_identity(
        candidate
    ):
        raise ValueError(
            "Invalid legacy Frozen25 identity."
        )

    return (
        LEGACY_FROZEN25_STRATEGY_FINGERPRINT
    )


def legacy_frozen25_identity_status() -> dict[str, Any]:

    return {
        "identity_type":
            LEGACY_FROZEN25_IDENTITY_TYPE,

        "identity_version":
            LEGACY_FROZEN25_IDENTITY_VERSION,

        "candidate_id":
            LEGACY_FROZEN25_CANDIDATE_ID,

        "strategy_name":
            LEGACY_FROZEN25_STRATEGY_NAME,

        "model_sha256":
            LEGACY_FROZEN25_MODEL_SHA256,

        "strategy_fingerprint":
            LEGACY_FROZEN25_STRATEGY_FINGERPRINT,

        "modern_contract_hash":
            None,

        "model_sha_is_contract_hash":
            False,

        "database_capability":
            False,

        "model_load_capability":
            False,

        "model_prediction_capability":
            False,

        "training_capability":
            False,

        "execution_capability":
            False,

        "runtime_activation":
            False,
    }


__all__ = [
    "LEGACY_FROZEN25_CANDIDATE_ID",
    "LEGACY_FROZEN25_IDENTITY_TYPE",
    "LEGACY_FROZEN25_IDENTITY_VERSION",
    "LEGACY_FROZEN25_MODEL_SHA256",
    "LEGACY_FROZEN25_STRATEGY_FINGERPRINT",
    "LEGACY_FROZEN25_STRATEGY_NAME",
    "build_legacy_frozen25_fingerprint",
    "legacy_frozen25_identity_status",
    "legacy_frozen25_strategy_fingerprint",
    "validate_legacy_frozen25_identity",
]
