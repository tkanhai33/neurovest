"""DOMAIN_LOGIC_V1 portfolio allocation."""


def allocate_cash(signal: dict, cash: float = 1000.0) -> dict:
    side = signal.get("side", "HOLD")
    if side == "BUY":
        allocation = cash * 0.25
    elif side == "SELL":
        allocation = 0.0
    else:
        allocation = cash * 0.05
    return {"side": side, "cash_allocated": allocation}
