
"""G43-R64 static CRA financial evidence catalogue.

This module never contacts a network, database or broker.
Its references are not live research results.
"""

from __future__ import annotations

import re

VERSION = "NEUROVEST_G43_R64_FINANCIAL_EVIDENCE"

SOURCES = {
    "rrsp_tax": {
        "title": "CRA — RRSP deduction",
        "url": (
            "https://www.canada.ca/en/revenue-agency/"
            "services/tax/individuals/topics/"
            "about-your-tax-return/tax-return/"
            "completing-a-tax-return/deductions-credits-expenses/"
            "line-20800-rrsp-deduction.html"
        ),
        "facts": [
            "Eligible RRSP contributions may produce income "
            "deductions, not direct income-tax credits.",
            "Tax savings depend on applicable marginal rates.",
            "Ordinary RRSP withdrawals are generally taxable.",
            "Contributing and claiming a deduction are "
            "distinct actions."
        ]
    },
    "rrsp_period": {
        "title": "CRA — RRSP contribution receipts",
        "url": (
            "https://www.canada.ca/en/revenue-agency/"
            "services/tax/individuals/topics/"
            "about-your-tax-return/tax-return/"
            "completing-a-tax-return/tax-slips/"
            "understand-your-tax-slips/"
            "rrsp-contribution-receipt-slip-information-"
            "individuals.html"
        ),
        "facts": [
            "Contributions during the first 60 days of "
            "the following calendar year may qualify "
            "for the previous tax year's deduction.",
            "The precise date for a specific year "
            "must be checked against current CRA guidance.",
            "This is not the income-tax filing deadline."
        ]
    },
    "rrsp_room": {
        "title": "CRA — RRSP deduction rules",
        "url": (
            "https://www.canada.ca/en/revenue-agency/"
            "services/tax/individuals/topics/"
            "about-your-tax-return/tax-return/"
            "completing-a-tax-return/deductions-credits-expenses/"
            "line-20800-rrsp-deduction.html"
        ),
        "facts": [
            "Eligible unused contributions may be deductible "
            "in a later year subject to applicable limits.",
            "Do not assume the user has available "
            "contribution or deduction room."
        ]
    },
    "tfsa_tax": {
        "title": "CRA — TFSA overview",
        "url": (
            "https://www.canada.ca/en/revenue-agency/"
            "services/tax/registered-plans-administrators/"
            "tax-free-savings-account-tfsa/"
            "about-tax-free-savings-account-tfsa.html"
        ),
        "facts": [
            "TFSA contributions are not tax-deductible.",
            "Eligible investment income and withdrawals "
            "are generally tax-free.",
            "Personal contribution room depends on "
            "eligibility and contribution history."
        ]
    },
    "tfsa_room": {
        "title": "CRA — TFSA withdrawals",
        "url": (
            "https://www.canada.ca/en/revenue-agency/"
            "services/tax/individuals/topics/"
            "tax-free-savings-account/withdraw.html"
        ),
        "facts": [
            "TFSA withdrawals generally restore "
            "contribution room on January 1 "
            "of the following calendar year.",
            "Withdrawal does not immediately create "
            "new contribution room in the same year.",
            "A same-year replacement requires sufficient "
            "other available contribution room."
        ]
    }
}

RRSP = re.compile(
    r"\b(?:rrsp|registered retirement savings plan)\b",
    re.I
)

TFSA = re.compile(
    r"\b(?:tfsa|tax.free savings account)\b",
    re.I
)

PERIOD = re.compile(
    r"\b(?:deadline|cutoff|cut.off|when|date|"
    r"tax year|first 60 days|contribut\w*)\b",
    re.I
)

ROOM = re.compile(
    r"\b(?:room|limits?|unused|carry.forward|"
    r"deduct\w*|contribut\w*)\b",
    re.I
)

WITHDRAW = re.compile(
    r"\b(?:withdraw\w*|re-?contribut\w*|"
    r"replace\w*|room|limits?|put back)\b",
    re.I
)

CURRENT = re.compile(
    r"\b(?:current|today|latest|this year|"
    r"202\d|203\d|deadline|contribution room|"
    r"tax brackets?|provincial rates?)\b",
    re.I
)


def select_sources(question):
    if not isinstance(question, str):
        return []

    if not 4 <= len(question) <= 5000:
        return []

    selected = []

    if RRSP.search(question):
        selected.append("rrsp_tax")

        if PERIOD.search(question):
            selected.append("rrsp_period")

        if ROOM.search(question):
            selected.append("rrsp_room")

    if TFSA.search(question):
        selected.append("tfsa_tax")

        if WITHDRAW.search(question):
            selected.append("tfsa_room")

    return list(dict.fromkeys(selected))


def grounding_for_question(question):
    ids = select_sources(question)

    if not ids:
        return ""

    lines = [
        "CANADIAN FINANCIAL EVIDENCE — G43-R64",
        "The following facts come from a static CRA "
        "reference catalogue, NOT fresh retrieval.",
        "Use only the relevant facts.",
        "Do not invent personal tax circumstances, "
        "current thresholds, deadlines or contribution room.",
        "Distinguish deductions from tax credits."
    ]

    for key in ids:
        source = SOURCES[key]

        lines.extend([
            "",
            "SOURCE: " + source["title"],
            "URL: " + source["url"],
        ])

        lines.extend(
            "- " + fact for fact in source["facts"]
        )

    if CURRENT.search(question):
        lines.extend([
            "",
            "CURRENT-DATA REQUIREMENT:",
            "Verify current tax-year dates, limits and "
            "rates using an up-to-date official source.",
            "If verification is unavailable, say so."
        ])

    lines.extend([
        "",
        "Give a direct, concise answer.",
        "Do not imply that static reference URLs "
        "were freshly opened or verified."
    ])

    return "\n".join(lines)
