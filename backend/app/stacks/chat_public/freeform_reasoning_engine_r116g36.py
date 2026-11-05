
"""Restricted positive-categorical inference for natural chat.

This is NOT a general theorem prover or natural-language parser.
Returns abstain for forms outside the exact supported grammar.
Does not access model, broker, network or database.
"""
from __future__ import annotations

import re
from collections import deque
from dataclasses import dataclass

@dataclass(frozen=True)
class Finding:
    status: str
    explanation: str
    rule: str

TERM = r"[a-z][a-z0-9-]*(?: [a-z][a-z0-9-]*){0,4}"

FORBIDDEN = {
    "not", "no", "never", "except", "unless", "if",
    "only", "without", "either", "or", "and", "but",
    "although", "however", "existing", "exists",
    "exist", "existence", "possibly", "perhaps", "may",
    "might", "which", "who", "whose", "that", "because",
    "assuming", "given", "provided", "already", "any",
    "most", "few", "many", "exactly", "none", "there",
    "at", "least", "one", "each", "every", "all", "some",
    "is", "are", "has", "have", "fade", "fades", "use",
    "uses", "require", "requires",
}

def safe_term(value):
    return (
        bool(re.fullmatch(TERM, value))
        and not bool(set(value.split()) & FORBIDDEN)
    )

def statement(text):
    if not isinstance(text, str):
        return None

    text = text.strip().casefold().rstrip(".").strip()

    if not 5 <= len(text) <= 220:
        return None

    if re.search(r"[,;:!?()\[\]{}]", text):
        return None

    pattern = (
        rf"(all|every|some) ({TERM}) "
        rf"(are|is|fade|fades|use|uses|"
        rf"require|requires|have|has) ({TERM})"
    )
    match = re.fullmatch(pattern, text)
    if not match:
        return None

    quant, subject, verb, predicate = match.groups()
    if not safe_term(subject) or not safe_term(predicate):
        return None

    # Singular-noun grammar is not yet supported.
    # Reject EVERY rather than assuming an implicit article.
    if quant == "every":
        return None
    if quant in {"all", "some"} and verb == "is":
        return None

    # Ordinary property verbs stay distinct from class membership.
    # No synonym or tense guessing.
    target = (
        predicate if verb in {"are", "is"}
        else verb + " " + predicate
    )
    kind = "some" if quant == "some" else "all"
    return kind, subject, target

def parse(message):
    if not isinstance(message, str):
        return None
    if not 25 <= len(message) <= 1300:
        return None
    if any(x in message for x in ("```", "\n", ";", ":")):
        return None

    match = re.fullmatch(
        r"(.+?)\s+"
        r"(?:does it necessarily follow that|"
        r"does it follow that|"
        r"must it follow that)\s+(.+?)\?",
        message.strip(),
        flags=re.IGNORECASE,
    )

    if not match:
        return None

    premise_text, conclusion_text = match.groups()
    pieces = [p.strip() for p in premise_text.split(".") if p.strip()]

    if len(pieces) != 2:
        return None

    premises = [statement(p) for p in pieces]
    conclusion = statement(conclusion_text)

    if any(p is None for p in premises) or conclusion is None:
        return None
    if conclusion[0] != "some":
        return None

    return premises, conclusion

def closure(start, edges):
    visited = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for target in edges.get(node, ()):
            if target not in visited:
                visited.add(target)
                queue.append(target)
    return visited

def verify(message):
    parsed = parse(message)
    if parsed is None:
        return Finding(
            "abstain",
            "This argument is outside the supported grammar.",
            "unsupported",
        )

    premises, conclusion = parsed
    _, desired_a, desired_b = conclusion

    inclusions = {}
    witnesses = []

    for kind, subject, predicate in premises:
        if kind == "all":
            inclusions.setdefault(subject, set()).add(predicate)
        else:
            # Every existential premise creates its own witness.
            witnesses.append((subject, predicate))

    for left, right in witnesses:
        # Closure must be calculated for this ONE witness.
        facts = closure(left, inclusions) | closure(right, inclusions)

        if desired_a in facts and desired_b in facts:
            return Finding(
                "entailed",
                "An existential premise supplies a witness. "
                "The universal relations establish that the "
                "same witness satisfies the conclusion.",
                "witness_entailment",
            )

    # For this restricted positive fragment, a model can
    # be built from its distinct witness closures.
    return Finding(
        "not_entailed",
        "The premises do not force any single witness "
        "to satisfy both parts of the conclusion.",
        "witness_countermodel",
    )

def authoritative_reply(message):
    finding = verify(message)
    if finding.status == "abstain":
        return None
    if finding.status == "entailed":
        return "Yes, the conclusion necessarily follows. " + finding.explanation
    return "No, the conclusion does not necessarily follow. " + finding.explanation
