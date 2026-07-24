from backend.app.stacks.snaptrade.config.provider_config import (
    DEFAULT_SNAPTRADE_CONFIG,
)

from backend.app.stacks.snaptrade.providers.disabled_provider import (
    SnapTradeDisabledProvider,
)

from backend.app.stacks.snaptrade.adapters.readonly_adapter import (
    SnapTradeReadOnlyAdapter,
)


def build_snaptrade_provider():

    if (
        DEFAULT_SNAPTRADE_CONFIG.enabled
        and DEFAULT_SNAPTRADE_CONFIG.credentials_available
    ):
        return SnapTradeReadOnlyAdapter(
            enabled=True
        )

    return SnapTradeDisabledProvider()
