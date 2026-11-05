from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

SCHEMA = "neuro-improvement-backlog-v1"
STATES = frozenset({
    "open", "in_progress", "blocked",
    "review_required", "completed"
})

def canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=True
    )

def digest(value):
    return hashlib.sha256(
        canonical(value).encode("utf-8")
    ).hexdigest()

def task_id(finding):
    key = str(finding["id"])
    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,100}", key):
        raise ValueError("Invalid improvement identifier")
    return "NVIMP-" + digest(key)[:16]

def evidence_signature(report):
    # Include only non-sensitive, allowlisted qualification
    # status and decision signals, not raw evidence content.
    allowed = {}

    for name, row in report.get("qualifications", {}).items():
        if not isinstance(row, dict):
            continue
        allowed[str(name)[:80]] = {
            "status": str(row.get("status", ""))[:40],
            "decision": str(row.get("decision", ""))[:120],
        }

    return digest(allowed)

def planned_tasks(report):
    recommendations = report.get("recommendations", [])

    if not isinstance(recommendations, list):
        raise ValueError("Recommendations must be a list")

    items = {}
    signature = evidence_signature(report)

    for finding in recommendations:
        if not isinstance(finding, dict):
            raise ValueError("Invalid recommendation")

        identifier = task_id(finding)

        if identifier in items:
            raise ValueError("Duplicate improvement identity")

        score = float(finding.get("score", 0))

        if not 0 <= score <= 100:
            raise ValueError("Invalid improvement score")

        items[identifier] = {
            "task_id": identifier,
            "finding_id": str(finding["id"]),
            "title": str(finding.get("title", ""))[:180],
            "capability": str(finding.get("capability", ""))[:80],
            "priority_score": score,
            "observation": str(
                finding.get("observation", "")
            )[:500],
            "next_action": str(
                finding.get("next_action", "")
            )[:500],
            "validation": str(
                finding.get("validation", "")
            )[:500],
            "evidence_signature": signature,
        }

    return items

def reconcile(report, prior=None):
    """
    Merge fresh findings with previous reviewed state.

    Completion never occurs automatically.
    Disappearing findings enter review rather than
    silently being considered resolved.
    """
    previous = (
        prior.get("tasks", {})
        if isinstance(prior, dict) else {}
    )

    if not isinstance(previous, dict):
        raise ValueError("Invalid previous backlog")

    proposed = planned_tasks(report)
    merged = {}
    changes = []

    for identifier, item in proposed.items():
        old = previous.get(identifier)

        if old is None:
            merged[identifier] = {
                **item,
                "state": "open",
                "review_note": None,
                "completion_evidence": None,
            }
            changes.append({
                "task_id": identifier,
                "event": "discovered",
            })
            continue

        state = old.get("state", "open")
        if state not in STATES:
            raise ValueError("Invalid previous task state")

        merged[identifier] = {
            **item,
            "state": state,
            "review_note": old.get("review_note"),
            "completion_evidence": old.get(
                "completion_evidence"
            ),
        }

        if old.get("priority_score") != item["priority_score"]:
            changes.append({
                "task_id": identifier,
                "event": "priority_changed",
                "old_score": old.get("priority_score"),
                "new_score": item["priority_score"],
            })

        if (
            old.get("evidence_signature")
            != item["evidence_signature"]
        ):
            changes.append({
                "task_id": identifier,
                "event": "qualification_evidence_changed",
            })

        # A completed task resurfacing requires developer
        # review rather than being silently reopened or ignored.
        if state == "completed":
            merged[identifier]["state"] = "review_required"
            merged[identifier]["review_note"] = (
                "Previously completed finding has reappeared."
            )
            changes.append({
                "task_id": identifier,
                "event": "completed_finding_reappeared",
            })

    for identifier, old in previous.items():
        if identifier in merged:
            continue

        if not isinstance(old, dict):
            raise ValueError("Invalid previous task entry")

        if old.get("state") == "completed":
            merged[identifier] = dict(old)
        else:
            merged[identifier] = {
                **old,
                "state": "review_required",
                "review_note": (
                    "Finding absent from latest assessment; "
                    "completion is not established."
                ),
            }
            if old.get("state") != "review_required":
                changes.append({
                    "task_id": identifier,
                    "event": "finding_disappeared",
                })

    ordered = dict(sorted(
        merged.items(),
        key=lambda pair: (
            -float(pair[1].get("priority_score", 0)),
            pair[0],
        )
    ))

    return {
        "schema_version": SCHEMA,
        "evidence_signature": evidence_signature(report),
        "tasks": ordered,
        "changes": changes,
        "approval_required": True,
        "deployment_approved": False,
        "live_trading_approved": False,
    }

