"""Conservative, audit-only NeuroVest capability checks.

No authorization decisions or response modifications occur here.
"""

from __future__ import annotations

import re


_RULES = {
    "live_broker_permission": re.compile(
        r"\b(?:I|we|NeuroVest|Neuro)\s+can\s+"
        r"(?:place|execute|submit)\s+"
        r"(?:real|live|brokerage)\s+"
        r"(?:brokerage\s+)?(?:orders?|trades?)\b",
        re.I,
    ),
    "paper_trading_unavailable": re.compile(
        r"\b(?:paper trading|simulations?|simulated trading)"
        r"(?:\s+and\s+(?:simulation|paper trading))?"
        r"\s+(?:is|are|remain|remains)\s+"
        r"(?:disabled|unavailable|locked)\b"
        r"|\bpaper trading cannot be used\b",
        re.I,
    ),
    "simulated_execution_unavailable": re.compile(
        r"\b(?:live\s+)?(?:trade\s+)?execution\s+"
        r"(?:is|remains)\s+disabled\b"
        r"[^.!?\n]{0,110}\b"
        r"(?:simulated trades?|paper trades?)\b",
        re.I,
    ),
    "automatic_language_model_learning": re.compile(
        r"\bI automatically retrain my language model\b"
        r"[^.!?\n]{0,100}\b(?:conversations?|messages?)\b",
        re.I,
    ),
    "personal_global_profile_modification": re.compile(
        r"\bpersonal (?:strategy )?training\b"
        r"[^.!?\n]{0,40}\b"
        r"(?:modifies|changes|updates)\b"
        r"[^.!?\n]{0,40}\bglobal strategy profile\b",
        re.I,
    ),
}

_REPORTED = re.compile(
    r"\b(?:asked|asks|questioned|wondered|"
    r"wanted\s+to\s+know|inquired)\b"
    r"[^.!?\n]{0,90}?\b(?:whether|if)\b",
    re.I,
)

_FALSE_QUOTE = re.compile(
    r'["“][^"”]+["”]\s+is\s+(?:false|incorrect)\b',
    re.I,
)



# NEUROVEST_UNIFIED_CAPABILITY_V1R5
# Audit-only detection; never authorizes broker or training actions.

_PAPER_V1R5_SUBJECT = (
    r"(?:paper trading|paper trades?|simulated trades?|"
    r"simulated trading|simulations?|simulation features?)"
)

_PAPER_V1R5_DIRECT = re.compile(
    r"\b" + _PAPER_V1R5_SUBJECT
    + r"(?:\s+and\s+(?:simulations?|simulation features?))?"
    + r"\s+(?:is|are|remain|remains)"
    + r"\s+(?:currently\s+)?"
    + r"(?:disabled|unavailable|locked)\b",
    re.I,
)

_PAPER_V1R5_PRONOUN = re.compile(
    r"\bas for\s+" + _PAPER_V1R5_SUBJECT
    + r"\s*,\s*(?:it['’]s|they['’]re|it is|they are)"
    + r"\s+(?:currently\s+)?"
    + r"(?:disabled|unavailable|locked)\b",
    re.I,
)

_PAPER_V1R5_ACTION = re.compile(
    r"\b(?:cannot|can['’]t|unable to)"
    r"\s+(?:currently\s+)?"
    r"(?:run|place|execute|use)"
    r"\s+(?:(?:any|a)\s+)?"
    r"(?:simulated|paper)\s+trades?\b",
    re.I,
)

_PAPER_V1R5_ATTRIBUTED = re.compile(
    r"\b(?:earlier|previous|prior|old|quoted|reported)"
    r"\s+(?:assistant\s+)?"
    r"(?:statement|claim|response|answer|message)\b"
    r".{0,120}?\b(?:was|is|were)\s+"
    r"(?:incorrect|wrong|false|mistaken)\b",
    re.I,
)

_PAPER_V1R5_REJECTION = re.compile(
    r"\b(?:it is false that|it is incorrect that|"
    r"it's false that|it's incorrect that|"
    r"contrary to the claim that)\b",
    re.I,
)

