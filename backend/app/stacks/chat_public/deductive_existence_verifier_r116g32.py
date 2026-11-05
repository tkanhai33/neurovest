
"""Conservative logical-validity verifier for explicit syllogisms.

This module proves only a narrow class of invalid conclusions.
Unsupported input is returned as "abstain", not guessed.
No model, network, database, authorization or trading access.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Verification:
    status: str
    reason: str
    rule: str



def _sentences(text: str):
    if not isinstance(text, str):
        return None
    if not 1 <= len(text.strip()) <= 600:
        return None

    fragments = []
    for line in text.splitlines():
        for sentence in re.split(r"[.!?]+", line):
            sentence = sentence.strip()
            if sentence:
                fragments.append(sentence)

    return fragments or None




def _universal_only(statement: str) -> bool:
    if not isinstance(statement, str):
        return False

    text = statement.strip().casefold()
    if not 1 <= len(text) <= 500:
        return False

    # Accept one terminal period only. Everything else
    # must belong to a single supported statement.
    if text.endswith("."):
        text = text[:-1].strip()

    if any(mark in text for mark in
           (".", "!", "?", ",", ";", ":", "(", ")",
            "{", "}", "[", "]", "/", "\\", "\n", "\r")):
        return False

    # Whole-word exclusions, not substring exclusions:
    # "orders" must not accidentally match "or".
    forbidden = {
        "some", "exists", "exist", "existing", "existence",
        "there", "any", "either", "or", "and", "if",
        "unless", "except", "excepting", "only", "not",
        "never", "without", "but", "however", "although",
        "which", "who", "that", "including", "excluding",
        "none", "no", "at", "least", "most", "because",
        "while", "where", "when", "whose", "whether",
        "could", "might", "may", "possibly", "possibly",
        "typically", "usually", "often", "sometimes",
        "provided", "assuming", "given", "unless",
        "already", "also", "else", "otherwise",
        "exactly", "three", "two", "one"
    }

    words = text.split()
    if not words or any(word in forbidden for word in words):
        return False

    # Restrict both sides of the predicate to plain
    # alphabetic noun/attribute phrases. Hyphenated
    # identifiers such as type-Z are supported.
    term = r"[a-z][a-z0-9-]*(?: [a-z][a-z0-9-]*){0,5}"
    patterns = (
        rf"all {term} are {term}",
        rf"all {term} have {term}",
        rf"all {term} use {term}",
        rf"all {term} require {term}",
        rf"every {term} is {term}",
        rf"every {term} has {term}",
        rf"every {term} uses {term}",
        rf"every {term} requires {term}",
    )
    return any(re.fullmatch(pattern, text) for pattern in patterns)





def _existential_conclusion(statement: str) -> bool:
    s = statement.strip().casefold()
    return bool(
        re.match(r"^(some|at least one)\s+\S", s)
        and re.search(
            r"\b(?:are|is|have|has|use|uses|"
            r"require|requires|exist|exists)\b",
            s,
        )
    )


def verify(premises, conclusion) -> Verification:
    """Evaluate existential import in explicit premises.

    Return not_entailed only when the supported form is
    logically refuted by an empty-predicate countermodel.
    Other structures receive abstain.
    """
    if (
        not isinstance(premises, (list, tuple))
        or not 1 <= len(premises) <= 12
        or not isinstance(conclusion, str)
        or not 1 <= len(conclusion) <= 500
    ):
        return Verification(
            "abstain", "Unsupported argument shape",
            "unsupported",
        )

    if not all(
        isinstance(p, str) and 1 <= len(p) <= 500
        for p in premises
    ):
        return Verification(
            "abstain", "Unsupported premise type",
            "unsupported",
        )

    # One full statement per premise prevents accidentally
    # ignoring existential facts after punctuation.
    for premise in premises:
        if (
            len(_sentences(premise) or []) != 1
            or ";" in premise
            or ":" in premise
        ):
            return Verification(
                "abstain",
                "Compound premise requires deeper analysis",
                "unsupported",
            )

    if (
        len(_sentences(conclusion) or []) != 1
        or ";" in conclusion
        or ":" in conclusion
    ):
        return Verification(
            "abstain",
            "Compound conclusion requires deeper analysis",
            "unsupported",
        )

    if not _existential_conclusion(conclusion):
        return Verification(
            "abstain",
            "Conclusion is outside existential rule",
            "unsupported",
        )

    if not all(_universal_only(p) for p in premises):
        return Verification(
            "abstain",
            "Premises include unsupported or existence-bearing claims",
            "unsupported",
        )

    return Verification(
        "not_entailed",
        (
            "Universal premises describe relationships but "
            "do not assert that any member of the relevant "
            "categories exists. An interpretation with "
            "empty relevant categories satisfies these "
            "premises while falsifying the existential "
            "conclusion."
        ),
        "universal_without_existential_import",
    )
