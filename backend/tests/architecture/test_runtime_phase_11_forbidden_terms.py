from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STACK = ROOT / "app" / "stacks" / "runtime"

FORBIDDEN_TERMS = [
    "while True",
    "asyncio.create_task",
    "BackgroundTasks",
    "APScheduler",
    "schedule.every",
    "run_scheduler",
    "execute_workflow",
    "execute_trade",
    "submit_order",
    "place_order",
    "broker_client",
    "mutate_strategy",
]


def test_runtime_phase_11_has_no_scheduler_or_execution_logic() -> None:
    scanned = []

    for path in STACK.rglob("*.py"):
        text = path.read_text(errors="ignore")
        scanned.append(path)

        for term in FORBIDDEN_TERMS:
            assert term not in text, f"Forbidden runtime implementation term {term!r} found in {path}"

    assert scanned
