
"""Conservative conversational formatting helpers.

No external IO, account access, tools, actions, or inference.
Only remove clear adjacent continuation echoes.
"""
from __future__ import annotations

import re

MARKER = "NEUROVEST_CONVERSATION_POLISH_R36"

GUIDANCE = """
CONVERSATIONAL PACING:
For beginners requesting simple explanations or step-by-step
help, respond like a helpful conversational guide.
Start with the direct answer and one useful next step.
Explain unfamiliar terms in plain language.
Prefer short paragraphs over long enumerated lectures.
Ask one relevant follow-up question when it helps.
Do not omit essential risk information or calculations.
Do not invent personalized financial facts.
Provide greater detail when explicitly requested.
"""


def clean_continuation_echo(value: str) -> str:
    """Remove only adjacent duplicate lead-in lines.

    Example:
      So, in short
      So, in short, the next step is ...

    Does not rewrite arithmetic or remove repeated content
    separated by paragraphs of different information.
    """
    if not isinstance(value, str) or not value:
        return value

    lines = value.splitlines(keepends=True)
    cleaned = []
    index = 0

    while index < len(lines):
        current = lines[index]
        lead = current.strip()

        if (
            lead
            and len(lead) <= 90
            and not lead.startswith(("-", "*", "#", ">", "|"))
        ):
            following = index + 1
            while (
                following < len(lines)
                and not lines[following].strip()
            ):
                following += 1

            if following < len(lines):
                next_line = lines[following].strip()
                a = re.sub(r"\s+", " ", lead).casefold()
                b = re.sub(r"\s+", " ", next_line).casefold()

                if (
                    len(a) >= 12
                    and b.startswith(a)
                    and len(b) > len(a)
                    and (
                        b[len(a)] in " ,.:;!?-"
                        or a.endswith((",", ":", "..."))
                    )
                ):
                    # Drop the orphaned prefix and blank lines
                    # only when the next line repeats it.
                    index = following
                    continue

        cleaned.append(current)
        index += 1

    return "".join(cleaned)
