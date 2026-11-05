from __future__ import annotations

import ast
import logging
import re
from dataclasses import dataclass
from pathlib import Path

LOG = logging.getLogger(
    "neurovest.developer_intelligence"
)

ROOT = Path(__file__).resolve().parents[4]
CHAT = ROOT / "backend/app/stacks/chat_public"

VERSION = "NEUROVEST_DEVELOPER_INTELLIGENCE_3E"

IMPROVEMENT_INTENT = re.compile(
    r"\bwhat\s+are\s+your\s+(?:current\s+)?operational\s+and\s+conversational\s+weaknesses\b|"
    r"\bwhat\s+are\s+your\s+(?:current\s+)?weaknesses\b|"
    r"\b("
    r"what\s+do\s+you\s+need\s+to\s+improve|"
    r"what\s+should\s+you\s+improve|"
    r"assess\s+your\s+(?:own\s+)?capabilities|"
    r"assess\s+your\s+(?:own\s+)?intelligence|"
    r"review\s+your\s+(?:own\s+)?weaknesses|"
    r"identify\s+your\s+(?:own\s+)?weaknesses|"
    r"how\s+can\s+you\s+improve\s+yourself|"
    r"review\s+your\s+(?:own\s+)?qualification\s+gaps"
    r")\b",
    re.IGNORECASE,
)

MODULES = {
    "natural_language_research":
        "natural_research_orchestrator.py",
    "model_tool_planner":
        "model_tool_router_3b.py",
    "general_response_guidance":
        "conversation_quality_3c.py",
    "generation_completion_guard":
        "ollama_completion_guard_3dr1.py",
    "general_answer_relevance_guard":
        "answer_relevance_3dr2.py",
    "financial_research_bridge":
        "financial_analysis_chat_bridge.py",
    "chat_runtime":
        "chat_runtime.py",
    "ollama_adapter":
        "ollama_chat_client.py",
}

RELEASE_PREFIXES = (
    "neuro_natural_chat_3A_",
    "neuro_intelligence_3B_",
    "neuro_intelligence_3C_",
    "neuro_completion_3DR1_",
    "neuro_relevance_3DR2_",
)

TOKEN_RE = re.compile(r"[a-z0-9]+")
STOP = {
    "the", "and", "that", "this", "with", "from",
    "into", "how", "what", "when", "where",
    "which", "explain", "please", "about",
    "neuro", "like", "beginner", "does",
    "works", "work", "your", "would",
    "could", "their", "there",
}


@dataclass(frozen=True)
class EvidenceInspection:
    applicable: bool
    status: str
    matched_terms: tuple[str, ...]
    question_terms: tuple[str, ...]


def is_improvement_request(message):
    return bool(
        isinstance(message, str)
        and len(message) <= 1500
        and IMPROVEMENT_INTENT.search(message)
    )


def _tokens(text):
    return {
        x for x in TOKEN_RE.findall(text.lower())
        if len(x) >= 4 and x not in STOP
    }


def inspect_retrieval(question, evidence):
    """
    Metadata-only relevance inspection.

    This does not claim that lexical overlap proves
    semantic or factual correctness. It also does
    not authorize tools or modify research evidence.
    """
    if (
        not isinstance(question, str)
        or not isinstance(evidence, str)
        or not evidence.strip()
    ):
        return EvidenceInspection(
            False, "no_evidence", (), ()
        )

    if len(question) > 2000:
        return EvidenceInspection(
            False, "question_out_of_scope", (), ()
        )

    q = _tokens(question)
    e = _tokens(evidence[:20000])

    matched = tuple(sorted(q & e))

    if not q:
        status = "insufficient_question_terms"
    elif matched:
        status = "lexical_overlap_not_verified_relevance"
    else:
        status = "no_lexical_overlap_review_required"

    return EvidenceInspection(
        True,
        status,
        matched[:12],
        tuple(sorted(q))[:12],
    )


def _module_inventory():
    inventory = {}

    for capability, filename in MODULES.items():
        path = CHAT / filename

        if not path.is_file():
            inventory[capability] = "absent"
            continue

        try:
            ast.parse(path.read_text())
            inventory[capability] = "source_present_parse_ok"
        except (SyntaxError, OSError, UnicodeError):
            inventory[capability] = "source_unreadable_or_invalid"

    return inventory


def _release_inventory():
    releases = ROOT / "runtime/releases"

    output = []

    if not releases.is_dir():
        return output

    for prefix in RELEASE_PREFIXES:
        candidates = sorted(
            (
                p for p in releases.iterdir()
                if p.is_dir()
                and p.name.startswith(prefix)
                and p.is_relative_to(releases)
            ),
            key=lambda p: p.name,
        )

        if not candidates:
            output.append(
                (prefix.rstrip("_"), "no_local_release")
            )
            continue

        latest = candidates[-1]
        log = latest / "evidence/tests.log"
        install_log = latest / "evidence/install.log"

        status = "release_directory_present"

        # Only inspect bounded local qualification logs.
        # Never include log text in the chat response.
        if log.is_file() and log.stat().st_size <= 200000:
            text = log.read_text(errors="replace")
            if "TEST_RESULT=PASS" in text:
                status = "focused_tests_passed"
            elif "TEST_RESULT=FAIL" in text:
                status = "focused_tests_failed"

        elif (
            install_log.is_file()
            and install_log.stat().st_size <= 200000
        ):
            text = install_log.read_text(errors="replace")
            if "INSTALL_RESULT=PASS" in text:
                status = "installation_reported_pass"

        output.append((prefix.rstrip("_"), status))

    return output


def build_developer_assessment():
    # NEUROVEST_DIAGNOSTICS_3F
    # Existing authenticated chat routing and authorization
    # remain authoritative. This changes report content only.
    from backend.app.stacks.chat_public.developer_diagnostics_3f import (
        build_report,
    )
    return build_report()


def safe_developer_reply(*, authorized, message):
    if not is_improvement_request(message):
        return None

    if authorized is not True:
        return None

    return build_developer_assessment()
