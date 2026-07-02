from app.stacks.runtime.contracts.runtime_contract import (
    RuntimeEventContract,
    RuntimeJobType,
    RuntimeScheduleContract,
    RuntimeSkeletonStatus,
    RuntimeWorkflowContract,
    RuntimeWorkflowStatus,
)


def test_runtime_workflow_contract_shape() -> None:
    workflow = RuntimeWorkflowContract(
        workflow_id="workflow_001",
        job_type=RuntimeJobType.MANUAL_RESEARCH_REFRESH,
    )

    assert workflow.workflow_id == "workflow_001"
    assert workflow.job_type == RuntimeJobType.MANUAL_RESEARCH_REFRESH
    assert workflow.status == RuntimeWorkflowStatus.DISABLED


def test_runtime_schedule_contract_shape() -> None:
    schedule = RuntimeScheduleContract(
        schedule_id="schedule_001",
        workflow_id="workflow_001",
    )

    assert schedule.schedule_id == "schedule_001"
    assert schedule.workflow_id == "workflow_001"
    assert schedule.enabled is False


def test_runtime_event_contract_shape() -> None:
    event = RuntimeEventContract(
        event_id="event_001",
        workflow_id="workflow_001",
        event_name="placeholder_event",
    )

    assert event.event_id == "event_001"
    assert event.workflow_id == "workflow_001"
    assert event.event_name == "placeholder_event"


def test_runtime_skeleton_status_locked() -> None:
    status = RuntimeSkeletonStatus()

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
