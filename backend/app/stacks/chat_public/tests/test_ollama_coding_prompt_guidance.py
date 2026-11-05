import json

from backend.app.stacks.chat_public import ollama_chat_client


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return json.dumps(
            {"message": {"content": "qualified reply"}}
        ).encode("utf-8")


def capture_system_message(monkeypatch, question):
    captured = {}

    def fake_urlopen(request, timeout):
        captured["request"] = request
        return FakeResponse()

    monkeypatch.setattr(
        ollama_chat_client.urllib.request,
        "urlopen",
        fake_urlopen,
    )

    result = ollama_chat_client.ask_ollama(
        question,
        model="neuro-reason:latest",
    )
    payload = json.loads(captured["request"].data.decode("utf-8"))

    assert result == "qualified reply"
    assert payload["model"] == "neuro-reason:latest"
    return payload["messages"][0]["content"]


def test_asyncio_gil_guidance_reaches_reason_system_prompt(monkeypatch):
    system_message = capture_system_message(
        monkeypatch,
        "Explain whether asyncio bypasses the GIL in CPython. "
        "Include a Python asyncio example.",
    )

    assert "Do not claim asyncio avoids or bypasses the GIL" in system_message
    assert "event-loop thread" in system_message
    assert "CPU-bound Python bytecode run in parallel" in system_message


def test_numeric_total_and_mock_safety_guidance_reaches_system_prompt(
    monkeypatch,
):
    system_message = capture_system_message(
        monkeypatch,
        "Write a Python example with exactly 10 workers and 100 increments "
        "per worker. Demonstrate mocked async fetches without live network calls.",
    )

    assert "Honor requested numeric totals exactly" in system_message
    assert "actually mocked or injected" in system_message
    assert "Do not include public service URLs" in system_message

def test_requested_example_and_pitfall_guidance_reaches_system_prompt(
    monkeypatch,
):
    system_message = capture_system_message(
        monkeypatch,
        "Write a Python example with exactly 10 workers and 100 increments "
        "per worker. Include one concrete example and one likely pitfall. "
        "Demonstrate mocked async fetches without live network calls.",
    )

    assert "When explicitly asked for a concrete example or" in system_message
    assert "include one relevant example" in system_message
    assert "label conceptual steps as pseudocode" in system_message
    assert "state one specific pitfall and why it matters" in system_message

def test_domain_accuracy_guidance_reaches_system_prompt(monkeypatch):
    system_message = capture_system_message(
        monkeypatch,
        "Write a Python example about FastAPI validation, PostgreSQL "
        "transactions, asyncio cancellation, systemd restart limits, "
        "Redis caching, HTTP idempotency, and typing.cast.",
    )

    for phrase in (
        "distinguish the default",
        "RequestValidationError",
        "leaves it aborted",
        "generally re-raise",
        "StartLimitBurst",
        "do not make Redis and a separate database atomic",
        "does not make a request idempotent",
        "typing.cast does not validate",
    ):
        assert phrase in system_message

def test_r214_technical_example_contract_reaches_system_prompt(monkeypatch):
    system_message = capture_system_message(
        monkeypatch,
        "Explain FastAPI validation and systemd restart limits with examples.",
    )

    for phrase in (
        "include imports for every",
        "JSONResponse when referenced",
        "do not make",
        "permitted number of starts",
        "under [Unit]",
        "under [Service]",
    ):
        assert phrase in system_message

