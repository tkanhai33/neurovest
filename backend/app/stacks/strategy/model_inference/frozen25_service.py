from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import hashlib

import joblib
import numpy as np
import pandas as pd


EXPECTED_MODEL_SHA256 = (
    "a77199c7306afdc2d2b5cd0a956312aef34b555ea1b50001b4ed6f6679b5e9cf"
)


DEFAULT_THRESHOLD = 0.555


MODEL_FEATURES = (
    "return_1d",
    "return_5d",
    "return_10d",
    "return_20d",
    "volatility_5d",
    "volatility_20d",
    "range_fraction",
    "close_to_sma_5",
    "close_to_sma_20",
    "close_to_sma_50",
    "volume_change_1d",
    "volume_ratio_20d",
    "research_053_cumulative_momentum_12m_skip_1m",
    "research_053_cumulative_rank",
    "research_053_mean_momentum_12m_skip_1m",
    "research_053_risk_adjusted_momentum_12m_skip_1m",
    "research_053_risk_adjusted_rank",
    "research_053_volatility_12m_skip_1m",
    "research_contract_replay_spec_ssrn_3247865_064_sector_momentum_rotation",
    "research_contract_replay_spec_ssrn_3247865_074_real_estate_momentum_regional_approach",
    "research_mean_reversion_pressure",
    "research_momentum_consensus",
    "research_momentum_cross_section_rank",
    "research_risk_adjusted_momentum",
    "research_volatility_regime",
)


@dataclass(frozen=True)
class Frozen25Prediction:

    probability: float
    threshold: float
    positive: bool


class Frozen25ReadOnlyInferenceService:

    def __init__(
        self,
        *,
        model_path: str | Path,
        threshold: float = DEFAULT_THRESHOLD,
    ) -> None:

        self._model_path = Path(
            model_path
        ).resolve()

        self._threshold = float(
            threshold
        )

        if not self._model_path.is_file():

            raise FileNotFoundError(
                self._model_path
            )


        actual_sha256 = hashlib.sha256(
            self._model_path.read_bytes()
        ).hexdigest()


        if actual_sha256 != EXPECTED_MODEL_SHA256:

            raise ValueError(
                "Frozen model SHA256 mismatch: "
                +
                actual_sha256
            )


        loaded = joblib.load(
            self._model_path
        )


        model = loaded


        if isinstance(
            loaded,
            dict,
        ):

            for key in (
                "model",
                "estimator",
                "classifier",
                "pipeline",
                "trained_model",
            ):

                candidate = loaded.get(
                    key
                )

                if (
                    candidate is not None
                    and
                    hasattr(
                        candidate,
                        "predict_proba",
                    )
                ):

                    model = candidate
                    break


        if not hasattr(
            model,
            "predict_proba",
        ):

            raise TypeError(
                "Frozen estimator does not expose predict_proba()."
            )


        self._model = model
        self._model_sha256 = actual_sha256


    @property
    def threshold(self) -> float:

        return self._threshold


    @property
    def model_sha256(self) -> str:

        return self._model_sha256


    @property
    def estimator_type(self) -> str:

        return (
            f"{type(self._model).__module__}."
            f"{type(self._model).__name__}"
        )


    def feature_columns(
        self,
    ) -> Sequence[str]:

        return MODEL_FEATURES


    def readiness(
        self,
    ) -> dict:

        return {
            "ready":
                True,

            "read_only":
                True,

            "feature_count":
                len(
                    MODEL_FEATURES
                ),

            "threshold":
                self._threshold,

            "model_sha256":
                self._model_sha256,

            "estimator_type":
                self.estimator_type,

            "execution_enabled":
                False,

            "broker_enabled":
                False,

            "snaptrade_enabled":
                False,

            "runtime_activated":
                False,
        }


    def _validate_frame(
        self,
        frame: pd.DataFrame,
    ) -> pd.DataFrame:

        missing = [
            feature
            for feature in MODEL_FEATURES
            if feature not in frame.columns
        ]


        if missing:

            raise ValueError(
                "Missing model features: "
                +
                repr(
                    missing
                )
            )


        candidate = frame[
            list(
                MODEL_FEATURES
            )
        ].copy()


        if list(
            candidate.columns
        ) != list(
            MODEL_FEATURES
        ):

            raise ValueError(
                "Frozen model feature ordering mismatch."
            )


        if candidate.isna().any().any():

            raise ValueError(
                "Frozen model input contains NaN."
            )


        return candidate


    def predict_probabilities(
        self,
        frame: pd.DataFrame,
    ) -> np.ndarray:

        candidate = self._validate_frame(
            frame
        )


        probabilities = self._model.predict_proba(
            candidate
        )


        if (
            getattr(
                probabilities,
                "ndim",
                0,
            )
            !=
            2
            or
            probabilities.shape[1]
            <
            2
        ):

            raise ValueError(
                "Unexpected predict_proba output shape."
            )


        return np.asarray(
            probabilities[
                :,
                1
            ],
            dtype=float,
        )


    def predict(
        self,
        frame: pd.DataFrame,
    ) -> list[Frozen25Prediction]:

        probabilities = self.predict_probabilities(
            frame
        )


        return [
            Frozen25Prediction(
                probability=float(
                    probability
                ),

                threshold=self._threshold,

                positive=bool(
                    probability
                    >=
                    self._threshold
                ),
            )
            for probability in probabilities
        ]
