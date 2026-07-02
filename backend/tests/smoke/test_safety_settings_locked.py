from app.shared.config.settings import get_settings


def test_safety_settings_locked_by_default() -> None:
    settings = get_settings()

    assert settings.broker_enabled is False
    assert settings.live_trading_enabled is False
    assert settings.canary_trading_enabled is False
