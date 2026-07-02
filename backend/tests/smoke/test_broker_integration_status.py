from app.stacks.broker_integration.adapters.snaptrade_adapter import (
    snaptrade_adapter_placeholder,
)
from app.stacks.broker_integration.contracts.broker_integration_contract import (
    BrokerOrderPreviewContract,
)
from app.stacks.broker_integration.services.broker_integration_service import (
    get_broker_integration_skeleton_status,
    reject_all_broker_order_previews_in_skeleton,
)


def test_broker_integration_status_is_skeleton_only() -> None:
    status = get_broker_integration_skeleton_status()

    assert status.stack == "broker_integration"
    assert status.phase == "phase_10_skeleton"
    assert status.broker_auth_implemented is False
    assert status.token_storage_implemented is False
    assert status.account_sync_implemented is False
    assert status.read_only_calls_enabled is False
    assert status.order_preview_implemented is False
    assert status.order_submission_implemented is False
    assert status.live_trading_implemented is False
    assert status.business_logic_implemented is False


def test_snaptrade_placeholder_does_not_call_broker() -> None:
    assert snaptrade_adapter_placeholder() == "phase_10_skeleton_only_no_broker_calls"


def test_broker_preview_remains_preview_only() -> None:
    preview = BrokerOrderPreviewContract(symbol="RY.TO", side="buy")
    rejected = reject_all_broker_order_previews_in_skeleton(preview)

    assert rejected.preview_only is True
