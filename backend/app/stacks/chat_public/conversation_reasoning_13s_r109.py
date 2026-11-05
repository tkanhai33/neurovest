"""
NeuroVest R109 — bounded conversational reasoning guidance.

Pre-generation context guidance for ordinary conversational
tasks. Does not grant permissions or execute tools.

Financial causation: distinguish measured changes from
documented causes, interpretations and hypotheses.

General conversation: prioritize the actual user request,
retain context, answer all requested parts, and avoid
fabricating tools, evidence, sources or completed actions.
"""

from __future__ import annotations

import re

# NEUROVEST_R109_CONVERSATIONAL_REASONING_ENGINE

MAX_MESSAGE = 6000
MAX_GUIDANCE = 2100

PROTECTED = re.compile(
    r"\b("
    r"emergency.stop|emergency stop|"
    r"execute (?:a )?(?:trade|order)|"
    r"place (?:a )?(?:trade|order)|"
    r"submit (?:a )?(?:trade|order)|"
    r"buy shares|sell shares|"
    r"enable live trading|"
    r"brokerage authorization|"
    r"change (?:my |user )?permissions|"
    r"change (?:my |user )?role|"
    r"developer authorization|"
    r"developer command|"
    r"what do you need to improve"
    r")\b",
    re.I,
)

WHY = re.compile(
    r"\b("
    r"why|because|caused|causes|drivers?|"
    r"reasons?|explain|what changed|"
    r"contributed|attributable|behind"
    r")\b",
    re.I,
)

FINANCIAL = re.compile(
    r"\b("
    r"revenue|earnings|income|margin|"
    r"profit|growth|cash flow|financial|"
    r"valuation|shares|stock|equity"
    r")\b",
    re.I,
)

COMPARISON = re.compile(
    r"\b("
    r"compare|compared|versus|vs\.?|"
    r"difference|increase|decrease|"
    r"higher|lower|previous|changed"
    r")\b",
    re.I,
)

MULTIPART = re.compile(
    r"\b("
    r"and also|as well as|in addition|"
    r"first.{0,100}then|both|"
    r"explain.{0,100}compare"
    r")\b",
    re.I | re.S,
)

FOLLOWUP = re.compile(
    r"\b("
    r"what about|how about|"
    r"and what|and why|"
    r"its|their|that result|"
    r"this result|previous answer"
    r")\b",
    re.I,
)

EVIDENCE_MARKERS = (
    "Resolved equity symbol:",
    "Financial reporting currency:",
    "R108 DETERMINISTIC ANNUAL FINANCIAL COMPARISON",
)


def build_guidance(message, model_context=""):
    if not isinstance(message, str):
        return ""

    message = message.strip()

    if (
        not message
        or len(message) > MAX_MESSAGE
        or PROTECTED.search(message)
    ):
        return ""

    if not isinstance(model_context, str):
        model_context = ""

    grounded_finance = (
        FINANCIAL.search(message) is not None
        and (
            "Resolved equity symbol:" in model_context
            and "Financial reporting currency:" in model_context
        )
    )

    parts = [
        "CONVERSATIONAL REASONING GUIDANCE:",
        "Answer the user's current question directly and naturally.",
        "Maintain continuity with relevant previous conversation,",
        "but do not assume missing details or invent prior turns.",
        "Distinguish established facts from inference, estimates,",
        "hypotheses and information that remains unknown.",
        "Never claim to have used a tool or source unless its",
        "results are actually present in the available context.",
        "Do not claim an action was completed unless it really was.",
        "Avoid unnecessary repetition, boilerplate or filler.",
        "This guidance does not override authorization, safety,",
        "tool permissions, system instructions or trading restrictions.",
    ]

    if MULTIPART.search(message) or message.count("?") >= 2:
        parts.extend([
            "MULTI-PART REQUEST:",
            "Address each separately requested component.",
            "Keep the response organized without becoming repetitive.",
            "If one component lacks evidence, answer supported parts",
            "and identify the missing evidence for the remainder.",
        ])

    if FOLLOWUP.search(message):
        parts.extend([
            "FOLLOW-UP CONTINUITY:",
            "Resolve references using the actual prior conversation.",
            "Avoid switching companies, dates or subjects silently.",
            "If the referent cannot be established, say so.",
        ])

    if COMPARISON.search(message):
        parts.extend([
            "COMPARISON DISCIPLINE:",
            "Compare like-for-like items, units and periods.",
            "Keep older and newer periods correctly identified.",
            "Use percentage points for changes between percentages.",
            "Avoid causal conclusions based on correlation alone.",
        ])

    if grounded_finance:
        parts.extend([
            "FINANCIAL EVIDENCE DISCIPLINE:",
            "Use the supplied provider observations and any",
            "deterministically calculated figures as the basis",
            "for numerical conclusions.",
            "Distinguish Yahoo Finance statement-column dates",
            "from independently verified official fiscal year ends.",
            "Do not invent SEC filings or official source links.",
            "Do not expose internal evidence identifiers.",
        ])

        if WHY.search(message):
            parts.extend([
                "FINANCIAL CAUSAL ATTRIBUTION:",
                "A revenue, profit or margin change establishes",
                "what changed, not necessarily why it changed.",
                "Only attribute a cause to a company when available",
                "evidence directly documents that explanation.",
                "Otherwise describe potential explanations as",
                "unverified possibilities, without implying",
                "that they were established for this company.",
                "If appropriate, identify which filings or",
                "management disclosures would verify the cause.",
            ])

    elif WHY.search(message):
        parts.extend([
            "EXPLANATION DISCIPLINE:",
            "Explain the mechanism when well established.",
            "Do not substitute a plausible story for evidence.",
            "Mark uncertainty where evidence is incomplete.",
        ])

    result = "\n".join(parts)

    if len(result) > MAX_GUIDANCE:
        return ""

    return result
