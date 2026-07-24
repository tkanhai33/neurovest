from dataclasses import dataclass
import os


@dataclass(frozen=True)
class SnapTradeCredentialState:
    available: bool
    value_present: bool


def load_snaptrade_credential_state() -> SnapTradeCredentialState:
    value = os.getenv(
        "SNAPTRADE_API_KEY"
    )

    if value is None:
        return SnapTradeCredentialState(
            available=False,
            value_present=False,
        )

    return SnapTradeCredentialState(
        available=True,
        value_present=True,
    )
