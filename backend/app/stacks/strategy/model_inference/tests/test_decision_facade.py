from __future__ import annotations

import ast
from pathlib import Path


from backend.app.stacks.strategy.model_inference.decision_facade import (
    CANONICAL_CANDIDATE_ID,
    CANONICAL_LEARNED_STRATEGY_NAME,
    StrategyDecisionInferenceFacade,
)


def fixed_signal():
    return {
        "status":
            "ok",

        "symbol":
            "TEST",

        "action":
            "hold",

        "decision":
            "HOLD",

        "confidence":
            0.0,

        "rsi":
            50.0,
    }


def test_default_is_fixed_rsi_only():

    facade = StrategyDecisionInferenceFacade()

    result = facade.decide(
        fixed_rsi_fallback=
            fixed_signal,
    )

    assert (
        facade.learned_inference_enabled
        is False
    )

    assert result.source == "fixed_rsi"

    assert result.learned_attempted is False
    assert result.learned_used is False

    assert result.fallback_used is True

    assert (
        result.fallback_reason
        == "learned_inference_disabled"
    )

    assert result.signal == fixed_signal()


def test_default_does_not_call_learned_decider():

    calls = {
        "count":
            0,
    }


    def learned(_frame):

        calls[
            "count"
        ] += 1

        raise AssertionError(
            "learned decider must not run"
        )


    facade = StrategyDecisionInferenceFacade()

    result = facade.decide(
        fixed_rsi_fallback=
            fixed_signal,

        feature_frame=
            object(),

        learned_decider=
            learned,
    )


    assert calls[
        "count"
    ] == 0

    assert result.source == "fixed_rsi"


def test_enabled_but_missing_frame_falls_back():

    facade = StrategyDecisionInferenceFacade(
        allow_learned_inference=
            True,
    )

    result = facade.decide(
        fixed_rsi_fallback=
            fixed_signal,

        learned_decider=
            lambda _frame: {
                "action":
                    "buy",
            },
    )


    assert result.source == "fixed_rsi"

    assert (
        result.fallback_reason
        == "missing_feature_frame"
    )

    assert result.learned_used is False


def test_enabled_but_missing_decider_falls_back():

    facade = StrategyDecisionInferenceFacade(
        allow_learned_inference=
            True,
    )

    result = facade.decide(
        fixed_rsi_fallback=
            fixed_signal,

        feature_frame=
            object(),
    )


    assert result.source == "fixed_rsi"

    assert (
        result.fallback_reason
        == "learned_decider_unavailable"
    )


def test_learned_exception_falls_back():

    def broken(_frame):

        raise RuntimeError(
            "synthetic learned failure"
        )


    facade = StrategyDecisionInferenceFacade(
        allow_learned_inference=
            True,
    )

    result = facade.decide(
        fixed_rsi_fallback=
            fixed_signal,

        feature_frame=
            object(),

        learned_decider=
            broken,
    )


    assert result.source == "fixed_rsi"

    assert result.learned_attempted is True
    assert result.learned_used is False

    assert (
        result.fallback_reason
        == "learned_inference_error"
    )


def test_non_mapping_learned_result_falls_back():

    facade = StrategyDecisionInferenceFacade(
        allow_learned_inference=
            True,
    )

    result = facade.decide(
        fixed_rsi_fallback=
            fixed_signal,

        feature_frame=
            object(),

        learned_decider=
            lambda _frame: 123,
    )


    assert result.source == "fixed_rsi"

    assert (
        result.fallback_reason
        == "learned_result_not_mapping"
    )


def test_explicit_injected_learned_path_preserves_identity():

    facade = StrategyDecisionInferenceFacade(
        allow_learned_inference=
            True,
    )

    result = facade.decide(
        fixed_rsi_fallback=
            fixed_signal,

        feature_frame=
            object(),

        learned_decider=
            lambda _frame: {
                "status":
                    "ok",

                "symbol":
                    "TEST",

                "action":
                    "hold",

                "decision":
                    "HOLD",

                "confidence":
                    0.51,
            },
    )


    assert result.source == "learned"

    assert result.strategy_name == (
        CANONICAL_LEARNED_STRATEGY_NAME
    )

    assert result.candidate_id == (
        CANONICAL_CANDIDATE_ID
    )

    assert result.learned_attempted is True
    assert result.learned_used is True

    assert result.fallback_used is False
    assert result.fallback_reason is None


def test_readiness_has_no_runtime_capabilities():

    facade = StrategyDecisionInferenceFacade()

    readiness = facade.readiness()


    assert (
        readiness[
            "learned_inference_enabled"
        ]
        is False
    )

    assert readiness[
        "model_construction"
    ] is False

    assert readiness[
        "model_load"
    ] is False

    assert readiness[
        "model_prediction"
    ] is False

    assert readiness[
        "database_capability"
    ] is False

    assert readiness[
        "execution_capability"
    ] is False

    assert readiness[
        "broker_capability"
    ] is False

    assert readiness[
        "snaptrade_capability"
    ] is False

    assert readiness[
        "paper_capability"
    ] is False

    assert readiness[
        "live_capability"
    ] is False

    assert readiness[
        "training_capability"
    ] is False

    assert readiness[
        "controller_capability"
    ] is False


def test_facade_source_has_no_frozen25_runtime_import():

    facade_path = (
        Path(__file__)
        .resolve()
        .parents[1]
        / "decision_facade.py"
    )

    source = facade_path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source
    )


    imported_modules = []


    for node in ast.walk(
        tree
    ):

        if isinstance(
            node,
            ast.Import,
        ):

            imported_modules.extend(
                alias.name
                for alias
                in node.names
            )


        elif isinstance(
            node,
            ast.ImportFrom,
        ):

            imported_modules.append(
                node.module
                or ""
            )


    forbidden = (
        "frozen25_service",
        "boundary",
        "joblib",
        "sklearn",
        "pandas",
    )


    for module in imported_modules:

        assert not any(
            token
            in module
            for token
            in forbidden
        ), (
            module,
            imported_modules,
        )
