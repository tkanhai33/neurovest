from backend.app.stacks.snaptrade.contracts.readonly_models import (
    SnapTradeAccountSnapshot,
    SnapTradeBalanceSnapshot,
    SnapTradePositionSnapshot,
)


class MockSnapTradeProvider:

    async def get_account_snapshot(
        self,
    ) -> SnapTradeAccountSnapshot:

        return SnapTradeAccountSnapshot(
            account_id="mock",
            balances=(
                SnapTradeBalanceSnapshot(
                    currency="USD",
                    total_value=1000.0,
                ),
            ),
            positions=(),
        )
