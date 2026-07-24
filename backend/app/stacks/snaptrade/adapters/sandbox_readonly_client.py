from backend.app.stacks.snaptrade.contracts.readonly_models import (
    SnapTradeAccountSnapshot,
    SnapTradeBalanceSnapshot,
    SnapTradePositionSnapshot,
)


class SnapTradeSandboxReadOnlyClient:

    def __init__(
        self,
        api_key: str,
    ):
        self.api_key = api_key


    async def get_account_snapshot(
        self,
    ) -> SnapTradeAccountSnapshot:

        """
        Placeholder boundary.

        Real SDK binding occurs here only after
        read-only permission verification.

        No mutation endpoints permitted.
        """

        raise RuntimeError(
            "Sandbox client binding requires approved "
            "read-only credentials"
        )
