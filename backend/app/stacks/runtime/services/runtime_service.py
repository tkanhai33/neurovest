from __future__ import annotations

from app.stacks.runtime.contracts.runtime_contract import (
    RuntimeSkeletonStatus,
    RuntimeWorkflowContract,
    RuntimeWorkflowStatus,
)


def get_runtime_skeleton_status() -> RuntimeSkeletonStatus:
    return RuntimeSkeletonStatus()


def disable_runtime_workflow_in_skeleton(
    workflow: RuntimeWorkflowContract,
) -> RuntimeWorkflowContract:
    return RuntimeWorkflowContract(
        workflow_id=workflow.workflow_id,
        job_type=workflow.job_type,
        status=RuntimeWorkflowStatus.DISABLED,
    )
