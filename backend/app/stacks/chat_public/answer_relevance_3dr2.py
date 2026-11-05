from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass

LOGGER = logging.getLogger("neurovest.answer_relevance")

# Conservative checks for demonstrable topic drift.
# This is not a universal semantic evaluator.

STOP = {
    "a", "an", "the", "to", "me", "my", "you",
    "your", "of", "for", "and", "or", "is",
    "are", "was", "were", "how", "what",
    "why", "does", "do", "can", "could",
    "would", "please", "neuro", "like",
    "im", "i", "beginner", "explain",
    "tell", "about", "works", "work",
    "from", "with", "into", "then",
}

GENERAL_EXPLANATION = re.compile(
    r"\b(explain|what is|what are|how does|"
    r"how do|teach me|describe)\b",
    re.IGNORECASE,
)

FINANCIAL = re.compile(
    r"\b(stocks?|etfs?|portfolio|brokerage|"
    r"financial|trading|investments?|"
    r"bullish|bearish|buy|sell|"
    r"research universe|market analysis)\b",
    re.IGNORECASE,
)

CODE = re.compile(
    r"\b(python|javascript|typescript|"
    r"debug|code|script|function|"
    r"traceback|programming|redis|postgres(?:ql)?|sql|"
    r"databases?|cach(?:e|ing)|fastapi|https?|apis?|"
    r"idempotency|rate[ -]?limiting|type[ -]?checking|"
    r"transactions?|asyncio|concurrency)\b",
    re.IGNORECASE,
)

WORDS = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class Assessment:
    checked: bool
    relevant: bool
    reason: str


def terms(text):
    return {
        word for word in WORDS.findall(text.lower())
        if len(word) > 2 and word not in STOP
    }


def eligible(question):
    if not isinstance(question, str):
        return False
    if not 10 <= len(question) <= 400:
        return False
    if question.lstrip().startswith("/"):
        return False
    if not GENERAL_EXPLANATION.search(question):
        return False
    if FINANCIAL.search(question) or CODE.search(question):
        return False
    return True


def assess(question, answer):
    if not eligible(question):
        return Assessment(False, True, "outside_scope")

    if not isinstance(answer, str) or not answer.strip():
        return Assessment(True, False, "empty_answer")

    keywords = terms(question)

    if not keywords:
        return Assessment(False, True, "no_topic_terms")

    response_terms = terms(answer)

    overlap = keywords & response_terms

    # Explicit known regression: conventional manual
    # transmission explanations must not be replaced
    # entirely with automated-manual/AMT explanations.
    question_low = question.lower()
    answer_low = answer.lower()

    conventional_manual = (
        "manual transmission" in question_low
        and any(
            item in question_low
            for item in (
                "clutch engagement",
                "gear changes",
                "gear shifting",
                "clutch pedal",
            )
        )
    )

    if conventional_manual:
        if (
            "automated manual transmission" in answer_low
            or "automatic actuation" in answer_low
        ) and not any(
            item in answer_low
            for item in (
                "clutch pedal",
                "release bearing",
                "synchronizer",
                "synchromesh",
                "input shaft",
            )
        ):
            return Assessment(
                True, False,
                "automated_transmission_topic_drift",
            )

    # Named technical concepts require identifiable
    # topic continuity in the answer.
    if not overlap:
        return Assessment(
            True, False, "no_subject_overlap",
        )

    return Assessment(True, True, "subject_present")


async def _g41_original_verify_and_repair(
    *,
    question,
    answer,
    model_call=None,
):
    first = assess(question, answer)

    if not first.checked or first.relevant:
        return answer, "unchanged"

    LOGGER.warning(
        "neuro_relevance_rejected reason=%s",
        first.reason,
    )

    if model_call is None:
        return (
            "I couldn't produce a reliable answer to "
            "that question. Please try asking again.",
            "blocked",
        )

    try:
        replacement = await asyncio.wait_for(
            asyncio.to_thread(model_call, question),
            timeout=12,
        )
    except Exception as exc:
        LOGGER.warning(
            "neuro_relevance_retry_failed error_type=%s",
            type(exc).__name__,
        )
        replacement = None

    second = assess(question, replacement)

    if (
        isinstance(replacement, str)
        and replacement.strip()
        and second.relevant
    ):
        LOGGER.info(
            "neuro_relevance_retry_accepted"
        )
        return replacement.strip(), "regenerated"

    LOGGER.warning(
        "neuro_relevance_retry_rejected reason=%s",
        second.reason,
    )

    return (
        "I couldn't verify that my response actually "
        "addressed your question. Please try again.",
        "blocked",
    )



