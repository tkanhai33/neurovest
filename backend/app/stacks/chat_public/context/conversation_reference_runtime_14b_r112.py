
"""R112-C6R: read-only chronological reference resolution."""
from __future__ import annotations
import re
from collections.abc import Mapping

def normalize(value):
    value = re.sub(r"^\s*\d+[.)]\s*", "", str(value))
    return " ".join(value.casefold().split()).strip(" ?.!")

def field(item, name):
    if isinstance(item, Mapping):
        return item.get(name)
    return getattr(item, name, None)

def classify(current):
    if not isinstance(current, str):
        return None
    q = normalize(current)

    if (
        re.search(r"\bwhat did i ask\b", q)
        and re.search(r"\b(?:immediately\s+)?before\b", q)
    ):
        return "before_anchor"

    if re.search(
        r"\b(before i asked|prior to asking)\b", q
    ) and re.search(r"\b(what|which)\b", q):
        return "before_meta"

    if re.search(
        r"\b(two questions ago|two questions back|"
        r"second previous question)\b", q
    ):
        return "two_back"

    if re.search(
        r"\b(what|which)\b", q
    ) and (
        re.search(
            r"\bmy\b.*\b(previous|last|prior)\b"
            r".*\b(question|subject|topic)\b", q
        )
        or re.search(
            r"\bwhat did i (just )?ask\b", q
        )
        or re.search(
            r"\bwhat was i just asking\b", q
        )
    ):
        return "previous"

    return None

def resolve_reference_answer(current, history):
    kind = classify(current)
    if kind is None or not isinstance(history, (list, tuple)):
        return None

    turns = []
    for item in history[-96:]:
        role = field(item, "role")
        if hasattr(role, "value"):
            role = role.value
        if str(role).casefold() not in ("user", "human"):
            continue
        content = field(item, "content")
        if isinstance(content, str) and content.strip():
            turns.append(" ".join(content.split()))

    # Current message may have been saved before context loading.
    while turns and normalize(turns[-1]) == normalize(current):
        turns.pop()

    if not turns:
        return None

    if kind == "before_anchor":
        match = re.search(
            r"\bwhat did i ask\b.{0,80}?\b(?:immediately\s+)?before\b(?P<anchor>.+)$",
            normalize(current),
        )
        if not match:
            return None

        stop_words = {
            "the", "a", "an", "what", "did", "i", "ask",
            "immediately", "before", "after", "question",
            "prompt", "message", "conversation", "right",
        }
        anchor_terms = (
            set(re.findall(r"[a-z0-9]+", match["anchor"]))
            - stop_words
        )
        if not anchor_terms:
            return None

        candidates = []
        for index, turn in enumerate(turns):
            turn_terms = set(re.findall(r"[a-z0-9]+", normalize(turn)))
            overlap = len(anchor_terms & turn_terms)
            if overlap:
                candidates.append((overlap, index))

        if not candidates:
            return None

        best_score = max(score for score, _ in candidates)
        anchor_index = min(
            index for score, index in candidates if score == best_score
        )
        if anchor_index == 0:
            return None
        target = turns[anchor_index - 1]

    elif kind == "previous":
        target = turns[-1]
    elif kind == "two_back":
        if len(turns) < 2:
            return None
        target = turns[-2]
    else:
        anchor = None
        for i in range(len(turns) - 1, -1, -1):
            t = normalize(turns[i])
            if (
                "previous question" in t
                or "previous subject" in t
                or "last question" in t
                or "before that" in t
            ):
                anchor = i
                break
        if anchor is None or anchor == 0:
            return None
        target = turns[anchor - 1]

    if not target or len(target) > 700:
        return None
    if normalize(target) == normalize(current):
        return None

    if kind == "before_anchor":
        return (
            "The question immediately before the referenced question was: "
            + "“" + target + "”"
        )

    return "Your earlier question was: “" + target + "”"
