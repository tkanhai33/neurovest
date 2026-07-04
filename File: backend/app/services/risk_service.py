from pydantic import BaseModel

class RiskService:
    async def check_risk_limits(self, order: dict) -> dict:
        limits = {"max_order_value": 1000.0, "max_gross_exposure": 5000.0}
        order_value = abs(float(order.get("quantity", 0)) * float(order.get("price", 0)))
        projected = float(limits["max_gross_exposure"]) + order_value

        if order_value > limits["max_order_value"]:
            return {"approved": False, "reason": "max_order_value_exceeded"}

        if projected > limits["max_gross_exposure"]:
            return {"approved": False, "reason": "max_gross_exposure_exceeded"}

        return {"approved": True, "reason": "risk_ok"}
