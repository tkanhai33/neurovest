"""Bounded CRA-grounded TFSA/RRSP answer repair.

This module is NOT a general tax law checker and does not
determine personal contribution room or authorize actions.
"""
from __future__ import annotations

import re

VERSION = "G43-R50-R3"

SOURCES = (
    "https://www.canada.ca/en/revenue-agency/services/"
    "tax/individuals/topics/tax-free-savings-account/"
    "contributing/before.html",
    "https://www.canada.ca/en/revenue-agency/services/"
    "tax/individuals/topics/tax-free-savings-account/"
    "owing-tax/excess.html",
    "https://www.canada.ca/en/revenue-agency/services/"
    "tax/individuals/topics/rrsps-related-plans/"
    "rrsp-options-when-you-turn-71/options-your-rrsps.html",
)

def eligible(question):
    if not isinstance(question, str):
        return False
    q = question.casefold()
    # Generic educational comparison only.
    if not ("tfsa" in q and "rrsp" in q):
        return False
    if not re.search(
        r"\b(compare|comparison|difference|"
        r"explain|versus|vs\.?)\b",
        q,
    ):
        return False
    # Avoid altering personalized calculations or advice.
    if re.search(
        r"\b(my|mine|our|ours|account number|"
        r"portfolio|buy|sell|transfer|withdraw now|"
        r"execute|place an order)\b",
        q,
    ):
        return False
    return True


def findings(answer):
    if not isinstance(answer, str):
        return ["invalid_answer"]

    t = re.sub(r"\s+", " ", answer.casefold())
    errors = []

    if re.search(
        r"(?:tfsa.{0,150}(?:lifetime (?:max|limit|"
        r"ceiling)|lifetime contribution limit))"
        r"|(?:lifetime (?:max|limit|ceiling).{0,100}tfsa)",
        t,
    ):
        errors.append("invented_tfsa_lifetime_cap")

    if re.search(
        r"(?:tfsa.{0,100}(?:stop|ends?|expire|"
        r"must close).{0,45}(?:age )?71)"
        r"|(?:age 71.{0,100}tfsa.{0,50}"
        r"(?:stop|close|convert))",
        t,
    ):
        errors.append("wrong_tfsa_age_71_rule")

    if re.search(
        r"(?:rrsp.{0,140}(?:early withdrawal|"
        r"withdrawal before|before age 65).{0,65}"
        r"(?:10%|10 percent).{0,30}penalt)"
        r"|(?:early withdraw.{0,80}10%.{0,35}penalt)",
        t,
    ):
        errors.append("invented_rrsp_early_penalty")

    if re.search(
        r"(?:tfsa.{0,200}over.?contribut.{0,70}"
        r"(?:10%|10 percent))"
        r"|(?:over.?contribut.{0,85}"
        r"(?:10%|10 percent).{0,85}tfsa)",
        t,
    ):
        errors.append("wrong_tfsa_excess_tax_rate")

    if not t.strip():
        errors.append("empty_answer")

    return errors


def verified_explanation():
    return (
        "**TFSA versus RRSP — Canadian tax basics**\n\n"
        "| Topic | TFSA | RRSP |\n"
        "|---|---|---|\n"
        "| Contributions | Not tax-deductible | "
        "Eligible contributions are generally deductible "
        "within your available deduction limit |\n"
        "| Investment growth | Generally tax-free | "
        "Generally tax-deferred while held in the plan |\n"
        "| Withdrawals | Generally tax-free | "
        "Generally included in taxable income; "
        "withholding can apply |\n"
        "| Contribution room | Annual entitlements, unused "
        "room and eligible prior-year withdrawals, "
        "subject to CRA rules | Generally based on "
        "earned income, pension adjustments and "
        "applicable annual limits |\n\n"
        "**Important distinctions:** A TFSA does not have "
        "a universal $80,000 lifetime contribution ceiling "
        "or a mandatory closure at age 71. TFSA excess "
        "contributions are generally taxed at 1% per month "
        "on the highest excess amount for that month. "
        "An RRSP normally must mature by the end of the "
        "year its annuitant turns 71, through withdrawal, "
        "a RRIF transfer, or an annuity. Ordinary RRSP "
        "withdrawals do not have a universal 10% "
        "early-withdrawal penalty; income tax and "
        "withholding rules still apply.\n\n"
        "Your available contribution room is personal and "
        "must be checked against your own records and CRA "
        "information. This is general education, not "
        "personal tax or investment advice.\n\n"
        "**CRA references:**\n"
        + "\n".join("- " + url for url in SOURCES)
    )