# G41_RELEVANCE_SEMANTIC_REPAIR
# Preserve final deterministic math, citation and safety verification.
# This module only assesses topical relevance.

_G41_FAILURE_PHRASES = (
    "i couldn't verify that my response",
    "i couldn't produce a reliable answer",
    "neuro local model is unavailable",
    "internal server error",
    "wikipedia summary could not be retrieved",
    "financial research request",
    "universe command unavailable",
)

_G41_CONCEPTS = (
    (
        r"\b(?:percentage|percent|percentages)\b",
        r"\b(?:percent|percentage|%|fraction|decimal)\b",
    ),
    (
        r"\b(?:probability|odds|chance)\b",
        r"\b(?:probability|chance|likelihood|odds)\b",
    ),
    (
        r"\b(?:maximum drawdown|drawdown)\b",
        r"\b(?:peak.to.trough|largest decline|maximum loss"
        r"|drawdown|portfolio decline)\b",
    ),
    (
        r"\b(?:look.ahead bias|backtest bias)\b",
        r"\b(?:future information|future data|information leakage"
        r"|unavailable at the time|look.ahead)\b",
    ),
    (
        r"\b(?:peer review|peer.reviewed)\b",
        r"\b(?:reviewers?|scientific scrutiny|expert evaluation"
        r"|referees?|manuscript evaluation)\b",
    ),
    (
        r"\b(?:tcp|udp)\b",
        r"\b(?:transmission control protocol|user datagram protocol"
        r"|tcp|udp)\b",
    ),
    (
        r"\b(?:http|https|tls)\b",
        r"\b(?:hypertext transfer|transport layer security"
        r"|http|https|tls)\b",
    ),
)

def _g41_has_failure_message(answer):
    lowered = str(answer or "").casefold()
    return any(
        phrase in lowered
        for phrase in _G41_FAILURE_PHRASES
    )

def _g41_relevance_recovery(question, answer, assessment):
    """Conservatively recognize specific lexical false negatives."""
    if getattr(assessment, "reason", None) != "no_subject_overlap":
        return False

    if not isinstance(answer, str) or not answer.strip():
        return False

    if _g41_has_failure_message(answer):
        return False

    question = str(question or "")
    answer = answer.strip()

    # Numerical answers frequently paraphrase a calculation
    # without repeating the question's vocabulary.
    #
    # Preserve only when the answer has numerical content.
    # Correctness is checked independently downstream.
    numeric_question = bool(re.search(
        r"\b(?:percent|percentage|calculate|compute|evaluate"
        r"|probability|how much|what is \d+|to the \d+"
        r"|square root)\b|%",
        question,
        re.I,
    ))

    numeric_answer = bool(re.search(
        r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?%?",
        answer,
    ))

    if numeric_question and numeric_answer:
        return True

    # Concept matching requires both a concept in the
    # question and its recognized explanatory vocabulary
    # in the answer. No generic length-only bypass.
    # G41_SHORT_DRAWDOWN_PARAPHRASE_RECOVERY
    # Recognize concise, substantive definitions without needing
    # an arbitrary 70-character minimum.
    if (
        re.search(r"\bdrawdown\b", question, re.I)
        and re.search(
            r"\b(?:peak.to.trough|largest peak|highest peak)\b",
            answer, re.I
        )
        and re.search(
            r"\b(?:portfolio|equity|investment|strategy|"
            r"decline|fall|loss)\b",
            answer, re.I
        )
    ):
        return True

    if len(answer) >= 70:
        for question_pattern, answer_pattern in _G41_CONCEPTS:
            if (
                re.search(question_pattern, question, re.I)
                and re.search(answer_pattern, answer, re.I)
            ):
                return True

    return False


async def verify_and_repair(*, question, answer, model_call=None):
    """G41 relevance-only wrapper. Final response guards stay active."""
    if _g41_clear_cross_topic_mismatch(question, answer):
        return await _g41_handle_cross_topic_mismatch(
            question, model_call
        )

    assessment = assess(question, answer)

    if (
        not getattr(assessment, "checked", False)
        or getattr(assessment, "relevant", False)
    ):
        return answer, "unchanged"

    if _g41_relevance_recovery(question, answer, assessment):
        return answer, "unchanged"

    # Genuine suspected off-topic answers retain the existing
    # regeneration / block behavior, now bounded to 12 seconds.
    return await _g41_original_verify_and_repair(
        question=question,
        answer=answer,
        model_call=model_call,
    )



