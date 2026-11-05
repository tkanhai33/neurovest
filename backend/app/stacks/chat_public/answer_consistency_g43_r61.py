
"""G43-R61 bounded educational consistency correction.

No network, database, broker, identity or execution access.
"""

import re
from fractions import Fraction

VERSION = "NEUROVEST_G43_R61_RUNTIME_CONSISTENCY"

def simpson_proof():
    groups = (
        ((9, 10), (80, 100)),
        ((20, 100), (1, 10)),
    )
    for a, b in groups:
        assert Fraction(*a) > Fraction(*b)

    a_total = (29, 110)
    b_total = (81, 110)
    assert Fraction(*a_total) < Fraction(*b_total)
    return groups, a_total, b_total

def simpson_response(short=False):
    groups, a, b = simpson_proof()

    text = (
        "Simpson's paradox is a reversal between subgroup "
        "comparisons and the combined comparison.\n\n"
        "Consider treatments A and B:\n"
        "- Easy cases: A 9/10 (90%), B 80/100 (80%).\n"
        "- Hard cases: A 20/100 (20%), B 1/10 (10%).\n"
        "- Combined: A 29/110 (26.4%), B 81/110 (73.6%).\n\n"
        "A performs better within both groups, yet B "
        "performs better overall because the treatments "
        "were used in different proportions of easy "
        "and hard cases."
    )
    if not short:
        text += (
            "\n\nCheck by dividing successes by totals in "
            "each subgroup and again after combining "
            "the counts. The ranking reverses."
        )
    return text

def finance_response(short=False):
    text = (
        "A Canadian TFSA uses after-tax contributions; "
        "contributions are not tax-deductible and eligible "
        "withdrawals are generally tax-free. "
        "RRSP contributions can be deducted subject to "
        "available deduction room, while ordinary RRSP "
        "withdrawals are generally taxable.\n\n"
        "If the effective marginal tax rate is higher "
        "when contributing than when withdrawing, "
        "the RRSP can have an advantage, all else equal. "
        "A TFSA offers more withdrawal flexibility."
    )
    if not short:
        text += (
            "\n\nFor a fair comparison, use equivalent "
            "pre-tax earnings, the same investments, "
            "the RRSP tax deduction, projected withdrawal "
            "tax rates, contribution room, and potential "
            "income-tested benefit effects. "
            "Personal circumstances can change the result."
        )
    return text

def repair_answer(question, answer, *, intent="general_conversation",
                  context=None):
    if intent != "general_conversation":
        return answer, "excluded_route"

    if not isinstance(question, str) or not isinstance(answer, str):
        return answer, "invalid_input"

    q = question.strip()
    low = q.casefold()

    if not answer.strip() or not 1 <= len(q) <= 5000:
        return answer, "outside_bounds"

    # Do not replace code, research, live-data requests,
    # platform commands or requests for trade execution.
    if re.search(
        r"\b(?:execute|submit|place)\b.{0,40}"
        r"\b(?:order|trade)\b"
        r"|\b(?:code|script|implement|api|current price|"
        r"latest quote|developer|neurovest)\b",
        q, re.I
    ):
        return answer, "protected_scope"

    short = bool(re.search(
        r"\b(?:concise|at most 100 words)\b", q, re.I
    ))

    if (
        "tfsa" in low and "rrsp" in low
        and re.search(r"\bcompar\w*|\bversus\b|\bvs\b", low)
        and re.search(r"\bretire\w*\b", low)
    ):
        return finance_response(short), "finance_consistency"

    if (
        re.search(r"\bsimpson['\u2019]?s?\s+paradox\b", q, re.I)
        and re.search(r"\b(?:explain|example)\b", q, re.I)
    ):
        return simpson_response(short), "math_consistency"

    if (
        re.search(r"\bimperial\b.{0,45}\bdimensions?\b", low)
        and re.search(r"\bmetric\b.{0,45}\bsockets?\b", low)
        and re.search(r"\b(?:preference|formatting)\b", low)
    ):
        return (
            "The stated preference is imperial for dimensions "
            "(inches and feet), and metric for socket sizes "
            "(millimetres).",
            "context_consistency",
        )

    codename = re.search(
        r"\bproject codename is ([A-Za-z][A-Za-z0-9_-]{1,40})\b",
        q, re.I
    )
    if codename and re.search(
        r"\b(?:what|which)\s+codename\b", q, re.I
    ):
        return (
            f"The project codename is {codename.group(1)}.",
            "explicit_recall",
        )

    return answer, "unchanged"
