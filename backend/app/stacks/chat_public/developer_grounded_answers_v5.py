"""Read-only, fingerprint-verified developer source answers.

Caller must perform developer authorization and thread
ownership checks before using this module. This module
does not grant permissions or execute repository code.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import re

SCHEMA = "neurovest_v5_ast_evidence_candidate_v1"

ALIASES = {
    "chat": ("chat", "conversation", "response", "runtime"),
    "routing": ("routing", "route", "router", "intent"),
    "memory": ("memory", "history", "context", "conversation"),
    "strategy": ("strategy", "candidate", "training"),
    "execution": ("execution", "paper", "broker", "order"),
    "risk": ("risk", "drawdown", "guard"),
    "portfolio": ("portfolio", "accounting", "reconciliation"),
    "market": ("market", "feed", "provider", "bars"),
    "authentication": ("identity", "auth", "session", "token"),
}

STOPWORDS = {
    "what", "which", "where", "when", "does", "this",
    "that", "with", "from", "your", "neuro", "neurovest",
    "explain", "inspect", "review", "please", "show",
    "how", "why", "would", "should", "could", "functions",
    "function", "work", "working", "code", "our",
}


class EvidenceUnavailable(RuntimeError):
    pass


def _terms(question):
    words = set(re.findall(
        r"[a-z_][a-z_0-9]{2,}",
        question.casefold(),
    ))
    terms = words - STOPWORDS

    for key, expansions in ALIASES.items():
        if key in words:
            terms.update(expansions)

    return terms


def load_verified_index(root, index_path):
    root = Path(root).resolve()
    index_path = Path(index_path).resolve()

    if (
        not index_path.is_file()
        or index_path.is_symlink()
        or not index_path.is_relative_to(root)
    ):
        raise EvidenceUnavailable("Evidence index unavailable")

    try:
        data = json.loads(index_path.read_text("utf-8"))
    except (OSError, ValueError) as exc:
        raise EvidenceUnavailable("Invalid evidence index") from exc

    if (
        data.get("schema") != SCHEMA
        or data.get("status") != "CANDIDATE_ONLY"
        or not isinstance(data.get("sources"), dict)
        or not data["sources"]
    ):
        raise EvidenceUnavailable("Evidence schema rejected")

    for relative, record in data["sources"].items():
        if (
            not isinstance(relative, str)
            or not isinstance(record, dict)
            or not isinstance(record.get("sha256"), str)
        ):
            raise EvidenceUnavailable("Invalid source record")

        source = root / relative

        if (
            source.is_symlink()
            or not source.is_file()
            or not source.resolve().is_relative_to(root)
        ):
            raise EvidenceUnavailable("Indexed source unavailable")

        actual = hashlib.sha256(source.read_bytes()).hexdigest()

        if actual != record["sha256"]:
            raise EvidenceUnavailable(
                "Indexed source changed; rebuild required"
            )

    return data


def search_definitions(index, question, *, limit=8):
    if not isinstance(question, str) or len(question) > 2000:
        return []

    terms = _terms(question)
    if not terms:
        return []

    results = []

    for relative, record in index["sources"].items():
        path = relative.casefold()

        for definition in record.get("definitions", []):
            name = str(definition.get("name", ""))
            normalized = name.casefold()
            calls = definition.get("syntactic_calls", [])

            name_score = sum(
                8 for term in terms if term in normalized
            )
            path_score = sum(
                3 for term in terms if term in path
            )
            call_score = sum(
                1 for term in terms
                if any(term in str(call).casefold() for call in calls)
            )

            score = name_score + path_score + min(call_score, 5)

            # Specific symbol matches outrank generic path matches.
            # Match complete underscore-delimited name tokens.
            import re as _re
            query_words = set(
                _re.findall(r"[a-z0-9]+", question.casefold())
            ) - STOPWORDS

            name_words = set(
                _re.findall(r"[a-z0-9]+", normalized)
            )

            overlap = len(query_words & name_words)
            score += overlap * 12

            if overlap >= 2:
                score += overlap * overlap * 8

            # Entry-point preference is only for broad questions,
            # never requests naming a specific implementation.
            broad_runtime = (
                "chat" in query_words
                and "runtime" in query_words
                and len(query_words) <= 3
            )

            if broad_runtime:
                if name == "run_chat_turn":
                    score += 45
                elif name == "handle_chat_message":
                    score += 30

            # A highly specific match should remain relevant
            # even when a generic function shares the file.

            if score <= 0:
                continue

            results.append({
                "file": relative,
                "name": name,
                "line": definition.get("line"),
                "kind": definition.get("kind"),
                "score": score,
                "syntactic_calls": calls[:12],
            })

    results.sort(
        key=lambda item: (
            -item["score"],
            item["file"],
            item["line"] or 0,
        )
    )

    return results[:max(1, min(int(limit), 20))]


def _nv_explain_verified_fallback(question, matches):
    """Conservative interpretation of verified definitions."""
    if not matches:
        return ""

    lower = str(question or "").casefold()

    improvement = any(term in lower for term in (
        "improve", "improvement", "priority",
        "priorities", "weakness", "limitation",
        "upgrade", "what do you need",
    ))

    architecture = any(term in lower for term in (
        "architecture", "routing", "implementation",
        "dependency", "component", "how does",
        "how do",
    ))

    lines = [
        "",
        "",
        "## What the verified evidence establishes",
        "",
    ]

    for item in matches[:5]:
        location = f"{item['file']}:{item['line']}"
        name = str(item["name"])
        kind = str(item["kind"])

        label = {
            "async_function": "asynchronous function",
            "function": "function",
            "class": "class",
        }.get(kind, "definition")

        lines.append(
            f"- `{name}` at `{location}` is a verified "
            f"{label} definition. Its execution behavior "
            "is not verified by this reference alone."
        )

    if improvement:
        lines.extend([
            "",
            "## Evidence-driven improvement investigation",
            "",
            "These source definitions identify where to "
            "investigate, but they do not establish "
            "the system's largest operational weakness.",
            "",
            "The next useful step is to compare controlled "
            "runtime observations against a baseline: "
            "answer correctness, citation accuracy, "
            "context retention, latency and failure rates.",
            "",
            "Use the observed gaps to prioritize changes, "
            "then verify improvements with regression tests. "
            "These are proposed actions, not completed work.",
        ])

    elif architecture:
        lines.extend([
            "",
            "## Architectural interpretation",
            "",
            "The indexed definitions indicate implementation "
            "locations worth investigating. Actual execution "
            "order, component relationships and authorization "
            "outcomes require runtime or contract evidence.",
        ])

    else:
        lines.extend([
            "",
            "These references establish source locations. "
            "Behavioral conclusions require additional "
            "verified evidence.",
        ])

    return "\n".join(lines)

def answer_developer_question(
    *, root, index_path, question, authorized=False,
):
    if authorized is not True:
        raise PermissionError(
            "Authenticated developer access required"
        )

    index = load_verified_index(root, index_path)
    matches = search_definitions(index, question)

    if not matches:
        return (
            "No directly relevant source definitions were "
            "identified in the current bounded evidence index. "
            "This does not prove the capability is absent."
        )

    lines = [
        "## Verified developer source references",
        "",
        f"Question: {question.strip()[:300]}",
        "",
    ]

    for item in matches:
        lines.append(
            f"- `{item['name']}` "
            f"({item['kind']}) — "
            f"`{item['file']}:{item['line']}`"
        )

    lines.extend([
        "",
        "These references are backed by current SHA-256 "
        "source fingerprints.",
        "Call names are syntactic observations, not verified "
        "runtime call relationships.",
        "No bug, execution outcome, or successful test "
        "is established by this source search.",
    ])

    return "\n".join(lines) + _nv_explain_verified_fallback(question, matches)