def repair(question, answer, *, enabled=False,
           protected_developer=False):
    if not enabled or protected_developer:
        return answer, False, ()

    if not eligible(question):
        return answer, False, ()

    issues = findings(answer)

    if not issues:
        return answer, False, ()

    replacement = verified_explanation()
    if findings(replacement):
        raise RuntimeError(
            "R50-R3 reference text failed self-check"
        )

    return replacement, True, tuple(issues)


# NEUROVEST_G43_R53_FINANCIAL_ACCURACY
#
# Extend the installed R50-R3 findings function.
# This is deterministic and intentionally narrow:
# detected defects trigger the existing gated repair
# pathway; no new model calls or action permissions.

_r53_previous_findings = findings


def _r53_clean_line(line):
    import re
    text = re.sub(r"[*_`#|]+", " ", str(line))
    text = re.sub(r"\s+", " ", text)
    return text.casefold().strip()


def _r53_negative_claim(line):
    """Identify explicit negations of a penalty claim."""
    import re
    return bool(re.search(
        r"\b(?:no|not|never|without|"
        r"do not|does not|is not|isn't)\b"
        r".{0,85}\b(?:penalty|penalties)\b",
        line,
    ))


def _r53_additional_findings(answer):
    import re

    if not isinstance(answer, str):
        return ()

    text = str(answer)
    lower = text.casefold()

    if not (
        "tfsa" in lower
        or "rrsp" in lower
    ):
        return ()

    # Preserve individual lines and sentences to avoid
    # accidentally treating explanatory negations as
    # positive misinformation.
    units = []

    for raw_line in text.splitlines():
        cleaned = _r53_clean_line(raw_line)

        if not cleaned:
            continue

        units.append(cleaned)

        for part in re.split(
            r"(?<=[.!?])\s+",
            cleaned,
        ):
            if part and part != cleaned:
                units.append(part)

    errors = []

    def add(code):
        if code not in errors:
            errors.append(code)

    for line in units:

        # R52: "Early withdrawals ... may incur
        # a penalty tax of 10-20%".
        if (
            re.search(
                r"\bearly withdrawals?\b"
                r"|\bwithdrawals?\s*\("
                r"before age",
                line,
            )
            and re.search(
                r"\bpenalt(?:y|ies)\b"
                r"|\bpenalty tax\b",
                line,
            )
            and not _r53_negative_claim(line)
        ):
            add("unsupported_early_withdrawal_penalty")

        # R52: "Unused room does not carry forward"
        # in the RRSP portion of the answer.
        if re.search(
            r"\bunused (?:rrsp )?"
            r"(?:contribution |deduction )?room\b"
            r".{0,50}\b(?:does not|doesn't|"
            r"cannot|can not|won't|will not|"
            r"not)\s+carry\s+forward\b",
            line,
        ) and "rrsp" in lower:
            add("wrong_rrsp_unused_room_carryforward")

        # R52: "TFSA contribution room is reset annually."
        if re.search(
            r"\btfsa\b.{0,70}"
            r"\b(?:room|contribution room)\b"
            r".{0,30}\breset\s+annually\b",
            line,
        ):
            add("misleading_tfsa_room_reset")

        # R52: "No age restrictions (can contribute
        # at any age)" is false for TFSA eligibility.
        if re.search(
            r"\bno age restrictions\b"
            r"|\bcontribute at any age\b",
            line,
        ) and "tfsa" in lower:
            add("incorrect_tfsa_minimum_age")

        # 2023 TFSA annual dollar limit was $6,500,
        # not $6,000. Year-linked only.
        if (
            (
                re.search(
                    r"\$6,?000.{0,30}\b2023\b",
                    line,
                )
                or re.search(
                    r"\b2023\b.{0,30}\$6,?000",
                    line,
                )
            )
            and "tfsa" in lower
        ):
            add("wrong_tfsa_2023_limit")

        # R52: "RRSP unused room does not carry
        # forward", expressed without "room".
        if (
            "rrsp" in lower
            and re.search(
                r"\bunused contributions?\b"
                r".{0,50}\b(?:do not|does not|"
                r"cannot|not)\s+carry\s+forward\b",
                line,
            )
        ):
            add("wrong_rrsp_unused_room_carryforward")

    return tuple(errors)


def findings(answer):
    previous = list(
        _r53_previous_findings(answer)
    )

    for issue in _r53_additional_findings(answer):
        if issue not in previous:
            previous.append(issue)

    return previous
