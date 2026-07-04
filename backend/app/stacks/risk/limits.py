"""DOMAIN_LOGIC_V1 risk limit checks."""

DEFAULT_LIMITS = {"max_order_value": 1000.0, "max_gross_exposure": 5000.0}


def check_risk_limits(order: dict, exposure: dict | None = None, limits: dict | None = None) -> dict:
    limits = limits or DEFAULT_LIMITS
    exposure = exposure or {"gross_exposure": 0.0}
    order_value = abs(float(order.get("quantity", 0)) * float(order.get("price", 0)))
    projected = float(exposure.get("gross_exposure", 0.0)) + order_value

    if order_value > limits["max_order_value"]:
        return {"approved": False, "reason": "max_order_value_exceeded"}

    if projected > limits["max_gross_exposure"]:
        return {"approved": False, "reason": "max_gross_exposure_exceeded"}

    return {"approved": True, "reason": "risk_ok"}