def transition(
    backlog, identifier, target,
    *,
    authorized=False,
    note=None,
    completion_evidence=None,
):
    """
    Explicit developer action, never model-generated
    approval. Authorization is supplied by a trusted
    caller; no HTTP authentication is implemented here.
    """
    if not authorized:
        raise PermissionError(
            "Developer authorization required"
        )

    if target not in STATES:
        raise ValueError("Unknown target state")

    tasks = backlog.get("tasks", {})
    if identifier not in tasks:
        raise KeyError("Unknown task")

    old = tasks[identifier]
    previous_state = old["state"]

    allowed = {
        "open": {"in_progress", "blocked", "review_required"},
        "in_progress": {
            "open", "blocked", "review_required"
        },
        "blocked": {
            "open", "in_progress", "review_required"
        },
        "review_required": {
            "open", "in_progress", "blocked", "completed"
        },
        "completed": {"review_required"},
    }

    if target not in allowed[previous_state]:
        raise ValueError("Disallowed state transition")

    if target == "completed":
        if not isinstance(completion_evidence, str):
            raise ValueError("Completion evidence required")
        if not re.fullmatch(
            r"[a-f0-9]{64}", completion_evidence
        ):
            raise ValueError(
                "Completion evidence must be SHA256"
            )

    updated = json.loads(canonical(backlog))
    updated["tasks"][identifier]["state"] = target
    updated["tasks"][identifier]["review_note"] = (
        str(note)[:500] if note is not None else None
    )

    if target == "completed":
        updated["tasks"][identifier][
            "completion_evidence"
        ] = completion_evidence

    updated["changes"] = [{
        "task_id": identifier,
        "event": "developer_transition",
        "from": previous_state,
        "to": target,
    }]

    return updated

def store(backlog, destination):
    destination = Path(destination)
    parent = destination.parent.resolve()

    if not parent.is_dir():
        raise FileNotFoundError(
            "Existing private progress directory required"
        )

    if destination.is_symlink():
        raise ValueError("Symlink target forbidden")

    if destination.exists():
        raise FileExistsError(
            "Snapshot must not overwrite prior evidence"
        )

    data = canonical(backlog) + "\n"
    fd = os.open(
        destination,
        os.O_CREAT | os.O_EXCL | os.O_WRONLY,
        0o600,
    )

    with os.fdopen(fd, "w", encoding="utf-8") as file:
        file.write(data)

    return digest(backlog)

def load(destination):
    destination = Path(destination)

    if destination.is_symlink():
        raise ValueError("Symlink source forbidden")

    if destination.stat().st_size > 2_000_000:
        raise ValueError("Backlog exceeds allowed size")

    data = json.loads(destination.read_text())

    if data.get("schema_version") != SCHEMA:
        raise ValueError("Unknown backlog schema")

    return data

def render(backlog, limit=8):
    lines = [
        "NEURO DEVELOPMENT BACKLOG",
        "Developer-reviewed state; no automatic deployment.",
        "",
    ]

    for index, item in enumerate(
        list(backlog["tasks"].values())[:limit], 1
    ):
        lines.extend([
            f"{index}. {item['title']}",
            f"   Task: {item['task_id']}",
            f"   State: {item['state']}",
            f"   Priority: {item['priority_score']}",
            f"   Why: {item['observation']}",
            f"   Next: {item['next_action']}",
        ])

    lines.append("")
    lines.append(
        "Completion requires trusted developer authorization "
        "and recorded validation evidence."
    )
    lines.append("Live broker execution remains unauthorized.")

    return "\n".join(lines)
