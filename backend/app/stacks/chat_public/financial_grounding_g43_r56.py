
"""G43-R56: bounded, evidence-backed Canadian account grounding.

No network access, execution authority, account access or private data.
Disabled unless NV_G43_R56_FINANCE_ENABLED=1.
"""

import re

FLAG = "NV_G43_R56_FINANCE_ENABLED"

REFERENCES = {
    "tfsa": (
        "TFSA withdrawals restore contribution room on January 1 of "
        "the NEXT calendar year, not immediately. A contribution "
        "in the withdrawal year is permitted only to the extent "
        "unused contribution room already exists. Ordinary TFSA "
        "withdrawals are generally not subject to income tax "
        "withholding or an age-based early-withdrawal penalty. "
        "There is no fixed TFSA lifetime dollar ceiling independent "
        "of individual accumulated room.",
        "https://www.canada.ca/en/revenue-agency/services/tax/"
        "individuals/topics/tax-free-savings-account/withdraw.html",
    ),
    "rrsp": (
        "Unused RRSP deduction room may be carried forward; "
        "there is no general 15-year expiry. Making an RRSP "
        "contribution and claiming its tax deduction are separate "
        "events. Ordinary RRSP withdrawals are taxable income; "
        "tax withheld at source is not a general early-withdrawal "
        "penalty. Special locked-in plans and specific programs "
        "have different rules.",
        "https://www.canada.ca/en/revenue-agency.html",
    ),
    "fhsa": (
        "An FHSA offers deductible eligible contributions and "
        "tax-free qualifying withdrawals for eligible first-time "
        "homebuyers. A non-qualifying withdrawal is generally "
        "taxable income, and eligibility and timing conditions "
        "must be checked. Do not invent special fixed penalties, "
        "an account-level home-price ceiling, or employer "
        "contribution allowances.",
        "https://www.canada.ca/en/revenue-agency/services/tax/"
        "individuals/topics/first-home-savings-account/"
        "withdrawals-transfers-out-your-fhsas.html",
    ),
    "rrif": (
        "An RRSP must mature no later than December 31 of the "
        "year its holder turns 71. Options generally include "
        "a RRIF, eligible annuity, or withdrawal. Standard RRIF "
        "minimum withdrawal factor at age 71 is 5.28%, not "
        "25%; payment timing and younger-spouse age elections "
        "may change an individual's calculation.",
        "https://www.canada.ca/en/revenue-agency.html",
    ),
}

def topics(question):
    q = str(question or "").casefold()
    found = []
    for term in ("tfsa", "rrsp", "fhsa", "rrif"):
        if re.search(r"\b" + term + r"s?\b", q):
            found.append(term)
    return tuple(found)

def guidance(question):
    selected = topics(question)
    if not selected:
        return ""
    parts = [
        "VERIFIED CANADIAN ACCOUNT FACTS (stable educational facts):",
        "Distinguish the facts below from personal advice.",
        "Do not fabricate dates, rates, limits or source verification.",
    ]
    for term in selected:
        claim, url = REFERENCES[term]
        parts.append(f"{term.upper()}: {claim} Reference: {url}")
    parts.append(
        "If uncertain about current law or an individual's room, "
        "explain what must be checked instead of guessing."
    )
    return "\n".join(parts)

def problematic_claims(question, answer):
    """Conservative diagnostics, not a general factual grade."""
    selected = topics(question)
    text = str(answer or "")
    issues = []
    # Explicit positives only: negations and quoted examples are
    # handled separately by not triggering an automatic replacement.
    if "tfsa" in selected:
        if re.search(
            r"(?:withdraw(?:n|al)? amounts?|withdrawn funds)"
            r".{0,90}(?:immediately|same calendar year)"
            r".{0,55}(?:recontribut|available)",
            text, re.I | re.S
        ):
            issues.append("tfsa_same_year_recontribution_claim")
        if re.search(
            r"(?:withholding tax|withheld tax)"
            r".{0,90}TFSA withdrawals?"
            r"|TFSA withdrawals?.{0,90}(?:withholding tax|withheld tax)",
            text, re.I
        ):
            # Only flag for manual checking because a correct answer
            # can say "no withholding tax".
            issues.append("tfsa_withholding_claim_review")
    if "rrsp" in selected:
        if re.search(
            r"(?:unused (?:RRSP )?(?:contribution )?room)"
            r".{0,90}(?:15 years?|expires after 15)",
            text, re.I | re.S
        ):
            issues.append("rrsp_room_expiry_review")
    return tuple(issues)

def review(question, answer, *, protected_developer=False):
    """Return answer unchanged, plus inspectable diagnostics.

    No unverifiable rewriting and no override of developer replies.
    """
    if protected_developer or not topics(question):
        return answer, ()
    return answer, problematic_claims(question, answer)



# G43_R56_CONTROLLED_CORRECTIONS_V2
# Retains the original Canadian grounding and diagnostic rules.
# Corrects only narrowly recognized false affirmative statements.
# Does not claim comprehensive factual verification.

