from app.stacks.runtime.contracts.runtime_contract import (
    RuntimeJobType,
    RuntimeWorkflowContract,
    RuntimeWorkflowStatus,
)
from app.stacks.runtime.services.runtime_service import (
    disable_runtime_workflow_in_skeleton,
    get_runtime_skeleton_status,
)


def test_runtime_status_is_skeleton_only() -> None:
    status = get_runtime_skeleton_status()

    assert status.stack == "runtime"
    assert status.phase == "phase_11_skeleton"
    assert status.scheduler_implemented is False
    assert status.background_loops_enabled is False
    assert status.workflow_execution_implemented is False
    assert status.strategy_execution_implemented is False
    assert status.paper_trading_integration_implemented is False
    assert status.broker_integration_implemented is False
    assert status.mutation_logic_implemented is False
    assert status.business_logic_implemented is False


def test_runtime_skeleton_disables_workflows() -> None:
    workflow = RuntimeWorkflowContract(
        workflow_id="workflow_001",
        job_type=RuntimeJobType.MANUAL_RESEARCH_REFRESH,
        status=RuntimeWorkflowStatus.SKELETON_ONLY,
    )

    disabled = disable_runtime_workflow_in_skeleton(workflow)

    assert disabled.workflow_id == "workflow_001"
    assert disabled.status == RuntimeWorkflowStatus.DISABLED
