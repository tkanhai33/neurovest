from types import SimpleNamespace

import pytest

from backend.app.stacks.chat_public.conversation_store import (
    ConversationStore,
)


@pytest.mark.asyncio
async def test_existing_thread_rejects_different_owner(
    monkeypatch,
) -> None:
    store = ConversationStore()
    existing = SimpleNamespace(user_id="owner-a")

    async def get_thread(thread_id: str):
        assert thread_id == "thread-a"
        return existing

    async def create_thread(**kwargs):
        raise AssertionError(
            "Cross-user access must not create a replacement thread."
        )

    monkeypatch.setattr(store, "get_thread", get_thread)
    monkeypatch.setattr(store, "create_thread", create_thread)

    with pytest.raises(
        PermissionError,
        match="Chat thread is not available",
    ):
        await store.get_or_create_thread(
            thread_id="thread-a",
            user_id="owner-b",
        )


@pytest.mark.asyncio
async def test_existing_thread_allows_exact_owner(
    monkeypatch,
) -> None:
    store = ConversationStore()
    existing = SimpleNamespace(user_id="owner-a")

    async def get_thread(thread_id: str):
        return existing

    monkeypatch.setattr(store, "get_thread", get_thread)

    result = await store.get_or_create_thread(
        thread_id="thread-a",
        user_id="owner-a",
    )

    assert result is existing


@pytest.mark.asyncio
async def test_existing_thread_rejects_missing_owner(
    monkeypatch,
) -> None:
    store = ConversationStore()
    existing = SimpleNamespace(user_id="owner-a")

    async def get_thread(thread_id: str):
        return existing

    monkeypatch.setattr(store, "get_thread", get_thread)

    with pytest.raises(PermissionError):
        await store.get_or_create_thread(
            thread_id="thread-a",
            user_id=None,
        )
