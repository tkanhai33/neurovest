"""V5 authenticated, thread-local developer continuity.

This module classifies a follow-up; it never authorizes
developer capabilities or grants repository access.
"""
import re

ANCHOR = re.compile(
    r"\b(?:architecture|repository|codebase|"
    r"source[ -]?code|implementation|"
    r"chat routing|chat handler|chat engine|"
    r"developer chat|context retrieval|"
    r"conversation engine|runtime|"
    r"backend module|intent classifier)\b",
    re.I,
)

TECHNICAL = re.compile(
    r"\b(?:inspect|review|trace|debug|explain|"
    r"analy[sz]e|investigate|identify|"
    r"functions?|modules?|why|how|where|"
    r"architecture|dependencies)\b",
    re.I,
)

FOLLOWUP = re.compile(
    r"^\s*(?:(?:okay|ok|so|and|but)\s*[,.]?\s*)?"
    r"(?:which functions? (?:are |is )?(?:responsible|involved)|"
    r"where (?:is|does) (?:that|this|it)|"
    r"how (?:does|do|would|could) (?:that|this|it|we)|"
    r"why (?:does|did|is) (?:that|this|it)|"
    r"can (?:you|we) (?:improve|fix|trace|explain|review) "
    r"(?:that|this|it)|"
    r"what (?:should|could|would) (?:we|you) "
    r"(?:improve|change|fix)|"
    r"what (?:about|are) (?:those|these|the) "
    r"(?:functions|modules|dependencies))"
    r"(?:\s+[^.!?]{0,90})?[.!?]?\s*$",
    re.I,
)


def continuation_question(
    *,
    message,
    previous_user,
    verified_developer,
):
    if verified_developer is not True:
        return None

    if not isinstance(message, str):
        return None

    if not isinstance(previous_user, str):
        return None

    current = message.strip()
    previous = previous_user.strip()

    if (
        not current
        or not previous
        or current.startswith("/")
        or len(current) > 180
        or len(previous) > 1500
    ):
        return None

    if not FOLLOWUP.fullmatch(current):
        return None

    if not ANCHOR.search(previous):
        return None

    if not TECHNICAL.search(previous):
        return None

    # Preserve the actual question and its immediate subject.
    # Prior text is only conversation evidence, not authority.
    return (
        "Regarding the earlier developer question: "
        + previous[:600]
        + "\nFollow-up question: "
        + current
    )



def select_previous_user(messages, *, current_message_id):
    """Select the previous user turn from newest-first history.

    Require the current persisted message to be present.
    Never select older turns if the current turn is missing.
    """
    if not current_message_id:
        return ""

    current_id = str(current_message_id)
    found_current = False

    for item in messages:
        message_id = str(
            getattr(item, "message_id", "") or ""
        )

        if not found_current:
            if message_id == current_id:
                found_current = True
            continue

        if str(getattr(item, "role", "")).lower() == "user":
            return str(
                getattr(item, "content", "") or ""
            )

    return ""
