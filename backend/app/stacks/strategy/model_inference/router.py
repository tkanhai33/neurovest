from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, status

from backend.app.stacks.identity_auth.api_dependencies import require_authenticated_principal

from .boundary import Frozen25ApplicationBoundary
from .http_contract import (
    PROPOSED_PATH,
    Frozen25HttpContractError,
    prediction_response,
    request_payload_to_frame,
    response_to_dict,
)


router = APIRouter()


def repository_root() -> Path:

    return Path(
        __file__
    ).resolve().parents[
        5
    ]


def get_boundary() -> Frozen25ApplicationBoundary:

    return Frozen25ApplicationBoundary(
        repository_root=
            repository_root()
    )


@router.post(
    PROPOSED_PATH,
)
def frozen25_read_only_inference(
    payload: dict[str, Any] = Body(...),
    principal: str = Depends(
        require_authenticated_principal
    ),
    boundary: Frozen25ApplicationBoundary = Depends(
        get_boundary
    ),
):

    if not principal:

        raise HTTPException(
            status_code=
                status.HTTP_401_UNAUTHORIZED,

            detail=
                "Authentication required.",
        )

    try:

        frame = request_payload_to_frame(
            payload
        )

        probabilities = (
            boundary.predict_probabilities(
                frame
            )
        )

        response = prediction_response(
            probabilities=
                probabilities,

            threshold=
                boundary.readiness()[
                    "threshold"
                ],
        )

        return response_to_dict(
            response
        )

    except Frozen25HttpContractError as exc:

        raise HTTPException(
            status_code=
                status.HTTP_422_UNPROCESSABLE_ENTITY,

            detail=
                str(
                    exc
                ),
        ) from exc

    except ValueError as exc:

        raise HTTPException(
            status_code=
                status.HTTP_422_UNPROCESSABLE_ENTITY,

            detail=
                str(
                    exc
                ),
        ) from exc
