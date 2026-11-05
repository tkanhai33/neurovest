"""V101: bounded, thread-local history ranking.

This module accepts already-authorized messages only.
It performs no database access, cross-thread queries, or model inference.
"""
from __future__ import annotations

import re
from typing import Any

STOP = frozenset("""
a an and are as at back be been but by can could did do does
for from had has have how i in is it me my of on or our
please that the them there these they this those to was we
were what when where which who why will with would you your
earlier previous discussed discussion about again returning
""".split())


def tokens(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", text.casefold())
    normalized = set()
    for word in words:
        if word.endswith("ies") and len(word) > 5:
            word = word[:-3] + "y"
        elif word.endswith("s") and len(word) > 5 and not word.endswith("ss"):
            word = word[:-1]
        if len(word) > 2 and word not in STOP:
            normalized.add(word)
    return normalized


def select_relevant_history(
    messages: list[Any],
    question: str,
    *,
    recent_count: int = 6,
    older_count: int = 6,
    character_budget: int = 4200,
) -> list[Any]:
    """Select older matching turns plus recent history.

    Return original objects in original order. No facts are synthesized.
    """
    if character_budget < 256:
        raise ValueError("character_budget too small")

    if not messages:
        return []

    recent_start = max(0, len(messages) - recent_count)
    selected = set(range(recent_start, len(messages)))
    query = tokens(question)

    # Reference-only follow-ups refer to immediate dialogue,
    # not to arbitrary older messages sharing words such as
    # "second" or "one". Keep explicitly topical historical
    # questions eligible for normal retrieval.
    reference_only = bool(re.fullmatch(
        r"\s*(?:(?:and|but|so)\s+)?"
        r"(?:(?:what|how)\s+about\s+)?"
        r"(?:the\s+)?"
        r"(?:first|second|third|fourth|last|next|other|"
        r"previous|same|that|this)"
        r"(?:\s+one)?"
        r"\s*[?!.]*\s*",
        question,
        flags=re.IGNORECASE,
    ))

    if reference_only:
        return [
            messages[i]
            for i in sorted(selected)
        ]


    ranked = []
    for i in range(recent_start):
        item = messages[i]
        content = str(getattr(item, "content", "") or "")
        role = str(getattr(item, "role", "") or "").lower()
        overlap = query & tokens(content)

        if not overlap:
            continue

        # Older user statements take priority over assistant assertions.
        score = len(overlap) * 10
        if role == "user":
            score += 3
        score += i / max(1, len(messages))
        ranked.append((score, i))

    ranked.sort(reverse=True)

    chosen_older = set()
    for _, i in ranked:
        if len(chosen_older) >= older_count:
            break

        # Include a neighboring reply when room permits.
        for j in (i, i + 1):
            if j < recent_start and len(chosen_older) < older_count:
                chosen_older.add(j)

    selected.update(chosen_older)

    # Allocate space to newest messages first, then relevant older
    # messages. Never silently cut a selected message here.
    order = list(range(recent_start, len(messages) - 1))[::-1]
    if messages:
        order = list(range(len(messages) - 1, recent_start - 1, -1))
    order += sorted(chosen_older, reverse=True)

    retained = set()
    used = 0

    for i in order:
        item = messages[i]
        content = str(getattr(item, "content", "") or "")
        cost = len(content) + 20
        if used + cost <= character_budget:
            retained.add(i)
            used += cost

    return [messages[i] for i in sorted(retained)]