def clean_general_reply(question):
    """
    Regenerate without retrieval excerpts or stale
    conversation documents when a clear mismatch
    has already been detected.

    Uses Neuro's existing local Ollama adapter.
    """
    from backend.app.stacks.chat_public.ollama_chat_client import (
        ask_ollama,
    )

    context = (
        "You are Neuro, a general-purpose assistant. "
        "Answer the current question directly, in your "
        "own words, without unrelated encyclopedia "
        "excerpts. Start with the subject the user asked "
        "about. Explain clearly at the requested level. "
        "Avoid unverified tool or research claims. "
        "Finish with a complete sentence. "
        "This request is an explanation only. "
        "No brokerage or system actions are authorized."
    )

    return ask_ollama(
        question,
        intent="general_conversation",
        context=context,
        model="neuro-reason:latest",
    )



# G41_CROSS_TOPIC_MISMATCH_GUARD
# Conservative mismatch classification. This is not a substitute
# for evidence verification, mathematical truth, or safety checks.

_G41_TOPICS = {
    "finance": re.compile(
        r"\b(?:drawdown|backtest(?:ing)?|look.ahead bias|"
        r"portfolio risk|sharpe ratio|volatility)\b", re.I
    ),
    "network": re.compile(
        r"\b(?:tcp|udp|http|https|tls|dns|network protocols?)\b",
        re.I,
    ),
    "programming": re.compile(
        r"\b(?:python code|javascript code|debug(?:ging)?|"
        r"stack trace|programming language)\b", re.I
    ),
}

_G41_FOREIGN_TOPICS = {
    "cooking": re.compile(
        r"\b(?:pasta|tomato sauce|boiling water|"
        r"recipe|garlic bread|baking cookies)\b", re.I
    ),
    "geography": re.compile(
        r"\b(?:capital of france|eiffel tower|"
        r"city of paris|mount everest)\b", re.I
    ),
    "gardening": re.compile(
        r"\b(?:planting roses|watering flowers|"
        r"garden soil|growing tomatoes)\b", re.I
    ),
}

def _g41_clear_cross_topic_mismatch(question, answer):
    question = str(question or "")
    answer = str(answer or "")

    if not question.strip() or not answer.strip():
        return False

    if _g41_has_failure_message(answer):
        return False

    # Only classify questions with an explicit, known topic.
    source_topics = {
        name for name, pattern in _G41_TOPICS.items()
        if pattern.search(question)
    }
    if not source_topics:
        return False

    # Preserve answers that substantively reference the asked topic.
    if any(
        _G41_TOPICS[name].search(answer)
        for name in source_topics
    ):
        return False

    # Also preserve recognized conceptual paraphrases.
    for question_pattern, answer_pattern in _G41_CONCEPTS:
        if (
            re.search(question_pattern, question, re.I)
            and re.search(answer_pattern, answer, re.I)
        ):
            return False

    # A mismatched answer must clearly concern an unrelated domain.
    unrelated = {
        name for name, pattern in _G41_FOREIGN_TOPICS.items()
        if pattern.search(answer)
    }

    return bool(unrelated)


async def _g41_handle_cross_topic_mismatch(question, model_call):
    # This rejection occurs before accepting the original assessment.
    # Optionally attempt one bounded relevance-only repair.
    if callable(model_call):
        try:
            candidate = await asyncio.wait_for(
                asyncio.to_thread(model_call, question),
                timeout=12,
            )
            if (
                isinstance(candidate, str)
                and candidate.strip()
                and not _g41_has_failure_message(candidate)
                and not _g41_clear_cross_topic_mismatch(
                    question, candidate
                )
            ):
                candidate_assessment = assess(question, candidate)
                if (
                    not getattr(candidate_assessment, "checked", False)
                    or getattr(candidate_assessment, "relevant", False)
                    or _g41_relevance_recovery(
                        question, candidate, candidate_assessment
                    )
                ):
                    return candidate, "repaired"
        except Exception:
            pass

    return (
        "I couldn't produce a relevant answer to that question. "
        "Please try rephrasing the request.",
        "relevance_blocked",
    )
