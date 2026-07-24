from dataclasses import dataclass


@dataclass(frozen=True)
class SnapTradePositionSnapshot:
    symbol: str
    quantity: float
    average_price: float
    market_value: float


@dataclass(frozen=True)
class SnapTradeBalanceSnapshot:
    currency: str
    total_value: float


@dataclass(frozen=True)
class SnapTradeAccountSnapshot:
    account_id: str
    balances: tuple[SnapTradeBalanceSnapshot, ...]
    positions: tuple[SnapTradePositionSnapshot, ...]
