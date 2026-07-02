from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class BrokerProvider(StrEnum):
    SNAPTRADE = "snaptrade"


class BrokerConnectionStatus(StrEnum):
    NOT_CONFIGURED = "not_configured"
    LOCKED = "locked"
    READ_ONLY_READY = "read_only_ready"


@dataclass(frozen=True)
class BrokerAccountContract:
    broker_account_id: str
    provider: BrokerProvider
    status: BrokerConnectionStatus = BrokerConnectionStatus.LOCKED


@dataclass(frozen=True)
class BrokerPositionContract:
    symbol: str
    quantity: float | None = None
    currency: str | None = None


@dataclass(frozen=True)
class BrokerOrderPreviewContract:
    symbol: str
    side: str
    quantity: float | None = None
    preview_only: bool = True


@dataclass(frozen=True)
class BrokerIntegrationSkeletonStatus:
    stack: str = "broker_integration"
    phase: str = "phase_10_skeleton"
    provider: BrokerProvider = BrokerProvider.SNAPTRADE
    broker_auth_implemented: bool = False
    token_storage_implemented: bool = False
    account_sync_implemented: bool = False
    read_only_calls_enabled: bool = False
    order_preview_implemented: bool = False
    order_submission_implemented: bool = False
    live_trading_implemented: bool = False
    business_logic_implemented: bool = False
