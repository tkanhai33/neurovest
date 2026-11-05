from __future__ import annotations

from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from pydantic import (
    BaseModel,
    ConfigDict,
)

from backend.app.stacks.identity_auth.api_dependencies import (
    require_authenticated_principal,
)

from backend.app.stacks.strategy_candidate_sandbox.captured_candidate_review_adapter import (
    CandidateReviewRejectedError,
    build_reviewed_training_candidate_preview,
)


router = APIRouter()


class CapturedCandidateReviewPreviewRequest(
    BaseModel
):
    model_config = ConfigDict(
        extra="forbid",
    )

    candidate_id: str
    approved: bool
    strategy_name: str
    decision_rule: str
    short_lookback_rows: int
    long_lookback_rows: int
    minimum_signal_strength: float


def _authenticated_subject(
    principal: Any,
) -> str:

    subject = str(
        getattr(
            principal,
            "subject",
            "",
        )
        or ""
    ).strip()

    if not subject:

        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Authentication required"
            ),
        )

    return subject


def _review_rejection_status(
    exc: CandidateReviewRejectedError,
) -> int:

    reason = str(
        exc
    ).strip().lower()


    if reason == "candidate not found":

        return (
            status.HTTP_404_NOT_FOUND
        )


    if (
        "candidate owner is missing"
        in reason
    ):

        return (
            status.HTTP_403_FORBIDDEN
        )


    if (
        "candidate owner does not match authenticated subject"
        in reason
    ):

        return (
            status.HTTP_403_FORBIDDEN
        )


    if (
        "explicit user approval is required"
        in reason
    ):

        return (
            status.HTTP_409_CONFLICT
        )


    if any(
        token
        in reason
        for token
        in (
            "candidate status is not reviewable",
            "candidate origin is not reviewable",
            "candidate approval contract is invalid",
            "candidate sandbox contract is invalid",
            "candidate promotion-review contract is invalid",
        )
    ):

        return (
            status.HTTP_409_CONFLICT
        )


    if any(
        token
        in reason
        for token
        in (
            "strategy_name is required",
            "decision_rule is required",
            "reviewed training candidate contract is invalid",
        )
    ):

        return (
            status.HTTP_422_UNPROCESSABLE_ENTITY
        )


    return (
        status.HTTP_422_UNPROCESSABLE_ENTITY
    )


@router.post(
    "/api/v1/strategy-candidates/review-preview",
)
def preview_authenticated_candidate_review(
    payload: CapturedCandidateReviewPreviewRequest,
    principal: Any = Depends(
        require_authenticated_principal
    ),
) -> dict[str, Any]:

    subject = _authenticated_subject(
        principal
    )


    try:

        return (
            build_reviewed_training_candidate_preview(
                candidate_id=(
                    payload.candidate_id
                ),
                authenticated_subject=(
                    subject
                ),
                approved=(
                    payload.approved
                ),
                strategy_name=(
                    payload.strategy_name
                ),
                decision_rule=(
                    payload.decision_rule
                ),
                short_lookback_rows=(
                    payload.short_lookback_rows
                ),
                long_lookback_rows=(
                    payload.long_lookback_rows
                ),
                minimum_signal_strength=(
                    payload.minimum_signal_strength
                ),
            )
        )

    except CandidateReviewRejectedError as exc:

        raise HTTPException(
            status_code=(
                _review_rejection_status(
                    exc
                )
            ),
            detail=str(
                exc
            ),
        ) from exc

    except HTTPException:

        raise

    except Exception as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Candidate review preview unavailable"
            ),
        ) from exc
