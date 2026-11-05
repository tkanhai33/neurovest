
from __future__ import annotations

import copy
import re
from typing import Any

from .neuro_improvement_service_f73b import (
    ImprovementService,
    VerifiedDeveloper,
)


class ImprovementBoundaryError(PermissionError):
    pass


def _safe(value: Any, maximum: int = 160) -> str:
    text = str(value if value is not None else "")
    text = re.sub(r"[\x00-\x1f\x7f]+", " ", text)
    return " ".join(text.split())[:maximum]


async def enrich_verified_r4_assessment(
    *,
    assessment: dict[str, Any],
    principal_owner: str,
    thread_owner: str,
    verified_developer: bool,
    engine: Any,
) -> dict[str, Any]:
    """
    Called only after NeuroVest's existing R4
    authorization, thread-owner check and report
    validation in run_chat_turn().

    SQL progress is supplemental evidence, never
    a substitute for the verified R4 assessment.
    """

    if (
        verified_developer is not True
        or not isinstance(principal_owner, str)
        or not principal_owner.strip()
        or thread_owner != principal_owner
    ):
        raise ImprovementBoundaryError(
            "VERIFIED_OWNER_DEVELOPER_REQUIRED"
        )

    if (
        not isinstance(assessment, dict)
        or assessment.get("status") != "ok"
        or assessment.get("read_only") is not True
        or assessment.get("broker_execution_allowed") is not False
        or assessment.get("production_approval_granted") is not False
        or not isinstance(assessment.get("recommendations"), list)
        or len(assessment["recommendations"]) != 5
        or not isinstance(assessment.get("answer"), str)
        or not assessment["answer"].strip()
    ):
        raise ImprovementBoundaryError(
            "QUALIFIED_R4_ASSESSMENT_REQUIRED"
        )

    original = copy.deepcopy(assessment)

    principal = VerifiedDeveloper(
        user_id=principal_owner,
        verified=True,
        role="developer",
    )

    progress = {
        "available": False,
        "tasks": [],
        "reason": "improvement_database_unavailable",
    }

    try:
        service = ImprovementService(engine)
        tasks = await service.list_tasks(principal)

        if not isinstance(tasks, list):
            raise ValueError("INVALID_TASK_RESULT")

        # F69 enforces owner scoping. Recheck every
        # returned row before displaying anything.
        for task in tasks:
            if (
                not isinstance(task, dict)
                or task.get("owner_id") != principal_owner
            ):
                raise ImprovementBoundaryError(
                    "PROGRESS_OWNER_MISMATCH"
                )

        progress = {
            "available": True,
            "tasks": copy.deepcopy(tasks),
            "reason": None,
        }

    except ImprovementBoundaryError:
        # A scope violation is a security failure,
        # not a harmless database outage.
        raise

    except Exception as _nv_f89_progress_error:
        import logging as _nv_f89_logging
        _nv_f89_logging.getLogger(__name__).warning(
            "NEURO_PROGRESS_READ_UNAVAILABLE exception_type=%s",
            type(_nv_f89_progress_error).__name__,
        )

    enriched = copy.deepcopy(original)
    enriched["improvement_progress"] = progress

    lines = [
        original["answer"].rstrip(),
        "",
        "Persistent improvement progress:",
    ]

    if not progress["available"]:
        lines.append(
            "Progress tracking is currently unavailable. "
            "No task completion is assumed."
        )
    elif not progress["tasks"]:
        lines.append(
            "No persistent improvement tasks have been "
            "recorded for this developer."
        )
    else:
        for task in progress["tasks"][:10]:
            title = _safe(task.get("title"), 130)
            status = _safe(task.get("status"), 40)
            capability = _safe(
                task.get("capability_key"), 64
            )
            lines.append(
                f"- [{status}] {title} ({capability})"
            )

        remaining = len(progress["tasks"]) - 10
        if remaining > 0:
            lines.append(
                f"{remaining} additional tasks are "
                "available in persistent progress."
            )

    lines.extend([
        "",
        "Improvement progress is informational only. "
        "It does not authorize deployment, strategy "
        "promotion, or live trading.",
    ])

    enriched["answer"] = "\n".join(lines)

    for key, value in original.items():
        if key != "answer" and enriched.get(key) != value:
            raise RuntimeError(
                "VERIFIED_R4_FIELD_MUTATED"
            )

    return enriched
