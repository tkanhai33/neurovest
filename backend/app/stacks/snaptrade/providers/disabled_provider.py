from backend.app.stacks.snaptrade.contracts.readonly_models import (
    SnapTradeAccountSnapshot,
)


class SnapTradeDisabledProvider:

    async def get_account_snapshot(
        self,
    ) -> SnapTradeAccountSnapshot:
        raise RuntimeError(
            "SnapTrade disabled: credentials not configured"
        )
