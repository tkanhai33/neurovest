from backend.app.stacks.snaptrade.contracts.readonly_provider import (
    SnapTradeReadOnlyProvider,
)


class SnapTradeReadOnlyFacade:

    def __init__(
        self,
        provider: SnapTradeReadOnlyProvider,
    ):
        self.provider = provider


    async def account_snapshot(self):
        return await self.provider.get_account_snapshot()