from decimal import Decimal

VERSION = "G43-R56-CONTROLLED-V2"

_previous_review = review


def required_recovery_percent(loss_percent):
    """Gain percentage needed to recover from a loss percentage."""
    loss = Decimal(str(loss_percent))

    if not loss.is_finite() or not (
        Decimal("0") <= loss < Decimal("100")
    ):
        raise ValueError("loss must be finite and 0 <= loss < 100")

    return (
        Decimal("100") * loss
        / (Decimal("100") - loss)
    )


def rebalance_deltas(total, targets, current):
    """Calculate dollar trades for target portfolio weights."""
    total = Decimal(str(total))

    weights = {
        k: Decimal(str(v))
        for k, v in targets.items()
    }
    holdings = {
        k: Decimal(str(v))
        for k, v in current.items()
    }

    if not total.is_finite() or total < 0:
        raise ValueError("invalid portfolio total")

    if set(weights) != set(holdings):
        raise ValueError("asset keys must match")

    if any(
        not v.is_finite() or v < 0
        for v in list(weights.values())
        + list(holdings.values())
    ):
        raise ValueError("invalid allocation data")

    if sum(weights.values()) != Decimal("100"):
        raise ValueError("weights must total 100")

    if sum(holdings.values()) != total:
        raise ValueError("holdings must equal portfolio total")

    return {
        k: total * weights[k] / Decimal("100")
        - holdings[k]
        for k in weights
    }


# Exact affirmative statements, deliberately not broad
# semantic substitutions. Unknown wording is not rewritten.
_CORRECTIONS = (
    (
        "tfsa",
        re.compile(
            r"TFSA withdrawals immediately restore "
            r"contribution room in the same year\.",
            re.I,
        ),
        "TFSA withdrawals generally restore contribution "
        "room on January 1 of the following calendar year.",
        "corrected_tfsa_recontribution",
    ),
    (
        "rrsp",
        re.compile(
            r"Unused RRSP contribution room expires "
            r"after 15 years\.",
            re.I,
        ),
        "Unused RRSP contribution room generally carries "
        "forward without a 15-year expiry.",
        "corrected_rrsp_expiry",
    ),
    (
        "rrsp",
        re.compile(
            r"Every early RRSP withdrawal has a "
            r"10% early withdrawal penalty\.",
            re.I,
        ),
        "Ordinary RRSP withdrawals are generally taxable "
        "and may have withholding tax, but there is no "
        "universal 10% early-withdrawal penalty.",
        "corrected_rrsp_penalty",
    ),
    (
        "tfsa",
        re.compile(
            r"TFSA withdrawals are subject to "
            r"Canadian withholding tax\.",
            re.I,
        ),
        "Ordinary TFSA withdrawals are generally not "
        "subject to Canadian income tax withholding.",
        "corrected_tfsa_withholding",
    ),
)


def _correct_standalone_statements(question, answer):
    selected = set(topics(question))
    updated = answer
    corrections = []

    # Do not change quotations, code fences, or negated statements.
    if (
        '```' in answer
        or '"' in answer
        or "\u201c" in answer
        or "\u201d" in answer
    ):
        return answer, ()

    for topic, pattern, replacement, code in _CORRECTIONS:
        if topic not in selected:
            continue

        # Recognize whole standalone lines only.
        lines = updated.splitlines(keepends=True)
        new_lines = []
        changed = False

        for line in lines:
            content = line.rstrip("\r\n")
            suffix = line[len(content):]

            if pattern.fullmatch(content.strip()):
                new_lines.append(replacement + suffix)
                changed = True
            else:
                new_lines.append(line)

        if changed:
            updated = "".join(new_lines)
            corrections.append(code)

    return updated, tuple(corrections)


def _correct_recovery_example(question, answer):
    q = question.casefold()

    if not any(
        word in q
        for word in ("recover", "recovery", "loss", "drawdown")
    ):
        return answer, ()

    # Only handle a standalone, explicit percentage example.
    pattern = re.compile(
        r"A ([0-9]+(?:\.[0-9]+)?)% loss "
        r"requires a ([0-9]+(?:\.[0-9]+)?)% "
        r"gain to recover\.",
        re.I,
    )

    if not pattern.fullmatch(answer.strip()):
        return answer, ()

    match = pattern.fullmatch(answer.strip())
    loss = Decimal(match.group(1))
    stated = Decimal(match.group(2))

    if not (
        Decimal("0") <= loss < Decimal("100")
    ):
        return answer, ("invalid_recovery_input",)

    expected = required_recovery_percent(loss)

    if abs(stated - expected) <= Decimal("0.005"):
        return answer, ()

    value = format(
        expected.quantize(Decimal("0.01")),
        "f",
    ).rstrip("0").rstrip(".")

    corrected = (
        f"A {match.group(1)}% loss requires approximately "
        f"a {value}% gain from the reduced value to recover."
    )

    return corrected, ("corrected_recovery_math",)


