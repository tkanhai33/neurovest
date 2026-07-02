from __future__ import annotations

from app.stacks.broker_integration.contracts.broker_integration_contract import (
    BrokerIntegrationSkeletonStatus,
    BrokerOrderPreviewContract,
)


def get_broker_integration_skeleton_status() -> BrokerIntegrationSkeletonStatus:
    return BrokerIntegrationSkeletonStatus()


def reject_all_broker_order_previews_in_skeleton(
    preview: BrokerOrderPreviewContract,
) -> BrokerOrderPreviewContract:
    return BrokerOrderPreviewContract(
        symbol=preview.symbol,
        side=preview.side,
        quantity=preview.quantity,
        preview_only=True,
    )
