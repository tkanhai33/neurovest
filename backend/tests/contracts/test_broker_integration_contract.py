from app.stacks.broker_integration.contracts.broker_integration_contract import (
    BrokerAccountContract,
    BrokerConnectionStatus,
    BrokerIntegrationSkeletonStatus,
    BrokerOrderPreviewContract,
    BrokerPositionContract,
    BrokerProvider,
)


def test_broker_account_contract_shape() -> None:
    account = BrokerAccountContract(
        broker_account_id="broker_001",
        provider=BrokerProvider.SNAPTRADE,
    )

    assert account.broker_account_id == "broker_001"
    assert account.provider == BrokerProvider.SNAPTRADE
    assert account.status == BrokerConnectionStatus.LOCKED


def test_broker_position_contract_shape() -> None:
    position = BrokerPositionContract(symbol="RY.TO", currency="CAD")

    assert position.symbol == "RY.TO"
    assert position.quantity is None
    assert position.currency == "CAD"


def test_broker_order_preview_contract_shape() -> None:
    preview = BrokerOrderPreviewContract(
        symbol="RY.TO",
        side="buy",
        quantity=None,
    )

    assert preview.symbol == "RY.TO"
    assert preview.side == "buy"
    assert preview.quantity is None
    assert preview.preview_only is True


def test_broker_integration_skeleton_status_locked() -> None:
    status = BrokerIntegrationSkeletonStatus()

    assert status.stack == "broker_integration"
    assert status.phase == "phase_10_skeleton"
    assert status.provider == BrokerProvider.SNAPTRADE
    assert status.broker_auth_implemented is False
    assert status.token_storage_implemented is False
    assert status.account_sync_implemented is False
    assert status.read_only_calls_enabled is False
    assert status.order_preview_implemented is False
    assert status.order_submission_implemented is False
    assert status.live_trading_implemented is False
    assert status.business_logic_implemented is False
