
import asyncio
from types import SimpleNamespace

import pytest

from backend.app.stacks.db_runtime import (
    training_findings_delivery as delivery,
)
from backend.app.stacks.chat_public import chat_runtime


def sample(**overrides):
    record = {
        "run_id": "training_test_abc123",
        "scope": "user",
        "status": "completed",
        "owner_user_id": "owner-a",
        "notification_thread_id": "thread-a",
        "notification_parent_message_id": "message-a",
        "selected_symbols": ["BTE.TO", "TD.TO", "WCP.TO"],
        "rows_evaluated": 34461,
        "eligible_symbol_count": 3,
    }
    record.update(overrides)
    return record


class FakeStore:
    def __init__(self, owner="owner-a"):
        self.owner = owner
        self.messages = []

    async def require_thread(self, thread_id):
        return SimpleNamespace(user_id=self.owner)

    async def get_message_by_client_id(
        self, *, thread_id, client_message_id
    ):
        for message in self.messages:
            if message["client_message_id"] == client_message_id:
                return message
        return None

    async def append_message(self, **kwargs):
        self.messages.append(kwargs)
        return SimpleNamespace(**kwargs)


def test_real_metrics_are_reported():
    report = delivery.format_training_findings(sample())
    assert "34,461" not in report or "34461" in report
    assert "BTE.TO, TD.TO, WCP.TO" in report
    assert "future returns" in report


def test_failure_is_not_reported_as_success():
    report = delivery.format_training_findings(
        sample(status="failed", error="Insufficient historical data")
    )
    assert "FAILED" in report
    assert "Insufficient historical data" in report


def test_delivery_is_idempotent(monkeypatch):
    store = FakeStore()
    monkeypatch.setattr(chat_runtime, "conversation_store", store)

    first = asyncio.run(
        delivery.deliver_training_findings(sample())
    )
    second = asyncio.run(
        delivery.deliver_training_findings(sample())
    )

    assert first is True
    assert second is False
    assert len(store.messages) == 1
    assert store.messages[0]["role"] == "assistant"
    assert store.messages[0]["parent_message_id"] == "message-a"


def test_wrong_owner_denied(monkeypatch):
    store = FakeStore(owner="owner-b")
    monkeypatch.setattr(chat_runtime, "conversation_store", store)

    with pytest.raises(PermissionError):
        asyncio.run(
            delivery.deliver_training_findings(sample())
        )

    assert not store.messages


def test_system_training_never_notified(monkeypatch):
    store = FakeStore()
    monkeypatch.setattr(chat_runtime, "conversation_store", store)

    result = asyncio.run(
        delivery.deliver_training_findings(
            sample(scope="system")
        )
    )
    assert result is False
    assert not store.messages
