"""R50: bounded, opt-in Ollama response completion.

This component does not authorize requests, select tools,
read private accounts, access a broker, or change the chat runtime.
Callers must apply their existing authorization, safety,
citation, and final verification gates to the combined answer.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Callable
import re

VERSION = "G43-R50"

@dataclass(frozen=True)
class CompletionResult:
    answer: str
    completed: bool
    rounds: int
    reasons: tuple[str, ...]
    stop_reason: str

    def as_dict(self):
        return asdict(self)


def _reason(response):
    if not isinstance(response, dict):
        return "invalid_response"
    reason = response.get("done_reason")
    if isinstance(reason, str) and reason.strip():
        return reason.strip().lower()
    if response.get("done") is True:
        return "done_unknown_reason"
    return "not_done"


def _merge(existing, extension):
    """Join continuations without duplicating shared text."""
    existing = existing.rstrip()
    extension = extension.lstrip()

    if not extension:
        return existing

    if existing.endswith(extension):
        return existing

    max_overlap = min(len(existing), len(extension), 500)
    for n in range(max_overlap, 23, -1):
        if existing[-n:] == extension[:n]:
            return existing + extension[n:]

    separator = "" if (
        existing.endswith((" ", "\n", "-", "("))
        or extension.startswith((".", ",", ";", ":", ")"))
    ) else " "

    return existing + separator + extension


def complete(
    question: str,
    model: str,
    generate: Callable,
    *,
    enabled: bool = False,
    first_tokens: int = 650,
    continuation_tokens: int = 650,
    max_continuations: int = 2,
):
    if not isinstance(question, str) or not question.strip():
        raise ValueError("A question is required")

    if not isinstance(model, str) or not model.strip():
        raise ValueError("A model is required")

    if not callable(generate):
        raise TypeError("generate must be callable")

    max_continuations = min(
        max(int(max_continuations), 0), 2
    )
    first_tokens = min(max(int(first_tokens), 64), 2048)
    continuation_tokens = min(
        max(int(continuation_tokens), 64), 2048
    )

    # The caller supplies the actual approved inference
    # transport. R50 itself does not connect to a broker
    # or perform retrieval.
    first = generate(model, question, first_tokens)
    text = str(first.get("response") or "").strip()
    reasons = [_reason(first)]

    if not text:
        return CompletionResult(
            "", False, 0, tuple(reasons), "empty_response"
        )

    if reasons[-1] == "stop":
        return CompletionResult(
            text, True, 0, tuple(reasons), "natural_stop"
        )

    if not enabled or reasons[-1] != "length":
        return CompletionResult(
            text, False, 0, tuple(reasons),
            "disabled_or_unconfirmed_completion",
        )

    for round_number in range(1, max_continuations + 1):
        # Supply only the original public question and
        # previously generated answer. The caller must
        # ensure the request is eligible for continuation.
        prompt = (
            "Continue the following assistant answer exactly "
            "where it stopped. Do not repeat earlier material. "
            "Do not start a new answer, invent evidence, or "
            "change the question. Complete unfinished sentences "
            "and sections naturally.\n\n"
            "QUESTION:\n" + question[:4000] + "\n\n"
            "ANSWER SO FAR:\n" + text[-6000:] + "\n\n"
            "CONTINUATION ONLY:\n"
        )

        next_response = generate(
            model, prompt, continuation_tokens
        )

        addition = str(
            next_response.get("response") or ""
        ).strip()

        reason = _reason(next_response)
        reasons.append(reason)

        if not addition:
            return CompletionResult(
                text, False, round_number,
                tuple(reasons), "empty_continuation",
            )

        merged = _merge(text, addition)

        if merged == text:
            return CompletionResult(
                text, False, round_number,
                tuple(reasons), "no_new_content",
            )

        text = merged

        if reason == "stop":
            return CompletionResult(
                text, True, round_number,
                tuple(reasons), "natural_stop",
            )

        if reason != "length":
            return CompletionResult(
                text, False, round_number,
                tuple(reasons), "unconfirmed_stop",
            )

    return CompletionResult(
        text, False, max_continuations,
        tuple(reasons), "continuation_budget_exhausted",
    )