def review(question, answer, *, protected_developer=False):
    """Preserve prior diagnostics; correct only supported patterns."""
    if protected_developer:
        return answer, ()

    original_answer, original_findings = _previous_review(
        question,
        answer,
        protected_developer=False,
    )

    if not isinstance(original_answer, str):
        return original_answer, tuple(original_findings)

    corrected, factual = _correct_standalone_statements(
        question,
        original_answer,
    )

    corrected, numerical = _correct_recovery_example(
        question,
        corrected,
    )

    findings = tuple(dict.fromkeys(
        tuple(original_findings)
        + tuple(factual)
        + tuple(numerical)
    ))

    return corrected, findings



# G43_R56_FINANCIAL_INTEGRITY_V3_R2
# Coordinates the existing V2 recovery corrector with V3.
# No additional model, network, database or trading access.

import re as _r56_re
from decimal import Decimal as _R56Decimal
from decimal import ROUND_HALF_UP as _R56_ROUND

V3_VERSION = "G43-R56-V3-R2"

_r56_v2_recovery = _correct_recovery_example

_R56_QUESTION_LOSS = _r56_re.compile(
    r"(?<![\d.])(\d+(?:\.\d+)?)%\s+"
    r"(?:(?:investment|portfolio|stock)\s+)?"
    r"(?:loss|drawdown|drop|decline)\b",
    _r56_re.I,
)

_R56_ANSWER_RECOVERY = _r56_re.compile(
    r"\bA\s+(?P<loss>\d+(?:\.\d+)?)%\s+loss\s+"
    r"requires\s+(?:approximately\s+)?"
    r"(?:a\s+)?(?P<gain>\d+(?:\.\d+)?)%\s+gain\s+"
    r"to\s+recover\b\.?",
    _r56_re.I,
)


def _r56_question_loss(question):
    if not isinstance(question, str):
        return None

    if not _r56_re.search(
        r"\b(?:recover|recovery|break.even|"
        r"gain|loss|drawdown)\b",
        question, _r56_re.I,
    ):
        return None

    values = _R56_QUESTION_LOSS.findall(question)

    if len(values) != 1:
        return None

    try:
        value = _R56Decimal(values[0])
        if value.is_finite() and 0 <= value < 100:
            return value
    except ArithmeticError:
        pass

    return None


# Important: V2 review looks up this function at runtime.
# Preserve V2's actual implementation, but block it when
# the question does not independently establish the
# matching loss percentage.
def _correct_recovery_example(question, answer):
    loss = _r56_question_loss(question)

    if loss is None or not isinstance(answer, str):
        return answer, ()

    if any(mark in answer for mark in (
        "```", '"', "\u201c", "\u201d",
    )):
        return answer, ()

    match = _R56_ANSWER_RECOVERY.fullmatch(answer.strip())

    if match is None:
        return answer, ()

    if _R56Decimal(match.group("loss")) != loss:
        return answer, ()

    return _r56_v2_recovery(question, answer)


_r56_previous_review = review


def _r56_contextual_recovery(question, answer):
    loss = _r56_question_loss(question)

    if loss is None or not isinstance(answer, str):
        return answer, ()

    if any(mark in answer for mark in (
        "```", '"', "\u201c", "\u201d",
    )):
        return answer, ()

    updated = []
    changes = 0

    for line in answer.splitlines(keepends=True):
        match = _R56_ANSWER_RECOVERY.search(line)

        if match is None:
            updated.append(line)
            continue

        if _r56_re.search(
            r"^\s*(?:>|#|//)",
            line,
        ):
            updated.append(line)
            continue

        if _r56_re.search(
            r"\b(?:not|incorrect|wrong|false|"
            r"never|doesn't|isn't)\b",
            line, _r56_re.I,
        ):
            updated.append(line)
            continue

        stated_loss = _R56Decimal(match.group("loss"))
        stated_gain = _R56Decimal(match.group("gain"))

        if stated_loss != loss:
            updated.append(line)
            continue

        expected = required_recovery_percent(loss)

        if abs(expected - stated_gain) <= _R56Decimal("0.005"):
            updated.append(line)
            continue

        rounded = expected.quantize(
            _R56Decimal("0.01"),
            rounding=_R56_ROUND,
        )

        number = format(rounded, "f").rstrip("0").rstrip(".")

        replacement = (
            f"A {match.group('loss')}% loss requires "
            f"approximately a {number}% gain "
            "from the reduced value to recover."
        )

        updated.append(
            line[:match.start()]
            + replacement
            + line[match.end():]
        )
        changes += 1

    if not changes:
        return answer, ()

    return (
        "".join(updated),
        ("v3_corrected_recovery_math",),
    )


def review(question, answer, *, protected_developer=False):
    if protected_developer:
        return answer, ()

    previous, old_findings = _r56_previous_review(
        question,
        answer,
        protected_developer=False,
    )

    corrected, new_findings = _r56_contextual_recovery(
        question,
        previous,
    )

    return corrected, tuple(dict.fromkeys(
        tuple(old_findings) + tuple(new_findings)
    ))
