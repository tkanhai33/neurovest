"""
134B3_CONVERSATION_STORE_IMPLEMENTATION

Persistent asynchronous conversation store for NeuroVest chat.

Owns persistence operations for:
- chat threads
- chat messages
- conversation state
- memory facts
- tool evidence

This phase does not yet:
- wire persistence into the live chat API
- inject history into Ollama
- summarize conversations
- enable streaming
- execute financial tools
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Sequence

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from backend.app.stacks.chat_public.contracts import (
    ChatMessage,
    ChatThread,
    ConversationState,
    MemoryFact,
    ToolEvidence,
)
from backend.app.stacks.chat_public.persistence import (
    ChatMessageRecord,
    ChatThreadRecord,
    ConversationStateRecord,
    MemoryFactRecord,
    ToolEvidenceRecord,
)
from backend.app.stacks.db_runtime import async_session


def utc_now() -> datetime:
    return datetime.now(UTC)


def _thread_contract(
    record: ChatThreadRecord,
) -> ChatThread:
    return ChatThread(
        thread_id=record.thread_id,
        user_id=record.user_id,
        title=record.title,
        status=record.status,
        summary=record.summary,
        message_count=record.message_count,
        created_at=record.created_at,
        updated_at=record.updated_at,
        metadata=dict(record.metadata_json or {}),
    )


def _message_contract(
    record: ChatMessageRecord,
) -> ChatMessage:
    metadata = dict(record.metadata_json or {})

    if record.client_message_id:
        metadata.setdefault(
            "client_message_id",
            record.client_message_id,
        )

    return ChatMessage(
        message_id=record.message_id,
        thread_id=record.thread_id,
        parent_message_id=record.parent_message_id,
        role=record.role,
        content=record.content,
        intent=record.intent,
        symbol=record.symbol,
        provider=record.provider,
        model=record.model,
        tool_evidence_ids=list(
            record.tool_evidence_ids or []
        ),
        created_at=record.created_at,
        metadata=metadata,
    )


def _state_contract(
    record: ConversationStateRecord,
) -> ConversationState:
    return ConversationState(
        thread_id=record.thread_id,
        summary=record.summary or "",
        active_entities=dict(
            record.active_entities or {}
        ),
        active_strategy=(
            dict(record.active_strategy)
            if record.active_strategy
            else None
        ),
        portfolio_context=dict(
            record.portfolio_context or {}
        ),
        pending_tasks=list(
            record.pending_tasks or []
        ),
        remembered_terms=dict(
            record.remembered_terms or {}
        ),
        last_message_id=record.last_message_id,
        updated_at=record.updated_at,
        metadata=dict(record.metadata_json or {}),
    )


def _memory_contract(
    record: MemoryFactRecord,
) -> MemoryFact:
    return MemoryFact(
        memory_id=record.memory_id,
        thread_id=record.thread_id,
        key=record.key,
        value=record.value_json,
        confidence=record.confidence,
        status=record.status,
        source_message_id=record.source_message_id,
        created_at=record.created_at,
        updated_at=record.updated_at,
        metadata=dict(record.metadata_json or {}),
    )


def _evidence_contract(
    record: ToolEvidenceRecord,
) -> ToolEvidence:
    return ToolEvidence(
        evidence_id=record.evidence_id,
        thread_id=record.thread_id,
        tool_name=record.tool_name,
        tool_call_id=record.tool_call_id,
        claim_types=list(record.claim_types or []),
        request=dict(record.request_json or {}),
        result=dict(record.result_json or {}),
        status=record.status,
        observed_at=record.observed_at,
        expires_at=record.expires_at,
        metadata=dict(record.metadata_json or {}),
    )


class ConversationStore:
    async def create_thread(
        self,
        *,
        thread_id: str | None = None,
        user_id: str | None = None,
        title: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ChatThread:
        contract = ChatThread(
            **(
                {"thread_id": thread_id}
                if thread_id
                else {}
            ),
            user_id=user_id,
            title=title,
            metadata=metadata or {},
        )

        record = ChatThreadRecord(
            thread_id=contract.thread_id,
            user_id=contract.user_id,
            title=contract.title,
            status=contract.status,
            summary=contract.summary,
            message_count=contract.message_count,
            created_at=contract.created_at,
            updated_at=contract.updated_at,
            metadata_json=contract.metadata,
        )

        state = ConversationStateRecord(
            thread_id=contract.thread_id,
            summary="",
            active_entities={},
            active_strategy=None,
            portfolio_context={},
            pending_tasks=[],
            remembered_terms={},
            last_message_id=None,
            updated_at=contract.created_at,
            metadata_json={},
        )

        async with async_session() as session:
            try:
                async with session.begin():
                    session.add(record)
                    session.add(state)

            except IntegrityError:
                await session.rollback()

                existing = await self.get_thread(
                    contract.thread_id
                )

                if existing is not None:
                    return existing

                raise

        return contract

    async def get_thread(
        self,
        thread_id: str,
    ) -> ChatThread | None:
        async with async_session() as session:
            record = await session.get(
                ChatThreadRecord,
                thread_id,
            )

            if record is None:
                return None

            return _thread_contract(record)

    async def require_thread(
        self,
        thread_id: str,
    ) -> ChatThread:
        thread = await self.get_thread(thread_id)

        if thread is None:
            raise LookupError(
                f"Chat thread not found: {thread_id}"
            )

        return thread

    async def get_or_create_thread(
        self,
        *,
        thread_id: str | None = None,
        user_id: str | None = None,
        title: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ChatThread:
        if thread_id:
            existing = await self.get_thread(thread_id)

            if existing is not None:
                return existing

        return await self.create_thread(
            thread_id=thread_id,
            user_id=user_id,
            title=title,
            metadata=metadata,
        )

    async def append_message(
        self,
        *,
        thread_id: str,
        role: str,
        content: str,
        parent_message_id: str | None = None,
        message_id: str | None = None,
        client_message_id: str | None = None,
        intent: str | None = None,
        symbol: str | None = None,
        provider: str | None = None,
        model: str | None = None,
        tool_evidence_ids: Sequence[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ChatMessage:
        clean_content = content.strip()

        if not clean_content:
            raise ValueError(
                "Chat message content cannot be empty."
            )

        if client_message_id:
            existing = await self.get_message_by_client_id(
                thread_id=thread_id,
                client_message_id=client_message_id,
            )

            if existing is not None:
                return existing

        thread = await self.require_thread(thread_id)

        if thread.status != "active":
            raise ValueError(
                f"Cannot append to {thread.status} thread."
            )

        if parent_message_id:
            parent = await self.get_message(
                parent_message_id
            )

            if parent is None:
                raise LookupError(
                    "Parent chat message not found: "
                    f"{parent_message_id}"
                )

            if parent.thread_id != thread_id:
                raise ValueError(
                    "Parent message belongs to another thread."
                )

        contract = ChatMessage(
            **(
                {"message_id": message_id}
                if message_id
                else {}
            ),
            thread_id=thread_id,
            parent_message_id=parent_message_id,
            role=role,
            content=clean_content,
            intent=intent,
            symbol=symbol,
            provider=provider,
            model=model,
            tool_evidence_ids=list(
                tool_evidence_ids or []
            ),
            metadata=metadata or {},
        )

        record = ChatMessageRecord(
            message_id=contract.message_id,
            thread_id=contract.thread_id,
            parent_message_id=(
                contract.parent_message_id
            ),
            client_message_id=client_message_id,
            role=contract.role,
            content=contract.content,
            intent=contract.intent,
            symbol=contract.symbol,
            provider=contract.provider,
            model=contract.model,
            tool_evidence_ids=(
                contract.tool_evidence_ids
            ),
            created_at=contract.created_at,
            metadata_json=contract.metadata,
        )

        async with async_session() as session:
            async with session.begin():
                thread_record = await session.get(
                    ChatThreadRecord,
                    thread_id,
                    with_for_update=True,
                )

                if thread_record is None:
                    raise LookupError(
                        f"Chat thread not found: {thread_id}"
                    )

                session.add(record)

                thread_record.message_count = int(
                    thread_record.message_count or 0
                ) + 1
                thread_record.updated_at = utc_now()

                state_record = await session.get(
                    ConversationStateRecord,
                    thread_id,
                )

                if state_record is None:
                    state_record = ConversationStateRecord(
                        thread_id=thread_id,
                        summary="",
                        active_entities={},
                        active_strategy=None,
                        portfolio_context={},
                        pending_tasks=[],
                        remembered_terms={},
                        metadata_json={},
                    )
                    session.add(state_record)

                state_record.last_message_id = (
                    contract.message_id
                )
                state_record.updated_at = utc_now()

        return contract

    async def get_message(
        self,
        message_id: str,
    ) -> ChatMessage | None:
        async with async_session() as session:
            record = await session.get(
                ChatMessageRecord,
                message_id,
            )

            if record is None:
                return None

            return _message_contract(record)

    async def get_message_by_client_id(
        self,
        *,
        thread_id: str,
        client_message_id: str,
    ) -> ChatMessage | None:
        statement = (
            select(ChatMessageRecord)
            .where(
                ChatMessageRecord.thread_id
                == thread_id,
                ChatMessageRecord.client_message_id
                == client_message_id,
            )
            .limit(1)
        )

        async with async_session() as session:
            result = await session.execute(statement)
            record = result.scalar_one_or_none()

            if record is None:
                return None

            return _message_contract(record)

    async def list_messages(
        self,
        thread_id: str,
        *,
        limit: int = 50,
        oldest_first: bool = True,
    ) -> list[ChatMessage]:
        bounded_limit = max(
            1,
            min(int(limit), 500),
        )

        ordering = (
            ChatMessageRecord.created_at.asc()
            if oldest_first
            else ChatMessageRecord.created_at.desc()
        )

        statement = (
            select(ChatMessageRecord)
            .where(
                ChatMessageRecord.thread_id
                == thread_id
            )
            .order_by(
                ordering,
                ChatMessageRecord.message_id.asc(),
            )
            .limit(bounded_limit)
        )

        async with async_session() as session:
            result = await session.execute(statement)
            records = result.scalars().all()

        return [
            _message_contract(record)
            for record in records
        ]

    async def get_conversation_state(
        self,
        thread_id: str,
    ) -> ConversationState:
        await self.require_thread(thread_id)

        async with async_session() as session:
            record = await session.get(
                ConversationStateRecord,
                thread_id,
            )

            if record is None:
                return ConversationState(
                    thread_id=thread_id
                )

            return _state_contract(record)

    async def upsert_conversation_state(
        self,
        state: ConversationState,
    ) -> ConversationState:
        await self.require_thread(state.thread_id)

        async with async_session() as session:
            async with session.begin():
                record = await session.get(
                    ConversationStateRecord,
                    state.thread_id,
                    with_for_update=True,
                )

                if record is None:
                    record = ConversationStateRecord(
                        thread_id=state.thread_id,
                    )
                    session.add(record)

                record.summary = state.summary
                record.active_entities = dict(
                    state.active_entities
                )
                record.active_strategy = (
                    dict(state.active_strategy)
                    if state.active_strategy
                    else None
                )
                record.portfolio_context = dict(
                    state.portfolio_context
                )
                record.pending_tasks = [
                    (
                        task.model_dump(
                            mode="json"
                        )
                        if hasattr(task, "model_dump")
                        else dict(task)
                    )
                    for task in state.pending_tasks
                ]
                record.remembered_terms = dict(
                    state.remembered_terms
                )
                record.last_message_id = (
                    state.last_message_id
                )
                record.updated_at = utc_now()
                record.metadata_json = dict(
                    state.metadata
                )

                thread = await session.get(
                    ChatThreadRecord,
                    state.thread_id,
                    with_for_update=True,
                )

                if thread is not None:
                    thread.summary = (
                        state.summary or None
                    )
                    thread.updated_at = utc_now()

        return await self.get_conversation_state(
            state.thread_id
        )

    async def upsert_memory_fact(
        self,
        memory: MemoryFact,
    ) -> MemoryFact:
        await self.require_thread(memory.thread_id)

        statement = (
            select(MemoryFactRecord)
            .where(
                MemoryFactRecord.thread_id
                == memory.thread_id,
                MemoryFactRecord.key == memory.key,
                MemoryFactRecord.status == "active",
            )
            .order_by(
                MemoryFactRecord.updated_at.desc()
            )
            .limit(1)
        )

        async with async_session() as session:
            async with session.begin():
                result = await session.execute(
                    statement
                )
                record = result.scalar_one_or_none()

                if record is None:
                    record = MemoryFactRecord(
                        memory_id=memory.memory_id,
                        thread_id=memory.thread_id,
                        key=memory.key,
                        value_json=memory.value,
                        confidence=memory.confidence,
                        status=memory.status,
                        source_message_id=(
                            memory.source_message_id
                        ),
                        created_at=memory.created_at,
                        updated_at=memory.updated_at,
                        metadata_json=memory.metadata,
                    )
                    session.add(record)

                else:
                    record.value_json = memory.value
                    record.confidence = (
                        memory.confidence
                    )
                    record.status = memory.status
                    record.source_message_id = (
                        memory.source_message_id
                    )
                    record.updated_at = utc_now()
                    record.metadata_json = dict(
                        memory.metadata
                    )

        active = await self.get_memory_fact(
            thread_id=memory.thread_id,
            key=memory.key,
        )

        if active is None:
            raise RuntimeError(
                "Memory fact was not persisted."
            )

        return active

    async def get_memory_fact(
        self,
        *,
        thread_id: str,
        key: str,
    ) -> MemoryFact | None:
        statement = (
            select(MemoryFactRecord)
            .where(
                MemoryFactRecord.thread_id
                == thread_id,
                MemoryFactRecord.key == key,
                MemoryFactRecord.status == "active",
            )
            .order_by(
                MemoryFactRecord.updated_at.desc()
            )
            .limit(1)
        )

        async with async_session() as session:
            result = await session.execute(statement)
            record = result.scalar_one_or_none()

            if record is None:
                return None

            return _memory_contract(record)

    async def list_memory_facts(
        self,
        thread_id: str,
        *,
        active_only: bool = True,
        limit: int = 200,
    ) -> list[MemoryFact]:
        statement = select(MemoryFactRecord).where(
            MemoryFactRecord.thread_id == thread_id
        )

        if active_only:
            statement = statement.where(
                MemoryFactRecord.status == "active"
            )

        statement = (
            statement
            .order_by(
                MemoryFactRecord.updated_at.desc()
            )
            .limit(
                max(1, min(int(limit), 1000))
            )
        )

        async with async_session() as session:
            result = await session.execute(statement)
            records = result.scalars().all()

        return [
            _memory_contract(record)
            for record in records
        ]

    async def retract_memory_fact(
        self,
        *,
        thread_id: str,
        key: str,
    ) -> bool:
        statement = (
            select(MemoryFactRecord)
            .where(
                MemoryFactRecord.thread_id
                == thread_id,
                MemoryFactRecord.key == key,
                MemoryFactRecord.status == "active",
            )
            .order_by(
                MemoryFactRecord.updated_at.desc()
            )
            .limit(1)
        )

        async with async_session() as session:
            async with session.begin():
                result = await session.execute(
                    statement
                )
                record = result.scalar_one_or_none()

                if record is None:
                    return False

                record.status = "retracted"
                record.updated_at = utc_now()

        return True

    async def add_tool_evidence(
        self,
        evidence: ToolEvidence,
    ) -> ToolEvidence:
        await self.require_thread(evidence.thread_id)

        record = ToolEvidenceRecord(
            evidence_id=evidence.evidence_id,
            thread_id=evidence.thread_id,
            tool_name=evidence.tool_name,
            tool_call_id=evidence.tool_call_id,
            claim_types=evidence.claim_types,
            request_json=evidence.request,
            result_json=evidence.result,
            status=evidence.status,
            observed_at=evidence.observed_at,
            expires_at=evidence.expires_at,
            metadata_json=evidence.metadata,
        )

        async with async_session() as session:
            async with session.begin():
                session.add(record)

        return evidence

    async def list_tool_evidence(
        self,
        thread_id: str,
        *,
        limit: int = 100,
    ) -> list[ToolEvidence]:
        statement = (
            select(ToolEvidenceRecord)
            .where(
                ToolEvidenceRecord.thread_id
                == thread_id
            )
            .order_by(
                ToolEvidenceRecord.observed_at.desc()
            )
            .limit(
                max(1, min(int(limit), 500))
            )
        )

        async with async_session() as session:
            result = await session.execute(statement)
            records = result.scalars().all()

        return [
            _evidence_contract(record)
            for record in records
        ]

    async def archive_thread(
        self,
        thread_id: str,
    ) -> ChatThread:
        async with async_session() as session:
            async with session.begin():
                record = await session.get(
                    ChatThreadRecord,
                    thread_id,
                    with_for_update=True,
                )

                if record is None:
                    raise LookupError(
                        f"Chat thread not found: {thread_id}"
                    )

                record.status = "archived"
                record.updated_at = utc_now()

        archived = await self.require_thread(thread_id)
        return archived

    async def load_context_bundle(
        self,
        thread_id: str,
        *,
        message_limit: int = 20,
        memory_limit: int = 100,
        evidence_limit: int = 50,
    ) -> dict[str, Any]:
        thread = await self.require_thread(thread_id)

        messages = await self.list_messages(
            thread_id,
            limit=message_limit,
            oldest_first=True,
        )

        state = await self.get_conversation_state(
            thread_id
        )

        memories = await self.list_memory_facts(
            thread_id,
            active_only=True,
            limit=memory_limit,
        )

        evidence = await self.list_tool_evidence(
            thread_id,
            limit=evidence_limit,
        )

        return {
            "thread": thread,
            "messages": messages,
            "conversation_state": state,
            "memory_facts": memories,
            "tool_evidence": evidence,
        }

    async def delete_thread_for_testing(
        self,
        thread_id: str,
    ) -> None:
        """
        Explicit test cleanup helper.

        The live chat path should archive rather than delete threads.
        """

        async with async_session() as session:
            async with session.begin():
                await session.execute(
                    delete(ToolEvidenceRecord).where(
                        ToolEvidenceRecord.thread_id
                        == thread_id
                    )
                )

                await session.execute(
                    delete(MemoryFactRecord).where(
                        MemoryFactRecord.thread_id
                        == thread_id
                    )
                )

                await session.execute(
                    delete(ConversationStateRecord).where(
                        ConversationStateRecord.thread_id
                        == thread_id
                    )
                )

                await session.execute(
                    delete(ChatMessageRecord).where(
                        ChatMessageRecord.thread_id
                        == thread_id
                    )
                )

                await session.execute(
                    delete(ChatThreadRecord).where(
                        ChatThreadRecord.thread_id
                        == thread_id
                    )
                )

    async def healthcheck(self) -> dict[str, Any]:
        try:
            async with async_session() as session:
                await session.execute(
                    select(ChatThreadRecord.thread_id)
                    .limit(1)
                )

            return {
                "stack": "chat_public",
                "component": "conversation_store",
                "status": "ok",
                "persistent": True,
            }

        except Exception as error:
            return {
                "stack": "chat_public",
                "component": "conversation_store",
                "status": "error",
                "persistent": False,
                "error": (
                    f"{type(error).__name__}: {error}"
                ),
            }


conversation_store = ConversationStore()


async def healthcheck() -> dict[str, Any]:
    return await conversation_store.healthcheck()
