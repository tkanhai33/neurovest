from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import os


class SnapTradeAuthMode(
    str,
    Enum,
):
    PERSONAL = "personal"
    COMMERCIAL = "commercial"


@dataclass(
    frozen=True
)
class SnapTradeCredentialState:
    auth_mode: SnapTradeAuthMode
    client_id_available: bool
    consumer_key_available: bool
    client_id_value_present: bool
    consumer_key_value_present: bool

    @property
    def available(
        self,
    ) -> bool:
        return (
            self.client_id_available
            and self.consumer_key_available
        )

    @property
    def value_present(
        self,
    ) -> bool:
        return (
            self.client_id_value_present
            and self.consumer_key_value_present
        )

    @property
    def ready(
        self,
    ) -> bool:
        return (
            self.available
            and self.value_present
        )


def _load_auth_mode() -> SnapTradeAuthMode:
    raw = (
        os.getenv(
            "SNAPTRADE_AUTH_MODE",
            SnapTradeAuthMode.PERSONAL.value,
        )
        .strip()
        .lower()
    )

    try:
        return SnapTradeAuthMode(
            raw
        )
    except ValueError as error:
        raise RuntimeError(
            "SNAPTRADE_AUTH_MODE must be "
            "'personal' or 'commercial'."
        ) from error


def load_snaptrade_credential_state(
    *,
    environ: dict[str, str] | None = None,
) -> SnapTradeCredentialState:
    source = (
        os.environ
        if environ is None
        else environ
    )

    auth_mode_raw = (
        source.get(
            "SNAPTRADE_AUTH_MODE",
            SnapTradeAuthMode.PERSONAL.value,
        )
        .strip()
        .lower()
    )

    try:
        auth_mode = SnapTradeAuthMode(
            auth_mode_raw
        )
    except ValueError as error:
        raise RuntimeError(
            "SNAPTRADE_AUTH_MODE must be "
            "'personal' or 'commercial'."
        ) from error

    client_id = source.get(
        "SNAPTRADE_CLIENT_ID"
    )

    consumer_key = source.get(
        "SNAPTRADE_CONSUMER_KEY"
    )

    return SnapTradeCredentialState(
        auth_mode=auth_mode,
        client_id_available=(
            client_id is not None
        ),
        consumer_key_available=(
            consumer_key is not None
        ),
        client_id_value_present=bool(
            client_id
            and client_id.strip()
        ),
        consumer_key_value_present=bool(
            consumer_key
            and consumer_key.strip()
        ),
    )


def load_snaptrade_credentials(
    *,
    environ: dict[str, str] | None = None,
) -> tuple[
    SnapTradeAuthMode,
    str,
    str,
]:
    source = (
        os.environ
        if environ is None
        else environ
    )

    state = load_snaptrade_credential_state(
        environ=source
    )

    if not state.ready:
        raise RuntimeError(
            "SnapTrade credentials are not configured. "
            "SNAPTRADE_CLIENT_ID and "
            "SNAPTRADE_CONSUMER_KEY are required."
        )

    client_id = source[
        "SNAPTRADE_CLIENT_ID"
    ].strip()

    consumer_key = source[
        "SNAPTRADE_CONSUMER_KEY"
    ].strip()

    return (
        state.auth_mode,
        client_id,
        consumer_key,
    )
