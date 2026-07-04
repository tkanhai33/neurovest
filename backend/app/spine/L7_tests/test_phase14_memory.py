from spine.L4_runtime.memory.state_event_store import append_event
from spine.L4_runtime.memory.state_replay_engine import replay_state
def test_event_store():
    append_event({"stack": "risk", "value": "test"})
    r = replay_state()
    assert "final_state" in r
