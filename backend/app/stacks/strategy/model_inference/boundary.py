from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .frozen25_service import (
    Frozen25Prediction,
    Frozen25ReadOnlyInferenceService,
)


MODEL_RELATIVE_PATH = (
    "runtime/training/"
    "generation279_automated_isolated_challenger_controller_"
    "20260809_192112/"
    "best_models/challenger_02952.joblib"
)


class Frozen25ApplicationBoundary:

    def __init__(
        self,
        *,
        repository_root: str | Path,
    ) -> None:

        root = Path(
            repository_root
        ).resolve()


        model_path = (
            root
            /
            MODEL_RELATIVE_PATH
        )


        self._service = (
            Frozen25ReadOnlyInferenceService(
                model_path=model_path,
            )
        )


    def readiness(
        self,
    ) -> dict[str, Any]:

        result = dict(
            self._service.readiness()
        )


        result.update(
            {
                "application_boundary":
                    True,

                "http_route_installed":
                    False,

                "execution_capability":
                    False,

                "database_capability":
                    False,

                "runtime_activation":
                    False,
            }
        )


        return result


    def feature_columns(
        self,
    ) -> tuple[str, ...]:

        return tuple(
            self._service.feature_columns()
        )


    def predict_probabilities(
        self,
        frame: pd.DataFrame,
    ):

        return (
            self._service
            .predict_probabilities(
                frame
            )
        )


    def predict(
        self,
        frame: pd.DataFrame,
    ) -> list[Frozen25Prediction]:

        return self._service.predict(
            frame
        )
