"""
Dormant strategy-decision inference facade.

This module provides one explicit seam between the existing fixed-RSI
strategy path and a future learned inference path.

Important runtime contract:

* learned inference is disabled by default;
* this module does not import Frozen25 model-service code;
* this module does not load or execute a model;
* this module performs no database operations;
* this module performs no execution, broker, SnapTrade, paper, or live
  operations;
* the caller must explicitly inject any future learned decision callable;
* any disabled, unavailable, incomplete, or failed learned path falls
  back to the existing caller-provided fixed-RSI function.

Installation of this module alone therefore cannot activate learned
strategy decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping


CANONICAL_LEARNED_STRATEGY_NAME = (
    "Frozen25 / challenger_02952"
)

CANONICAL_CANDIDATE_ID = (
    "challenger_02952"
)


SignalResult = dict[str, Any]

FixedFallback = Callable[
    [],
    SignalResult,
]

LearnedDecision = Callable[
    [Any],
    SignalResult,
]


@dataclass(
    frozen=True,
)
class StrategyDecisionFacadeResult:
    """
    Result of facade selection.

    `signal` preserves the existing strategy-signal dictionary contract.
    """

    signal: SignalResult
    source: str
    strategy_name: str
    candidate_id: str | None
    learned_attempted: bool
    learned_used: bool
    fallback_used: bool
    fallback_reason: str | None

    def as_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "signal":
                dict(
                    self.signal
                ),

            "source":
                self.source,

            "strategy_name":
                self.strategy_name,

            "candidate_id":
                self.candidate_id,

            "learned_attempted":
                self.learned_attempted,

            "learned_used":
                self.learned_used,

            "fallback_used":
                self.fallback_used,

            "fallback_reason":
                self.fallback_reason,
        }


class StrategyDecisionInferenceFacade:
    """
    Disabled-by-default orchestration boundary.

    The facade deliberately accepts callables rather than constructing
    Frozen25 itself. That keeps model construction outside this module
    and prevents mere import or construction from activating inference.
    """

    def __init__(
        self,
        *,
        allow_learned_inference: bool = False,
    ) -> None:

        self._allow_learned_inference = bool(
            allow_learned_inference
        )


    @property
    def learned_inference_enabled(
        self,
    ) -> bool:

        return self._allow_learned_inference


    def readiness(
        self,
    ) -> dict[str, Any]:

        return {
            "ready":
                True,

            "facade":
                True,

            "canonical_strategy_name":
                CANONICAL_LEARNED_STRATEGY_NAME,

            "candidate_id":
                CANONICAL_CANDIDATE_ID,

            "learned_inference_enabled":
                self._allow_learned_inference,

            "default_runtime_behavior":
                "fixed_rsi_only",

            "fixed_rsi_fallback":
                True,

            "model_construction":
                False,

            "model_load":
                False,

            "model_prediction":
                False,

            "database_capability":
                False,

            "execution_capability":
                False,

            "broker_capability":
                False,

            "snaptrade_capability":
                False,

            "paper_capability":
                False,

            "live_capability":
                False,

            "training_capability":
                False,

            "controller_capability":
                False,
        }


    def decide(
        self,
        *,
        fixed_rsi_fallback: FixedFallback,
        feature_frame: Any = None,
        learned_decider: LearnedDecision | None = None,
    ) -> StrategyDecisionFacadeResult:
        """
        Select a strategy signal without owning model construction.

        Current safe/default behavior is always fixed RSI.

        Learned behavior requires ALL of:

        * explicit facade enablement;
        * an explicit feature frame;
        * an explicitly injected learned decision callable.

        Any learned exception falls back to fixed RSI.
        """

        if not self._allow_learned_inference:

            return self._fallback(
                fixed_rsi_fallback=
                    fixed_rsi_fallback,

                reason=
                    "learned_inference_disabled",
            )


        if feature_frame is None:

            return self._fallback(
                fixed_rsi_fallback=
                    fixed_rsi_fallback,

                reason=
                    "missing_feature_frame",

                learned_attempted=
                    False,
            )


        if learned_decider is None:

            return self._fallback(
                fixed_rsi_fallback=
                    fixed_rsi_fallback,

                reason=
                    "learned_decider_unavailable",

                learned_attempted=
                    False,
            )


        try:

            learned_signal = learned_decider(
                feature_frame
            )


            if not isinstance(
                learned_signal,
                Mapping,
            ):

                return self._fallback(
                    fixed_rsi_fallback=
                        fixed_rsi_fallback,

                    reason=
                        "learned_result_not_mapping",

                    learned_attempted=
                        True,
                )


            normalized_signal = dict(
                learned_signal
            )


            if not normalized_signal:

                return self._fallback(
                    fixed_rsi_fallback=
                        fixed_rsi_fallback,

                    reason=
                        "learned_result_empty",

                    learned_attempted=
                        True,
                )


            return StrategyDecisionFacadeResult(
                signal=
                    normalized_signal,

                source=
                    "learned",

                strategy_name=
                    CANONICAL_LEARNED_STRATEGY_NAME,

                candidate_id=
                    CANONICAL_CANDIDATE_ID,

                learned_attempted=
                    True,

                learned_used=
                    True,

                fallback_used=
                    False,

                fallback_reason=
                    None,
            )


        except Exception:

            return self._fallback(
                fixed_rsi_fallback=
                    fixed_rsi_fallback,

                reason=
                    "learned_inference_error",

                learned_attempted=
                    True,
            )


    @staticmethod
    def _fallback(
        *,
        fixed_rsi_fallback: FixedFallback,
        reason: str,
        learned_attempted: bool = False,
    ) -> StrategyDecisionFacadeResult:

        signal = fixed_rsi_fallback()


        if not isinstance(
            signal,
            Mapping,
        ):

            raise TypeError(
                "fixed_rsi_fallback must return a mapping."
            )


        normalized_signal = dict(
            signal
        )


        return StrategyDecisionFacadeResult(
            signal=
                normalized_signal,

            source=
                "fixed_rsi",

            strategy_name=
                "fixed_rsi",

            candidate_id=
                None,

            learned_attempted=
                learned_attempted,

            learned_used=
                False,

            fallback_used=
                True,

            fallback_reason=
                reason,
        )
