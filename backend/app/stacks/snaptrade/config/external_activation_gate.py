from backend.app.stacks.snaptrade.security.credential_boundary import (
    load_snaptrade_credential_state,
)


def snaptrade_external_access_allowed() -> bool:

    state = load_snaptrade_credential_state()

    return (
        False
        and state.available
        and state.value_present
    )
