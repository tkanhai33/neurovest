from app.main import health


def test_health_contract_locks_live_trading() -> None:
    result = health()
    assert result["status"] == "ok"
    assert result["live_trading"] == "locked"
    assert result["broker_orders"] == "locked"
