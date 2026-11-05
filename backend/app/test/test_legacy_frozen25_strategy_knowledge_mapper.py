from __future__ import annotations

import pytest


from backend.app.stacks.strategy_candidate_sandbox.legacy_frozen25_identity import (
    LEGACY_FROZEN25_CANDIDATE_ID,
    LEGACY_FROZEN25_IDENTITY_TYPE,
    LEGACY_FROZEN25_IDENTITY_VERSION,
    LEGACY_FROZEN25_MODEL_SHA256,
    LEGACY_FROZEN25_STRATEGY_FINGERPRINT,
    LEGACY_FROZEN25_STRATEGY_NAME,
    build_legacy_frozen25_fingerprint,
    legacy_frozen25_strategy_fingerprint,
    validate_legacy_frozen25_identity,
)

from backend.app.stacks.strategy_candidate_sandbox.strategy_knowledge_runtime_mapper import (
    map_runtime_candidate_to_strategy_knowledge,
)


def legacy_candidate():
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
    }


def test_legacy_fingerprint_matches_frozen_authority():

    candidate = legacy_candidate()

    fingerprint = build_legacy_frozen25_fingerprint(
        identity_version=
            candidate[
                "identity_version"
            ],

        identity_type=
            candidate[
                "identity_type"
            ],

        candidate_id=
            candidate[
                "candidate_id"
            ],

        strategy_name=
            candidate[
                "strategy_name"
            ],

        model_sha256=
            candidate[
                "model_sha256"
            ],
    )

    assert fingerprint == (
        LEGACY_FROZEN25_STRATEGY_FINGERPRINT
    )


def test_valid_legacy_identity_has_no_modern_contract_hash():

    candidate = legacy_candidate()

    assert "contract_hash" not in candidate

    assert (
        validate_legacy_frozen25_identity(
            candidate
        )
        is True
    )

    assert (
        legacy_frozen25_strategy_fingerprint(
            candidate
        )
        == LEGACY_FROZEN25_STRATEGY_FINGERPRINT
    )


def test_legacy_mapper_uses_legacy_fingerprint():

    candidate = legacy_candidate()

    record = (
        map_runtime_candidate_to_strategy_knowledge(
            candidate
        )
    )

    assert record.strategy_id == (
        LEGACY_FROZEN25_CANDIDATE_ID
    )

    assert record.strategy_name == (
        LEGACY_FROZEN25_STRATEGY_NAME
    )

    assert record.name == (
        LEGACY_FROZEN25_STRATEGY_NAME
    )

    assert record.strategy_fingerprint == (
        LEGACY_FROZEN25_STRATEGY_FINGERPRINT
    )


def test_legacy_candidate_may_supply_matching_fingerprint():

    candidate = legacy_candidate()

    candidate[
        "strategy_fingerprint"
    ] = (
        LEGACY_FROZEN25_STRATEGY_FINGERPRINT
    )

    assert (
        validate_legacy_frozen25_identity(
            candidate
        )
        is True
    )


def test_wrong_candidate_id_rejected():

    candidate = legacy_candidate()

    candidate[
        "candidate_id"
    ] = "challenger_06627"

    assert (
        validate_legacy_frozen25_identity(
            candidate
        )
        is False
    )

    with pytest.raises(
        ValueError
    ):

        map_runtime_candidate_to_strategy_knowledge(
            candidate
        )


def test_wrong_strategy_name_rejected():

    candidate = legacy_candidate()

    candidate[
        "strategy_name"
    ] = "Frozen25"

    assert (
        validate_legacy_frozen25_identity(
            candidate
        )
        is False
    )


def test_wrong_model_sha_rejected():

    candidate = legacy_candidate()

    candidate[
        "model_sha256"
    ] = "0" * 64

    assert (
        validate_legacy_frozen25_identity(
            candidate
        )
        is False
    )


def test_modern_contract_hash_is_rejected_on_legacy_identity():

    candidate = legacy_candidate()

    candidate[
        "contract_hash"
    ] = "1" * 64

    assert (
        validate_legacy_frozen25_identity(
            candidate
        )
        is False
    )


def test_wrong_supplied_legacy_fingerprint_rejected():

    candidate = legacy_candidate()

    candidate[
        "strategy_fingerprint"
    ] = "2" * 64

    assert (
        validate_legacy_frozen25_identity(
            candidate
        )
        is False
    )


def test_modern_mapper_behavior_is_preserved():

    candidate = {
        "candidate_id":
            "training_candidate_123456789012345678901234",

        "contract_hash":
            "a" * 64,

        "strategy_name":
            "Modern Test Strategy",

        "strategy_family":
            "test_family",

        "symbols":
            [
                "TEST.TO",
            ],
    }

    record = (
        map_runtime_candidate_to_strategy_knowledge(
            candidate
        )
    )

    assert record.strategy_id == (
        candidate[
            "candidate_id"
        ]
    )

    assert record.strategy_fingerprint == (
        candidate[
            "contract_hash"
        ]
    )

    assert record.strategy_name == (
        candidate[
            "strategy_name"
        ]
    )

    assert record.name == (
        candidate[
            "strategy_name"
        ]
    )

    assert record.strategy_family == (
        "test_family"
    )

    assert record.symbols == [
        "TEST.TO",
    ]


def test_modern_candidate_without_contract_hash_still_rejected():

    candidate = {
        "candidate_id":
            "training_candidate_123456789012345678901234",

        "strategy_name":
            "Modern Test Strategy",
    }

    with pytest.raises(
        ValueError,
        match="contract_hash",
    ):

        map_runtime_candidate_to_strategy_knowledge(
            candidate
        )


def test_unknown_identity_type_does_not_bypass_modern_contract():

    candidate = {
        "identity_type":
            "something_else",

        "candidate_id":
            "challenger_02952",

        "strategy_name":
            LEGACY_FROZEN25_STRATEGY_NAME,

        "model_sha256":
            LEGACY_FROZEN25_MODEL_SHA256,
    }

    with pytest.raises(
        ValueError,
        match="contract_hash",
    ):

        map_runtime_candidate_to_strategy_knowledge(
            candidate
        )
