from __future__ import annotations

import pytest

from backend.app.stacks.snaptrade.adapters.sdk_client_factory import (
    SnapTradeReadOnlySdkClient,
    build_snaptrade_sdk_client,
)

from backend.app.stacks.snaptrade.config.external_activation_gate import (
    snaptrade_external_access_allowed,
)

from backend.app.stacks.snaptrade.config.provider_config import (
    load_snaptrade_provider_config,
)

from backend.app.stacks.snaptrade.security.credential_boundary import (
    SnapTradeAuthMode,
    load_snaptrade_credential_state,
)


def test_credentials_absent_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for name in (
        "SNAPTRADE_CLIENT_ID",
        "SNAPTRADE_CONSUMER_KEY",
        "SNAPTRADE_AUTH_MODE",
        "SNAPTRADE_ENABLED",
        "SNAPTRADE_EXTERNAL_READONLY_ENABLED",
    ):
        monkeypatch.delenv(
            name,
            raising=False,
        )

    state = load_snaptrade_credential_state()

    assert state.auth_mode is (
        SnapTradeAuthMode.PERSONAL
    )

    assert state.ready is False


def test_external_access_is_disabled_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "SNAPTRADE_CLIENT_ID",
        "test-client-id",
    )

    monkeypatch.setenv(
        "SNAPTRADE_CONSUMER_KEY",
        "test-consumer-key",
    )

    monkeypatch.delenv(
        "SNAPTRADE_ENABLED",
        raising=False,
    )

    monkeypatch.delenv(
        "SNAPTRADE_EXTERNAL_READONLY_ENABLED",
        raising=False,
    )

    config = (
        load_snaptrade_provider_config()
    )

    assert config.credentials_available is True
    assert config.enabled is False
    assert (
        config.external_readonly_enabled
        is False
    )
    assert config.network_access_allowed is False
    assert (
        snaptrade_external_access_allowed()
        is False
    )


@pytest.mark.parametrize(
    (
        "auth_mode",
        "expected",
    ),
    (
        (
            "personal",
            SnapTradeAuthMode.PERSONAL,
        ),
        (
            "commercial",
            SnapTradeAuthMode.COMMERCIAL,
        ),
    ),
)
def test_builds_supported_auth_modes_without_network_call(
    monkeypatch: pytest.MonkeyPatch,
    auth_mode: str,
    expected: SnapTradeAuthMode,
) -> None:
    monkeypatch.setenv(
        "SNAPTRADE_CLIENT_ID",
        "test-client-id",
    )

    monkeypatch.setenv(
        "SNAPTRADE_CONSUMER_KEY",
        "test-consumer-key",
    )

    monkeypatch.setenv(
        "SNAPTRADE_AUTH_MODE",
        auth_mode,
    )

    monkeypatch.delenv(
        "SNAPTRADE_ENABLED",
        raising=False,
    )

    monkeypatch.delenv(
        "SNAPTRADE_EXTERNAL_READONLY_ENABLED",
        raising=False,
    )

    client = build_snaptrade_sdk_client()

    assert isinstance(
        client,
        SnapTradeReadOnlySdkClient,
    )

    descriptor = client.descriptor

    assert descriptor.auth_mode is expected
    assert (
        descriptor.external_access_allowed
        is False
    )
    assert descriptor.trading_exposed is False


def test_network_health_check_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "SNAPTRADE_CLIENT_ID",
        "test-client-id",
    )

    monkeypatch.setenv(
        "SNAPTRADE_CONSUMER_KEY",
        "test-consumer-key",
    )

    monkeypatch.setenv(
        "SNAPTRADE_AUTH_MODE",
        "personal",
    )

    monkeypatch.delenv(
        "SNAPTRADE_ENABLED",
        raising=False,
    )

    monkeypatch.delenv(
        "SNAPTRADE_EXTERNAL_READONLY_ENABLED",
        raising=False,
    )

    client = build_snaptrade_sdk_client()

    with pytest.raises(
        RuntimeError,
        match=(
            "external read-only access "
            "is disabled"
        ),
    ):
        client.check_api_status()


def test_wrapper_exposes_no_trading_methods(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "SNAPTRADE_CLIENT_ID",
        "test-client-id",
    )

    monkeypatch.setenv(
        "SNAPTRADE_CONSUMER_KEY",
        "test-consumer-key",
    )

    client = build_snaptrade_sdk_client()

    forbidden = {
        "trading",
        "place_order",
        "submit_order",
        "execute_order",
        "cancel_order",
        "replace_order",
        "preview_order",
    }

    exposed = set(
        dir(
            client
        )
    )

    assert forbidden.isdisjoint(
        exposed
    )
