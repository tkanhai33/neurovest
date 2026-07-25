from __future__ import annotations

from dataclasses import dataclass
import os

from backend.app.stacks.snaptrade.security.credential_boundary import (
    SnapTradeAuthMode,
    load_snaptrade_credential_state,
)


_TRUE_VALUES = {
    "1",
    "true",
    "yes",
    "on",
}


@dataclass(
    frozen=True
)
class SnapTradeProviderConfig:
    enabled: bool
    external_readonly_enabled: bool
    credentials_available: bool
    auth_mode: SnapTradeAuthMode

    @property
    def network_access_allowed(
        self,
    ) -> bool:
        return (
            self.enabled
            and self.external_readonly_enabled
            and self.credentials_available
        )


def _environment_flag(
    name: str,
    *,
    default: bool = False,
) -> bool:
    value = os.getenv(
        name
    )

    if value is None:
        return default

    return (
        value.strip().lower()
        in _TRUE_VALUES
    )


def load_snaptrade_provider_config(
) -> SnapTradeProviderConfig:
    credential_state = (
        load_snaptrade_credential_state()
    )

    return SnapTradeProviderConfig(
        enabled=_environment_flag(
            "SNAPTRADE_ENABLED",
            default=False,
        ),
        external_readonly_enabled=(
            _environment_flag(
                "SNAPTRADE_EXTERNAL_READONLY_ENABLED",
                default=False,
            )
        ),
        credentials_available=(
            credential_state.ready
        ),
        auth_mode=(
            credential_state.auth_mode
        ),
    )


DEFAULT_SNAPTRADE_CONFIG = (
    load_snaptrade_provider_config()
)
