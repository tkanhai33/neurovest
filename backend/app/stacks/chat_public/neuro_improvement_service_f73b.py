"""
NeuroVest F69 candidate.

Owner-scoped improvement tracking with:
- server-authorized developer access
- evidence-bound completion
- PostgreSQL persistence
- owner-isolated reads and writes
- non-fabricating outage fallback

Staged implementation only.
Not connected to production chat or broker execution.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import uuid

from dataclasses import dataclass
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


STATUSES = {
    "identified",
    "planned",
    "in_progress",
    "blocked",
    "validated",
}

KEY_PATTERN = re.compile(
    r"^[a-z][a-z0-9_.-]{2,95}$"
)


class ImprovementAuthorizationError(PermissionError):
    pass


class ImprovementValidationError(ValueError):
    pass


@dataclass(frozen=True)
class VerifiedDeveloper:
    """
    Trusted service-boundary context.

    The caller must construct this only after
    the existing JWT and developer-role checks.
    Client input must never create this authority.
    """
    user_id: str
    verified: bool
    role: str


def authorize(principal: VerifiedDeveloper) -> str:
    if not isinstance(principal, VerifiedDeveloper):
        raise ImprovementAuthorizationError(
            "TRUSTED_PRINCIPAL_REQUIRED"
        )

    if (
        not principal.verified
        or principal.role != "developer"
        or not principal.user_id.strip()
    ):
        raise ImprovementAuthorizationError(
            "VERIFIED_DEVELOPER_REQUIRED"
        )

    return principal.user_id.strip()


def digest_evidence(evidence: dict[str, Any]) -> str:
    if not isinstance(evidence, dict) or not evidence:
        raise ImprovementValidationError(
            "EVIDENCE_REQUIRED"
        )

    encoded = json.dumps(
        evidence,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )

    return hashlib.sha256(
        encoded.encode("utf-8")
    ).hexdigest()


class ImprovementService:
    def __init__(self, engine: AsyncEngine):
        if not isinstance(engine, AsyncEngine):
            raise TypeError("ASYNC_ENGINE_REQUIRED")

        self.engine = engine

    async def initialize(self) -> None:
        """
        Qualification schema bootstrap only.
        Production deployment requires an
        approved migration instead.
        """
        async with self.engine.begin() as conn:
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS
                nv_improvement_tasks_f69 (
                    task_id UUID PRIMARY KEY,
                    owner_id TEXT NOT NULL,
                    capability_key VARCHAR(96) NOT NULL,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    evidence_sha256 CHAR(64),
                    evidence_json JSONB,
                    detail TEXT NOT NULL DEFAULT '',
                    revision INTEGER NOT NULL DEFAULT 1,
                    created_at TIMESTAMPTZ NOT NULL
                        DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL
                        DEFAULT NOW(),
                    CONSTRAINT nv_f69_status_valid CHECK (
                        status IN (
                            'identified',
                            'planned',
                            'in_progress',
                            'blocked',
                            'validated'
                        )
                    ),
                    CONSTRAINT nv_f69_revision_valid CHECK (
                        revision >= 1
                    ),
                    UNIQUE (owner_id, capability_key)
                )
            """))

            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS
                nv_f69_owner_status_idx
                ON nv_improvement_tasks_f69
                (owner_id, status)
            """))

    @staticmethod
    def _record(row) -> dict[str, Any]:
        data = dict(row)

        data["task_id"] = str(data["task_id"])

        if data.get("evidence_json") is not None:
            data["evidence_json"] = copy.deepcopy(
                data["evidence_json"]
            )

        return data

    async def create_task(
        self,
        principal: VerifiedDeveloper,
        capability_key: str,
        title: str,
        *,
        detail: str = "",
        evidence: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        owner = authorize(principal)

        if not KEY_PATTERN.fullmatch(capability_key):
            raise ImprovementValidationError(
                "CAPABILITY_KEY_INVALID"
            )

        if not title.strip() or len(title) > 300:
            raise ImprovementValidationError(
                "TITLE_INVALID"
            )

        if len(detail) > 4000:
            raise ImprovementValidationError(
                "DETAIL_TOO_LONG"
            )

        evidence_sha = (
            digest_evidence(evidence)
            if evidence is not None
            else None
        )

        task_id = str(uuid.uuid4())

        async with self.engine.begin() as conn:
            result = await conn.execute(
                text("""
                    INSERT INTO nv_improvement_tasks_f69
                    (
                        task_id,
                        owner_id,
                        capability_key,
                        title,
                        status,
                        detail,
                        evidence_sha256,
                        evidence_json
                    )
                    VALUES (
                        CAST(:task_id AS UUID),
                        :owner,
                        :capability,
                        :title,
                        'identified',
                        :detail,
                        :evidence_sha,
                        CAST(:evidence_json AS JSONB)
                    )
                    RETURNING
                        task_id,
                        owner_id,
                        capability_key,
                        title,
                        status,
                        detail,
                        evidence_sha256,
                        evidence_json,
                        revision
                """),
                {
                    "task_id": task_id,
                    "owner": owner,
                    "capability": capability_key,
                    "title": title.strip(),
                    "detail": detail,
                    "evidence_sha": evidence_sha,
                    "evidence_json": (
                        json.dumps(evidence)
                        if evidence is not None
                        else None
                    ),
                },
            )

            row = result.mappings().one()

        return self._record(row)

    async def list_tasks(
        self,
        principal: VerifiedDeveloper,
    ) -> list[dict[str, Any]]:
        owner = authorize(principal)

        async with self.engine.connect() as conn:
            result = await conn.execute(
                text("""
                    SELECT
                        task_id,
                        owner_id,
                        capability_key,
                        title,
                        status,
                        detail,
                        evidence_sha256,
                        evidence_json,
                        revision
                    FROM nv_improvement_tasks_f69
                    WHERE owner_id = :owner
                    ORDER BY capability_key
                """),
                {"owner": owner},
            )

            return [
                self._record(row)
                for row in result.mappings().all()
            ]

    async def get_task(
        self,
        principal: VerifiedDeveloper,
        task_id: str,
    ) -> dict[str, Any] | None:
        owner = authorize(principal)

        try:
            normalized = str(uuid.UUID(task_id))
        except (TypeError, ValueError, AttributeError):
            return None

        async with self.engine.connect() as conn:
            result = await conn.execute(
                text("""
                    SELECT
                        task_id,
                        owner_id,
                        capability_key,
                        title,
                        status,
                        detail,
                        evidence_sha256,
                        evidence_json,
                        revision
                    FROM nv_improvement_tasks_f69
                    WHERE owner_id = :owner
                      AND task_id = CAST(:task_id AS UUID)
                """),
                {
                    "owner": owner,
                    "task_id": normalized,
                },
            )

            row = result.mappings().first()

            return (
                self._record(row)
                if row is not None
                else None
            )

    async def update_task(
        self,
        principal: VerifiedDeveloper,
        task_id: str,
        *,
        status: str,
        detail: str,
        evidence: dict[str, Any] | None = None,
        expected_revision: int,
    ) -> dict[str, Any] | None:
        owner = authorize(principal)

        try:
            normalized = str(uuid.UUID(task_id))
        except (TypeError, ValueError, AttributeError):
            return None

        if status not in STATUSES:
            raise ImprovementValidationError(
                "STATUS_INVALID"
            )

        if not isinstance(detail, str) or len(detail) > 4000:
            raise ImprovementValidationError(
                "DETAIL_INVALID"
            )

        if (
            isinstance(expected_revision, bool)
            or not isinstance(expected_revision, int)
            or expected_revision < 1
        ):
            raise ImprovementValidationError(
                "REVISION_INVALID"
            )

        if status == "validated" and evidence is None:
            raise ImprovementValidationError(
                "VALIDATION_EVIDENCE_REQUIRED"
            )

        evidence_sha = (
            digest_evidence(evidence)
            if evidence is not None
            else None
        )

        async with self.engine.begin() as conn:
            result = await conn.execute(
                text("""
                    UPDATE nv_improvement_tasks_f69
                    SET
                        status = :status,
                        detail = :detail,
                        evidence_sha256 =
                            COALESCE(
                                :evidence_sha,
                                evidence_sha256
                            ),
                        evidence_json =
                            COALESCE(
                                CAST(:evidence_json AS JSONB),
                                evidence_json
                            ),
                        revision = revision + 1,
                        updated_at = NOW()
                    WHERE owner_id = :owner
                      AND task_id = CAST(:task_id AS UUID)
                      AND revision = :revision
                    RETURNING
                        task_id,
                        owner_id,
                        capability_key,
                        title,
                        status,
                        detail,
                        evidence_sha256,
                        evidence_json,
                        revision
                """),
                {
                    "owner": owner,
                    "task_id": normalized,
                    "status": status,
                    "detail": detail,
                    "revision": expected_revision,
                    "evidence_sha": evidence_sha,
                    "evidence_json": (
                        json.dumps(evidence)
                        if evidence is not None
                        else None
                    ),
                },
            )

            row = result.mappings().first()

            return (
                self._record(row)
                if row is not None
                else None
            )

    async def delete_task(
        self,
        principal: VerifiedDeveloper,
        task_id: str,
    ) -> bool:
        owner = authorize(principal)

        try:
            normalized = str(uuid.UUID(task_id))
        except (TypeError, ValueError, AttributeError):
            return False

        async with self.engine.begin() as conn:
            result = await conn.execute(
                text("""
                    DELETE FROM nv_improvement_tasks_f69
                    WHERE owner_id = :owner
                      AND task_id = CAST(:task_id AS UUID)
                """),
                {
                    "owner": owner,
                    "task_id": normalized,
                },
            )

            return result.rowcount == 1


def merge_assessment(
    verified_assessment: dict[str, Any],
    tasks: list[dict[str, Any]] | None,
    *,
    sql_available: bool,
) -> dict[str, Any]:
    """
    Preserve original verified evidence.

    Task progress is included only when fetched
    successfully from the owner-scoped service.

    This function never manufactures completion.
    """
    result = copy.deepcopy(verified_assessment)

    if not isinstance(result, dict):
        raise ImprovementValidationError(
            "ASSESSMENT_INVALID"
        )

    if not sql_available:
        result["improvement_progress"] = {
            "available": False,
            "source": "unavailable",
            "tasks": [],
            "note": (
                "Persistent improvement progress "
                "could not be verified."
            ),
        }
        return result

    if tasks is None:
        raise ImprovementValidationError(
            "AVAILABLE_TASKS_REQUIRED"
        )

    result["improvement_progress"] = {
        "available": True,
        "source": "owner_scoped_postgresql",
        "tasks": copy.deepcopy(tasks),
        "count": len(tasks),
    }

    return result


async def assess_with_progress(
    assessment: dict[str, Any],
    principal: VerifiedDeveloper,
    service: ImprovementService,
) -> dict[str, Any]:
    """
    Fail closed on authorization, but degrade
    gracefully on unavailable SQL progress.
    """
    authorize(principal)

    try:
        tasks = await service.list_tasks(principal)
    except (
        OSError,
        ConnectionError,
        TimeoutError,
    ):
        return merge_assessment(
            assessment,
            None,
            sql_available=False,
        )
    except Exception as exc:
        from sqlalchemy.exc import SQLAlchemyError

        if not isinstance(exc, SQLAlchemyError):
            raise

        return merge_assessment(
            assessment,
            None,
            sql_available=False,
        )

    return merge_assessment(
        assessment,
        tasks,
        sql_available=True,
    )
