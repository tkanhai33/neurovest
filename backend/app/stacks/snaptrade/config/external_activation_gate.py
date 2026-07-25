from __future__ import annotations

from backend.app.stacks.snaptrade.config.provider_config import (
    load_snaptrade_provider_config,
)


def snaptrade_external_access_allowed(
) -> bool:
    config = (
        load_snaptrade_provider_config()
    )

    return config.network_access_allowed