_PAPER_V1R5_QUOTED_REJECTION = re.compile(
    r'["“][^"”]+["”]\s+'
    r'(?:is|was)\s+(?:false|incorrect|wrong)\b',
    re.I,
)

_PAPER_V1R5_CONTRAST = re.compile(
    r"[,;]\s*(?:but|however|yet)\s+",
    re.I,
)



# NEUROVEST_UNIFIED_CAPABILITY_V1R6R3
# Supplemental direct/pronoun detection through the V1R5 audit path.
# This remains observational, not a history-redaction authorization.

_PAPER_V1R6R3_SUBJECT = (
    r"(?:paper trading|paper trades?|"
    r"simulated paper trades?|simulated trades?|"
    r"simulated trading|simulations?|simulation features?)"
)

_PAPER_V1R6R3_PRONOUN = re.compile(
    r"\b(?:as for\s+)?"
    + _PAPER_V1R6R3_SUBJECT
    + r"\s*(?:[,;:]|[—–-])\s*"
    + r"(?:they['’]re|it['’]s|they are|it is)"
    + r"\s+(?:currently\s+)?"
    + r"(?:disabled|unavailable|locked)\b",
    re.I,
)

_PAPER_V1R6R3_DIRECT = re.compile(
    r"\b" + _PAPER_V1R6R3_SUBJECT
    + r"\s+(?:is|are|remain|remains)"
    + r"\s+(?:currently\s+)?"
    + r"(?:disabled|unavailable|locked)\b",
    re.I,
)


def _paper_supplement_v1r6r3(clause: str) -> bool:
    # Reuse the V1R5 rejection checks instead of creating
    # a competing correction/quotation decision path.
    if (
        _PAPER_V1R5_ATTRIBUTED.search(clause)
        or _PAPER_V1R5_REJECTION.search(clause)
        or _PAPER_V1R5_QUOTED_REJECTION.search(clause)
    ):
        return False

    return bool(
        _PAPER_V1R6R3_PRONOUN.search(clause)
        or _PAPER_V1R6R3_DIRECT.search(clause)
    )


def _paper_contradiction_v1r5(clause: str) -> bool:
    if (
        _PAPER_V1R5_ATTRIBUTED.search(clause)
        or _PAPER_V1R5_REJECTION.search(clause)
        or _PAPER_V1R5_QUOTED_REJECTION.search(clause)
    ):
        return False

    return any(
        pattern.search(clause)
        for pattern in (
            _PAPER_V1R5_DIRECT,
            _PAPER_V1R5_PRONOUN,
            _PAPER_V1R5_ACTION,
        )
    )


def audit_capability_claims(response: str) -> dict:
    """Return potential contradiction categories, without raw text.

    Conservative heuristic: results require review and never authorize
    automatic correction, suppression, or operational actions.
    """
    text = str(response or "")
    findings = []

    # Bound processing cost independently of the caller.
    text = text[:20000]

    # Analyze clauses rather than exempting entire answers
    # because one clause contains a reported question.
    clauses = re.split(r"(?<=[.!?])\s+|\n+", text)

    for sentence in clauses[:160]:
        for part in _PAPER_V1R5_CONTRAST.split(sentence):
            stripped = part.strip()

            if not stripped or stripped.endswith("?"):
                continue

            if (
                _FALSE_QUOTE.search(stripped)
                or _REPORTED.search(stripped)
            ):
                continue

            if (_paper_contradiction_v1r5(stripped) or _paper_supplement_v1r6r3(stripped)):
                findings.append("paper_trading_unavailable")

            for category, pattern in _RULES.items():
                # V1R5 is the sole classifier for paper-trading
                # availability. Do not run the superseded regex.
                if category == "paper_trading_unavailable":
                    continue

                if (
                    _PAPER_V1R5_ATTRIBUTED.search(stripped)
                    or _PAPER_V1R5_REJECTION.search(stripped)
                    or _PAPER_V1R5_QUOTED_REJECTION.search(stripped)
                ):
                    continue

                if pattern.search(stripped):
                    findings.append(category)

    return {
        "mode": "audit_only",
        "potential_contradictions": sorted(set(findings)),
        "review_required": bool(findings),
        "enforcement_enabled": False,
    }
