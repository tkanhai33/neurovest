from backend.app.stacks.snaptrade.contracts.readonly_models import (
    SnapTradeAccountSnapshot,
)

from backend.app.stacks.snaptrade.contracts.readonly_provider import (
    SnapTradeReadOnlyProvider,
)


class SnapTradeReadOnlyAdapter(
    SnapTradeReadOnlyProvider
):

    def __init__(
        self,
        enabled: bool = False,
    ):
        self.enabled = enabled


    async def get_account_snapshot(
        self,
    ) -> SnapTradeAccountSnapshot:

        if not self.enabled:
            raise RuntimeError(
                "SnapTrade adapter disabled"
            )

        raise RuntimeError(
            "SnapTrade network activation not authorized"
        )
