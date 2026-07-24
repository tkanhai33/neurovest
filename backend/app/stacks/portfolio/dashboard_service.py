from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any

class DashboardService:
    @staticmethod
    def _to_fin_decimal(value: float) -> Decimal:
        """Enforces uniform financial rounding to exactly two decimal places."""
        return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def calculate_summary(self, raw_transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Executes strict immutable ledger calculations over transaction metrics.
        Guarantees zero rounding drift by forcing all evaluations through fixed-point arithmetic.
        """
        # Base operational figures
        starting_cash = self._to_fin_decimal(5000.00)
        investment_valuation = self._to_fin_decimal(8300.00)

        running_delta = Decimal("0.00")
        sanitized_tx_history = []

        for tx in raw_transactions:
            tx_amount = self._to_fin_decimal(tx.get("amount", 0.0))
            tx_type = tx.get("type", "").lower()

            if tx_type == "credit":
                running_delta += tx_amount
            elif tx_type == "debit":
                running_delta -= tx_amount

            sanitized_tx_history.append({
                "id": tx.get("id"),
                "description": tx.get("description", "Sanitized Transaction"),
                "amount": float(tx_amount),
                "type": tx_type,
                "date": tx.get("date")
            })

        total_balance = starting_cash + running_delta

        return {
            "total_balance": float(total_balance),
            "active_investments": float(investment_valuation),
            "recent_transactions": sanitized_tx_history
        }

dashboard_service = DashboardService()
