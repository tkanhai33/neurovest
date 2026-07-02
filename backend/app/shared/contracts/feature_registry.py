from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FeatureFlag:
    name: str
    enabled: bool = False
    reason: str = "disabled_by_default"


FEATURE_FLAGS: tuple[FeatureFlag, ...] = (
    FeatureFlag("live_trading"),
    FeatureFlag("canary_trading"),
    FeatureFlag("broker_orders"),
    FeatureFlag("broker_read_only_calls"),
    FeatureFlag("market_data_provider_calls"),
    FeatureFlag("strategy_scoring"),
    FeatureFlag("risk_approval_engine"),
    FeatureFlag("paper_trading_fill_engine"),
    FeatureFlag("runtime_scheduler"),
    FeatureFlag("ai_model_calls"),
    FeatureFlag("ai_tool_use"),
    FeatureFlag("ai_memory"),
    FeatureFlag("ai_rag"),
)
