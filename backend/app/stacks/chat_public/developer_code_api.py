"""Developer-only local Ollama code proposal API.

Generates and reads proposals. Never applies source mutations.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.app.stacks.identity_auth.api_dependencies import (
    require_authenticated_principal,
)
from backend.app.stacks.identity_auth.contracts import (
    AuthenticatedPrincipal,
)

from backend.app.stacks.chat_public.developer_role_guard import (
    authenticated_developer_role,
)

ROOT = Path(__file__).resolve().parents[4]
GENERATOR = ROOT / "scripts/neuro_developer_patch_preview.py"
PROPOSALS = ROOT / "runtime/developer_patch_proposals"

ALLOWED_SOURCE = (
    "backend/app/stacks/chat_public/"
    "developer_repository_inspection.py"
)

# NEUROVEST_PATCH_SCOPE_EXPANSION_V1
ALLOWED_PATCH_SOURCES = (
    ALLOWED_SOURCE,
    'backend/app/stacks/chat_public/developer_self_review.py',
)

router = APIRouter(prefix="/api/v1/developer/code", tags=["developer-code"])
_generation_lock = asyncio.Lock()


class CodeProposalRequest(BaseModel):
    task: str = Field(min_length=12, max_length=1500)
    source_file: str = ALLOWED_SOURCE


def _require_developer(principal: AuthenticatedPrincipal) -> None:
    """Fail closed unless the trusted principal explicitly has developer role."""
    if not authenticated_developer_role(principal):
        raise HTTPException(
            status_code=403,
            detail="Authenticated developer role required.",
        )


def _read_proposal(proposal_id: str) -> dict:
    if (
        not proposal_id.startswith("proposal_")
        or len(proposal_id) > 110
        or not all(
            c.isascii() and (c.isalnum() or c == "_")
            for c in proposal_id
        )
    ):
        raise HTTPException(404, "Proposal not found.")

    folder = PROPOSALS / proposal_id

    if folder.is_symlink() or not folder.is_dir():
        raise HTTPException(404, "Proposal not found.")

    meta = folder / "proposal.json"
    diff = folder / "change.diff"

    if (
        not meta.is_file()
        or not diff.is_file()
        or meta.is_symlink()
        or diff.is_symlink()
    ):
        raise HTTPException(404, "Proposal not found.")

    try:
        if meta.stat().st_size > 16000 or diff.stat().st_size > 32000:
            raise ValueError("Oversized proposal.")

        metadata = json.loads(meta.read_text("utf-8"))
        patch = diff.read_text("utf-8")

        if (
            metadata.get("type") != "developer_patch_preview"
            or metadata.get("source_file") not in ALLOWED_PATCH_SOURCES
        ):
            raise ValueError("Invalid proposal.")

    except (OSError, ValueError, TypeError):
        raise HTTPException(404, "Proposal not found.")

    return {
        "proposal_id": proposal_id,
        "metadata": metadata,
        "diff": patch,
    }


@router.post("/proposals")
async def generate_code_proposal(
    payload: CodeProposalRequest,
    principal: AuthenticatedPrincipal = Depends(
        require_authenticated_principal
    ),
):
    _require_developer(principal)

    if payload.source_file not in ALLOWED_PATCH_SOURCES:
        raise HTTPException(
            400, "Source outside the initial developer scope."
        )

    if _generation_lock.locked():
        raise HTTPException(
            409, "A developer proposal is already generating."
        )

    async with _generation_lock:
        before = {
            p.name for p in PROPOSALS.glob("proposal_*")
            if p.is_dir() and not p.is_symlink()
        } if PROPOSALS.is_dir() else set()

        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"

        proc = await asyncio.create_subprocess_exec(
            sys.executable,
            str(GENERATOR),
            "--file",
            payload.source_file,
            "--task",
            payload.task,
            cwd=str(ROOT),
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        try:
            stdout, _ = await asyncio.wait_for(
                proc.communicate(),
                timeout=195,
            )
        except asyncio.TimeoutError:
            proc.kill()
            await proc.communicate()
            raise HTTPException(504, "Local model timed out.")

        if proc.returncode != 0:
            raise HTTPException(
                422,
                "Local patch generation failed: "
                + stdout.decode("utf-8", errors="replace")[-700:],
            )

        after = {
            p.name for p in PROPOSALS.glob("proposal_*")
            if p.is_dir() and not p.is_symlink()
        }

        created = after - before

        if len(created) != 1:
            raise HTTPException(
                500,
                "Could not uniquely identify the generated proposal.",
            )

        result = _read_proposal(created.pop())
        result["applied"] = False
        result["approval_required"] = True
        return result


@router.get("/proposals/{proposal_id}")
async def get_code_proposal(
    proposal_id: str,
    principal: AuthenticatedPrincipal = Depends(
        require_authenticated_principal
    ),
):
    _require_developer(principal)
    return _read_proposal(proposal_id)
