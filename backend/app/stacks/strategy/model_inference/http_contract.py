from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

import math

import pandas as pd

from .frozen25_service import MODEL_FEATURES


HTTP_CONTRACT_VERSION = "frozen25-readonly-v1"


HTTP_METHOD = "POST"


PROPOSED_PATH = (
    "/api/v1/strategy/model-inference/frozen25"
)


AUTHENTICATION_REQUIRED = True


READ_ONLY = True


ROUTE_REGISTERED = False


RUNTIME_ACTIVATED = False


DATABASE_MUTATION = False


BROKER_EXECUTION = False


SNAPTRADE_CONTACT = False


MAX_ROWS_PER_REQUEST = 100


@dataclass(frozen=True)
class Frozen25HttpPrediction:

    probability: float
    threshold: float
    positive: bool


@dataclass(frozen=True)
class Frozen25HttpResponse:

    contract_version: str
    read_only: bool
    feature_count: int
    row_count: int
    predictions: tuple[Frozen25HttpPrediction, ...]


class Frozen25HttpContractError(
    ValueError
):
    pass


def contract_metadata() -> dict[str, Any]:

    return {
        "contract_version":
            HTTP_CONTRACT_VERSION,

        "http_method":
            HTTP_METHOD,

        "proposed_path":
            PROPOSED_PATH,

        "authentication_required":
            AUTHENTICATION_REQUIRED,

        "read_only":
            READ_ONLY,

        "route_registered":
            ROUTE_REGISTERED,

        "runtime_activated":
            RUNTIME_ACTIVATED,

        "database_mutation":
            DATABASE_MUTATION,

        "broker_execution":
            BROKER_EXECUTION,

        "snaptrade_contact":
            SNAPTRADE_CONTACT,

        "feature_count":
            len(
                MODEL_FEATURES
            ),

        "max_rows_per_request":
            MAX_ROWS_PER_REQUEST,
    }


def _validate_row_mapping(
    row: Mapping[str, Any],
) -> dict[str, float]:

    missing = [
        feature
        for feature in MODEL_FEATURES
        if feature not in row
    ]


    if missing:

        raise Frozen25HttpContractError(
            "Missing required features: "
            +
            repr(
                missing
            )
        )


    extras = [
        key
        for key in row.keys()
        if key not in MODEL_FEATURES
    ]


    if extras:

        raise Frozen25HttpContractError(
            "Unexpected input fields: "
            +
            repr(
                extras
            )
        )


    normalized = {}


    for feature in MODEL_FEATURES:

        value = row[
            feature
        ]


        if isinstance(
            value,
            bool,
        ):

            raise Frozen25HttpContractError(
                f"Boolean not allowed for feature: {feature}"
            )


        try:

            numeric = float(
                value
            )

        except (
            TypeError,
            ValueError,
        ):

            raise Frozen25HttpContractError(
                f"Feature is not numeric: {feature}"
            )


        if not math.isfinite(
            numeric
        ):

            raise Frozen25HttpContractError(
                f"Feature is not finite: {feature}"
            )


        normalized[
            feature
        ] = numeric


    return normalized


def request_payload_to_frame(
    payload: Mapping[str, Any],
) -> pd.DataFrame:

    if not isinstance(
        payload,
        Mapping,
    ):

        raise Frozen25HttpContractError(
            "Request payload must be an object."
        )


    allowed_top_level = {
        "rows",
    }


    extras = [
        key
        for key in payload.keys()
        if key not in allowed_top_level
    ]


    if extras:

        raise Frozen25HttpContractError(
            "Unexpected request fields: "
            +
            repr(
                extras
            )
        )


    rows = payload.get(
        "rows"
    )


    if not isinstance(
        rows,
        list,
    ):

        raise Frozen25HttpContractError(
            "'rows' must be a list."
        )


    if not rows:

        raise Frozen25HttpContractError(
            "'rows' must contain at least one item."
        )


    if len(
        rows
    ) > MAX_ROWS_PER_REQUEST:

        raise Frozen25HttpContractError(
            "Request exceeds maximum row count."
        )


    normalized_rows = []


    for index, row in enumerate(
        rows
    ):

        if not isinstance(
            row,
            Mapping,
        ):

            raise Frozen25HttpContractError(
                f"Row {index} must be an object."
            )


        normalized_rows.append(
            _validate_row_mapping(
                row
            )
        )


    frame = pd.DataFrame(
        normalized_rows,
        columns=list(
            MODEL_FEATURES
        ),
    )


    if list(
        frame.columns
    ) != list(
        MODEL_FEATURES
    ):

        raise Frozen25HttpContractError(
            "Feature ordering mismatch."
        )


    return frame


def prediction_response(
    *,
    probabilities,
    threshold: float,
) -> Frozen25HttpResponse:

    predictions = []


    for value in probabilities:

        probability = float(
            value
        )


        if not math.isfinite(
            probability
        ):

            raise Frozen25HttpContractError(
                "Prediction probability is not finite."
            )


        if not (
            0.0
            <=
            probability
            <=
            1.0
        ):

            raise Frozen25HttpContractError(
                "Prediction probability is outside [0,1]."
            )


        predictions.append(
            Frozen25HttpPrediction(
                probability=
                    probability,

                threshold=
                    float(
                        threshold
                    ),

                positive=
                    bool(
                        probability
                        >=
                        threshold
                    ),
            )
        )


    return Frozen25HttpResponse(
        contract_version=
            HTTP_CONTRACT_VERSION,

        read_only=
            True,

        feature_count=
            len(
                MODEL_FEATURES
            ),

        row_count=
            len(
                predictions
            ),

        predictions=
            tuple(
                predictions
            ),
    )


def response_to_dict(
    response: Frozen25HttpResponse,
) -> dict[str, Any]:

    result = asdict(
        response
    )


    result[
        "predictions"
    ] = [
        dict(
            item
        )
        for item in result[
            "predictions"
        ]
    ]


    return result
