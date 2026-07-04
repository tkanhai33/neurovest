from spine.L3_facade.stack_wiring_facade import get_stack_flow, healthcheck
def test_stack_flow_exists():
    flow = get_stack_flow()
    assert "auth_identity" in flow
    assert "chat_public" in flow
    assert flow.index("risk") < flow.index("execution")
def test_stack_wiring_healthcheck():
    h = healthcheck()
    assert h["status"] == "ok"
    assert h["stack_count"] >= 10
