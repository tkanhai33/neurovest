"""Optional V5 grounded developer awareness integration.

Feature flag: NEURO_V5_GROUNDED_AWARENESS=1
No public or ordinary-user entry point.
"""
from __future__ import annotations

import asyncio
import os
from pathlib import Path

from backend.app.stacks.chat_public.developer_role_guard import (
    authenticated_developer_role,
)


async def maybe_grounded_developer_answer(
    *, root, principal, thread, question,
):
    if os.environ.get("NEURO_V5_GROUNDED_AWARENESS") != "1":
        return None

    # Fail closed before repository evidence or inference access.
    if not authenticated_developer_role(principal):
        return None

    owner = str(getattr(principal, "subject", "") or "").strip()
    thread_owner = str(getattr(thread, "user_id", "") or "").strip()
    thread_id = str(getattr(thread, "thread_id", "") or "").strip()

    if not owner or not thread_id or owner != thread_owner:
        return None

    if not isinstance(question, str):
        return None

    question = question.strip()

    if not question or len(question) > 2000:
        return None

    root = Path(root).resolve()
    index_path = (
        root / "runtime/qualification/"
        "neuro_v5_developer_candidate/evidence_index.json"
    )

    try:
        from backend.app.stacks.chat_public.developer_model_synthesis_v5 import (
            synthesize_developer_answer,
        )
        from backend.app.stacks.chat_public.developer_ollama_bridge_v5 import (
            make_local_model,
        )

        # Local-only inference. Never accepts an endpoint from
        # a user message or a model-generated instruction.
        model = make_local_model(timeout=45.0)

        return await synthesize_developer_answer(
            root=root,
            index_path=index_path,
            question=question,
            principal=principal,
            thread=thread,
            model=model,
        )
    except asyncio.CancelledError:
        raise
    except Exception:
        # Old authenticated V3 path remains the fallback.
        return None
