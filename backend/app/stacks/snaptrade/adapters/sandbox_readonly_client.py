from __future__ import annotations

from backend.app.stacks.snaptrade.adapters.sdk_client_factory import (
    SnapTradeReadOnlySdkClient,
    build_snaptrade_sdk_client,
)


class SnapTradeSandboxReadOnlyClient:
    """
    Disabled-by-default SDK integration boundary.

    This wrapper intentionally exposes no order, preview, cancel,
    replace, trade, or mutation operation.
    """

    def __init__(
        self,
    ) -> None:
        self._client: (
            SnapTradeReadOnlySdkClient
            | None
        ) = None

    def build_client(
        self,
    ) -> SnapTradeReadOnlySdkClient:
        if self._client is None:
            self._client = (
                build_snaptrade_sdk_client()
            )

        return self._client

    def client_info_health_check(
        self,
    ):
        return (
            self.build_client()
            .get_partner_info()
        )

    def api_status_health_check(
        self,
    ):
        return (
            self.build_client()
            .check_api_status()
        )
