"""
G43-R59: general answer-quality guidance.

Prompt guidance only.
No database, network, broker, execution or identity authority.
"""

from __future__ import annotations

import re


VERSION = "NEUROVEST_G43_R59_QUALITY_GUIDANCE"


GENERAL_GUIDANCE = """
NEUROVEST ANSWER RELIABILITY:

Answer the user's actual question directly.

Use the conversation context already supplied.
When the user asks for a previously supplied fact,
retrieve that fact from the available conversation
rather than asking for it again.

A newer explicit correction supersedes an older
statement about the same subject.

Do not claim to remember information that is
not present in the supplied context.

Before giving a numerical result, check the
arithmetic and explain only the necessary steps.

Before using an illustrative example, confirm
that the example actually demonstrates the
claimed mathematical or logical property.

For comparisons, evaluate both sides consistently
using the same assumptions and definitions.

Separate verified facts, user-supplied information,
estimates, assumptions, and unknowns.

Never claim a source, price, filing, tool result,
or calculation was verified unless supporting
evidence is actually available.

Prefer concise, complete answers.
Do not sacrifice correctness for brevity.

Preserve authorization, execution, citation, and safety boundaries relevant to the user's request.
"""


CANADIAN_ACCOUNT_GUIDANCE = """
CANADIAN REGISTERED ACCOUNT FACTS:

TFSA contributions are not tax deductible.

Eligible TFSA withdrawals are generally tax-free.

RRSP contributions may qualify for an income-tax
deduction, subject to available deduction room.

Ordinary RRSP withdrawals are generally taxable.

When comparing TFSA and RRSP accounts, consider
the person's marginal tax rate now and later,
contribution room, withdrawal flexibility,
eligibility, and individual circumstances.

All else equal, a lower expected tax rate
on RRSP withdrawal can favour the RRSP
tax-deferral comparison.

Do not recommend TFSA solely because the
retirement tax rate is expected to be lower.

Do not invent current contribution limits,
personal contribution room, or eligibility.

These are general educational facts, not
personalized tax or financial advice.
"""


_ACCOUNT_PATTERN = re.compile(
    r"\b(?:tfsa|rrsp)\b",
    re.IGNORECASE,
)


def build_guidance(message: str) -> str:
    """Construct bounded prompt guidance for a user question."""

    question = message if isinstance(message, str) else ""

    result = GENERAL_GUIDANCE

    if _ACCOUNT_PATTERN.search(question):
        result += "\n" + CANADIAN_ACCOUNT_GUIDANCE

    return result


# NEUROVEST_G43_R64_FINANCIAL_EVIDENCE
from functools import wraps as _r64_wraps

_r64_original_guidance = build_guidance

@_r64_wraps(_r64_original_guidance)
def build_guidance(*args, **kwargs):
    original = _r64_original_guidance(*args, **kwargs)

    question = (
        args[0] if args else
        kwargs.get("message", kwargs.get("question", ""))
    )

    from backend.app.stacks.chat_public.financial_evidence_g43_r64 import (
        grounding_for_question as _r64_ground,
    )

    evidence = _r64_ground(question)

    if not evidence:
        return original

    if not isinstance(original, str):
        raise TypeError(
            "R64 expected string guidance output"
        )

    return original + "\n\n" + evidence
