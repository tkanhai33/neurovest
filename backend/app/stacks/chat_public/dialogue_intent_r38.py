
"""Presentation preference guidance, not tool authorization."""
from __future__ import annotations
import re

MARKER = "NEUROVEST_DIALOGUE_INTENT_R38"

AVERSION = (
    r"\bcharts?\s+(?:confuse|confuses|overwhelm|overwhelms)\s+me\b",
    r"\b(?:confused|overwhelmed)\s+by\s+(?:the\s+)?charts?\b",
    r"\b(?:don't|do not)\s+(?:show|use|want)\s+(?:me\s+)?charts?\b",
    r"\bwithout\s+(?:any\s+)?charts?\b",
    r"\b(?:hate|avoid)\s+charts?\b",
)

GUIDED = (
    r"\bone\s+step\s+at\s+a\s+time\b",
    r"\bstep\s+by\s+step\b",
    r"\bstart\s+(?:with\s+)?(?:the\s+)?basics\b",
    r"\b(?:teach|walk)\s+me\s+through\b",
    r"\b(?:completely\s+)?new\s+to\s+investing\b",
    r"\b(?:i'm|i am)\s+(?:a\s+)?beginner\b",
    r"\bwithout\s+overwhelming\s+me\b",
    r"\b(?:keep|make)\s+it\s+simple\b",
    r"\bnormal\s+conversation\b",
    r"\bexplain\s+(?:it\s+)?simply\b",
)

DETAILED = (
    r"\b(?:in.depth|deep.dive|detailed)\s+(?:analysis|explanation)\b",
    r"\bexplain\s+in\s+detail\b",
    r"\bexplain\b.{0,100}\bin\s+detail\b",
    r"\bfull\s+(?:breakdown|analysis)\b",
    r"\btechnical\s+(?:details|explanation)\b",
)

def matches(patterns, text):
    return any(re.search(p, text, re.I) for p in patterns)

def classify_dialogue_preference(message, intent):
    if intent not in ("general_conversation", "trading_conversation"):
        return "default"
    if not isinstance(message, str) or not message.strip():
        return "default"
    if matches(AVERSION, message):
        return "chart_averse"
    if matches(DETAILED, message):
        return "detailed"
    if matches(GUIDED, message):
        return "guided"
    return "default"

def build_dialogue_guidance(message, intent):
    mode = classify_dialogue_preference(message, intent)

    if mode == "chart_averse":
        return (
            "\n\nUSER PRESENTATION PREFERENCE — CHART AVERSE:\n"
            "Respect the user's stated difficulty with charts. "
            "Do not suggest viewing or analyzing charts as the "
            "first step. Explain one foundational concept in "
            "plain language, then offer one manageable next step. "
            "Ask no more than one follow-up question. "
            "Avoid unnecessary product or ticker recommendations. "
            "Do not omit important risks or invent financial facts.\n"
        )

    if mode == "guided":
        return (
            "\n\nUSER PRESENTATION PREFERENCE — GUIDED:\n"
            "Respond as a patient conversational teacher. "
            "Answer the immediate question, introduce one or "
            "two concepts, and offer a useful next step. "
            "Prefer concise paragraphs over a long checklist. "
            "Do not immediately pitch brokers, ETFs or specific "
            "stocks when the user's goals are unknown. "
            "Ask one relevant question when helpful. "
            "Keep important risks and uncertainties intact.\n"
        )

    if mode == "detailed":
        return (
            "\n\nUSER PRESENTATION PREFERENCE — DETAILED:\n"
            "Give a substantive, structured explanation. "
            "Respect the requested depth while clearly "
            "separating evidence, assumptions and unknowns. "
            "Never fabricate numerical results or sources.\n"
        )

    return ""
