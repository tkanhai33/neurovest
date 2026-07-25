from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from snaptrade_client import (
    SnapTrade,
    SnapTradeAuth,
)

from backend.app.stacks.snaptrade.config.external_activation_gate import (
    snaptrade_external_access_allowed,
)

from backend.app.stacks.snaptrade.security.credential_boundary import (
    SnapTradeAuthMode,
    load_snaptrade_credentials,
)


@dataclass(
    frozen=True
)
class SnapTradeSdkDescriptor:
    auth_mode: SnapTradeAuthMode
    external_access_allowed: bool
    trading_exposed: bool = False


class SnapTradeReadOnlySdkClient:
    """
    Narrow SnapTrade SDK boundary.

    The raw SDK client remains private. This class intentionally
    does not expose the SDK trading namespace or any order method.

    Network requests remain blocked unless the independent external
    read-only activation gate is explicitly enabled.
    """

    def __init__(
        self,
        *,
        client: SnapTrade,
        auth_mode: SnapTradeAuthMode,
    ) -> None:
        self.__client = client
        self.__auth_mode = auth_mode

    @property
    def descriptor(
        self,
    ) -> SnapTradeSdkDescriptor:
        return SnapTradeSdkDescriptor(
            auth_mode=self.__auth_mode,
            external_access_allowed=(
                snaptrade_external_access_allowed()
            ),
            trading_exposed=False,
        )

    def _require_external_readonly_access(
        self,
    ) -> None:
        if not snaptrade_external_access_allowed():
            raise RuntimeError(
                "SnapTrade external read-only access "
                "is disabled."
            )

    def get_partner_info(
        self,
    ) -> Any:
        """
        Perform the credential/client-info health check.

        This is the first external call authorized in the next
        qualification step. It does not register users, open a
        brokerage portal, fetch holdings, or submit orders.
        """
        self._require_external_readonly_access()

        return (
            self.__client
            .reference_data
            .get_partner_info()
        )

    def check_api_status(
        self,
    ) -> Any:
        """
        Check SnapTrade API status after external read-only
        activation has been separately authorized.
        """
        self._require_external_readonly_access()

        return (
            self.__client
            .api_status
            .check()
        )


def build_snaptrade_sdk_client(
) -> SnapTradeReadOnlySdkClient:
    auth_mode, client_id, consumer_key = (
        load_snaptrade_credentials()
    )

    if auth_mode is SnapTradeAuthMode.PERSONAL:
        auth = (
            SnapTradeAuth.personal_api_key(
                client_id=client_id,
                consumer_key=consumer_key,
            )
        )
    else:
        auth = (
            SnapTradeAuth.commercial_api_key(
                client_id=client_id,
                consumer_key=consumer_key,
            )
        )

    raw_client = SnapTrade(
        auth=auth
    )

    return SnapTradeReadOnlySdkClient(
        client=raw_client,
        auth_mode=auth_mode,
    )
