
"""R113-B: current-date awareness and evidence calibration.

This module has no network, database, tool, or broker access.
It does not assert any current external fact.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

VERSION = "NEUROVEST_R113B_TEMPORAL_GROUNDING_V1"

CURRENT_PATTERNS = (
    r"\b(current|currently|today|tonight|right now|"
    r"as of now|at present|latest|recent|recently|"
    r"this week|this month|this year|now)\b",
    r"\b(who is|who's|is .* still|has .* changed)\b",
    r"\b(live price|stock price|market price|"
    r"breaking news|in office|president|prime minister|"
    r"ceo|governor|election results)\b",
)

CHANGING_TOPICS = (
    r"\b(president|prime minister|leader|minister|"
    r"governor|mayor|administration|officeholder|"
    r"politic|government|election|war|conflict|"
    r"sanction|ceasefire|invasion)\b",
    r"\b(stock|market|share price|quote|earnings|"
    r"interest rate|exchange rate|inflation|"
    r"bond yield|crypto|revenue|valuation)\b",
    r"\b(version|release|update|software|"
    r"regulation|law|rule|availability|"
    r"weather|forecast|schedule|sports|score)\b",
)

def requires_current_evidence(question):
    if not isinstance(question, str):
        return False
    q = question.casefold()
    if any(re.search(p, q) for p in CURRENT_PATTERNS):
        return True
    return False

def build_temporal_guidance(question, now=None):
    if now is None:
        now = datetime.now(timezone.utc)

    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("Timezone-aware datetime required")

    date = now.astimezone(timezone.utc).date().isoformat()

    base = (
        VERSION + "\n"
        + "CURRENT DATE (UTC): " + date + "\n"
        + "This date is provided by the server clock. "
        + "It is not proof that any external fact is current.\n"
        + "Treat earlier conversation facts, model knowledge, "
        + "and historical documents as potentially outdated.\n"
        + "Never treat model memory as a live news, market, "
        + "government, regulatory, or provider lookup."
    )

    if not requires_current_evidence(question):
        return base

    return base + """

CURRENT-FACT EVIDENCE STANDARD
The current user question may depend on facts that change over time.

Use relevant live retrieval results only when they were actually
returned by authorized tools in this request. Check the effective
date, publication date, event date, identity, jurisdiction, and
whether the source actually supports the specific claim.

Distinguish the present officeholder or status from a historical one.
Do not rely on an outdated remembered officeholder as current.

When current evidence is absent, stale, contradictory, or
insufficient, do not confidently guess the latest person,
price, officeholder, geopolitical status, release, or rule.

Say briefly what could not be verified and what information
is reliably known. Do not invent citations or imply a lookup ran.

A declaration is not required for a conflict to exist.
Distinguish official designations, observed events, and
analytical labels, including terms such as world war.

For financial questions, never invent fresh price quotes,
live account figures, portfolio positions, or broker status.
Historical or illustrative figures must be identified as such.

Prefer concise, directly responsive uncertainty over generic
disclaimers. Still answer stable parts of the user's question.
""".strip()

