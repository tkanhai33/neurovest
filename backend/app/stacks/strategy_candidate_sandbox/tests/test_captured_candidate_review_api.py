from __future__ import annotations

from importlib.util import (
    module_from_spec,
    spec_from_file_location,
)

from pathlib import Path
from types import SimpleNamespace

import pytest

from fastapi import (
    FastAPI,
    HTTPException,
)

from fastapi.testclient import (
    TestClient,
)

from backend.app.stacks.identity_auth.api_dependencies import (
    require_authenticated_principal,
)

from backend.app.stacks.strategy_candidate_sandbox.captured_candidate_review_adapter import (
    CandidateReviewRejectedError,
)


ROUTE_PATH = (
    Path(
        __file__
    ).resolve().parents[1]
    / "captured_candidate_review_api.py"
)


SPEC = spec_from_file_location(
    "_neurovest_review_v1r2_sandbox_api",
    ROUTE_PATH,
)


assert SPEC is not None
assert SPEC.loader is not None


MODULE = module_from_spec(
    SPEC
)


SPEC.loader.exec_module(
    MODULE
)


ENDPOINT_PATH = (
    "/api/v1/strategy-candidates/review-preview"
)


VALID_PAYLOAD = {
    "candidate_id":
        "candidate_20260826_123456_abcdef12",

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
}


def _app(
    *,
    subject: str = "owner-a",
):

    app = FastAPI()

    app.include_router(
        MODULE.router
    )


    def principal():

        return SimpleNamespace(
            subject=subject
        )


    app.dependency_overrides[
        require_authenticated_principal
    ] = principal


    return app


def _client(
    *,
    subject: str = "owner-a",
):

    return TestClient(
        _app(
            subject=subject
        )
    )


def _qualified_preview():

    return {
        "status":
            "qualified_preview_only",

        "candidate_id":
            VALID_PAYLOAD[
                "candidate_id"
            ],

        "training_candidate": {
            "strategy_name":
                VALID_PAYLOAD[
                    "strategy_name"
                ],

            "created_from":
                "chat_candidate_review",
        },

        "candidate_mutated":
            False,

        "training_candidate_persisted":
            False,

        "training_started":
            False,
    }


def test_success_maps_200(
    monkeypatch,
):

    seen = {}


    def fake_adapter(
        **kwargs,
    ):

        seen.update(
            kwargs
        )

        return (
            _qualified_preview()
        )


    monkeypatch.setattr(
        MODULE,
        "build_reviewed_training_candidate_preview",
        fake_adapter,
    )


    response = _client().post(
        ENDPOINT_PATH,
        json=VALID_PAYLOAD,
    )


    assert response.status_code == 200

    data = response.json()


    assert (
        data[
            "status"
        ]
        == "qualified_preview_only"
    )

    assert (
        data[
            "candidate_mutated"
        ]
        is False
    )

    assert (
        data[
            "training_candidate_persisted"
        ]
        is False
    )

    assert (
        data[
            "training_started"
        ]
        is False
    )

    assert (
        seen[
            "authenticated_subject"
        ]
        == "owner-a"
    )

    assert (
        seen[
            "approved"
        ]
        is True
    )

    assert (
        seen[
            "candidate_id"
        ]
        == VALID_PAYLOAD[
            "candidate_id"
        ]
    )


def test_missing_authentication_maps_401():

    app = FastAPI()

    app.include_router(
        MODULE.router
    )


    def reject_auth():

        raise HTTPException(
            status_code=401,
            detail=(
                "Authentication required"
            ),
        )


    app.dependency_overrides[
        require_authenticated_principal
    ] = reject_auth


    response = TestClient(
        app
    ).post(
        ENDPOINT_PATH,
        json=VALID_PAYLOAD,
    )


    assert response.status_code == 401


def test_candidate_not_found_maps_404(
    monkeypatch,
):

    def fake_adapter(
        **kwargs,
    ):

        raise CandidateReviewRejectedError(
            "candidate not found"
        )


    monkeypatch.setattr(
        MODULE,
        "build_reviewed_training_candidate_preview",
        fake_adapter,
    )


    response = _client().post(
        ENDPOINT_PATH,
        json=VALID_PAYLOAD,
    )


    assert response.status_code == 404


def test_owner_missing_maps_403(
    monkeypatch,
):

    def fake_adapter(
        **kwargs,
    ):

        raise CandidateReviewRejectedError(
            "candidate owner is missing"
        )


    monkeypatch.setattr(
        MODULE,
        "build_reviewed_training_candidate_preview",
        fake_adapter,
    )


    response = _client().post(
        ENDPOINT_PATH,
        json=VALID_PAYLOAD,
    )


    assert response.status_code == 403


def test_owner_mismatch_maps_403(
    monkeypatch,
):

    def fake_adapter(
        **kwargs,
    ):

        raise CandidateReviewRejectedError(
            "candidate owner does not match authenticated subject"
        )


    monkeypatch.setattr(
        MODULE,
        "build_reviewed_training_candidate_preview",
        fake_adapter,
    )


    response = _client().post(
        ENDPOINT_PATH,
        json=VALID_PAYLOAD,
    )


    assert response.status_code == 403


def test_candidate_not_reviewable_maps_409(
    monkeypatch,
):

    def fake_adapter(
        **kwargs,
    ):

        raise CandidateReviewRejectedError(
            "candidate status is not reviewable"
        )


    monkeypatch.setattr(
        MODULE,
        "build_reviewed_training_candidate_preview",
        fake_adapter,
    )


    response = _client().post(
        ENDPOINT_PATH,
        json=VALID_PAYLOAD,
    )


    assert response.status_code == 409


def test_explicit_approval_missing_maps_409(
    monkeypatch,
):

    def fake_adapter(
        **kwargs,
    ):

        raise CandidateReviewRejectedError(
            "explicit user approval is required"
        )


    monkeypatch.setattr(
        MODULE,
        "build_reviewed_training_candidate_preview",
        fake_adapter,
    )


    payload = dict(
        VALID_PAYLOAD
    )

    payload[
        "approved"
    ] = False


    response = _client().post(
        ENDPOINT_PATH,
        json=payload,
    )


    assert response.status_code == 409


def test_invalid_semantics_maps_422(
    monkeypatch,
):

    def fake_adapter(
        **kwargs,
    ):

        raise CandidateReviewRejectedError(
            "reviewed training candidate contract is invalid"
        )


    monkeypatch.setattr(
        MODULE,
        "build_reviewed_training_candidate_preview",
        fake_adapter,
    )


    response = _client().post(
        ENDPOINT_PATH,
        json=VALID_PAYLOAD,
    )


    assert response.status_code == 422
