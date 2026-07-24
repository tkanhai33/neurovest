from typing import Protocol

from .readonly_models import (
    SnapTradeAccountSnapshot,
)


class SnapTradeReadOnlyProvider(Protocol):

    async def get_account_snapshot(
        self,
    ) -> SnapTradeAccountSnapshot:
        ...
