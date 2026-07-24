from dataclasses import dataclass


@dataclass(frozen=True)
class SnapTradeProviderConfig:
    enabled: bool = False
    credentials_available: bool = False


DEFAULT_SNAPTRADE_CONFIG = (
    SnapTradeProviderConfig()
)
