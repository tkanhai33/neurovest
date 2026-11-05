
from __future__ import annotations

import re

HEADER = re.compile(
    r"(?m)^Premises:\s*$"
)
CONCLUSION = re.compile(
    r"(?m)^Conclusion:\s*$"
)

ALLOWED_ENDINGS = {
    "",
    "Does the conclusion necessarily follow?",
    "Does this conclusion necessarily follow?",
    "Does it necessarily follow?",
    "Is the inference valid?",
}

def extract(message):
    if not isinstance(message, str):
        return None
    if not 20 <= len(message) <= 6000:
        return None
    if message.count("Premises:") != 1:
        return None
    if message.count("Conclusion:") != 1:
        return None
    if "```" in message:
        return None

    headers = list(HEADER.finditer(message))
    conclusions = list(CONCLUSION.finditer(message))
    if len(headers) != 1 or len(conclusions) != 1:
        return None

    a = headers[0]
    b = conclusions[0]
    if a.end() >= b.start():
        return None

    preamble = message[:a.start()].strip()

    # Reject embedded meta-instructions and user-defined
    # exceptions before relying on exact premise parsing.
    allowed_preambles = {
        "",
        "Evaluate this deductive argument.",
        "Evaluate this argument using only the premises.",
        "Evaluate the following deductive argument.",
    }
    if preamble not in allowed_preambles:
        return None

    body = message[a.end():b.start()].strip()
    premises = [
        line.strip()
        for line in body.splitlines()
        if line.strip()
    ]
    if not 1 <= len(premises) <= 12:
        return None

    tail_lines = [
        line.strip()
        for line in message[b.end():].splitlines()
        if line.strip()
    ]
    if not 1 <= len(tail_lines) <= 2:
        return None

    conclusion = tail_lines[0]
    ending = tail_lines[1] if len(tail_lines) == 2 else ""

    if ending not in ALLOWED_ENDINGS:
        return None

    if any(len(p) > 500 for p in premises):
        return None
    if not 1 <= len(conclusion) <= 500:
        return None

    return premises, conclusion

def evaluate(message, verifier):
    parsed = extract(message)
    if parsed is None:
        return None

    premises, conclusion = parsed
    result = verifier(premises, conclusion)

    if result.status != "not_entailed":
        return None

    return {
        "status": result.status,
        "rule": result.rule,
        "reason": result.reason,
        "premises": premises,
        "conclusion": conclusion,
    }

def guidance(evidence):
    if not isinstance(evidence, dict):
        return ""

    if evidence.get("rule") != "universal_without_existential_import":
        return ""

    return (
        "VERIFIED DEDUCTIVE OBSERVATION:\n"
        "A restricted deterministic check established that "
        "the conclusion is NOT_ENTAILED by the supplied premises. "
        "These premises are universal statements and do not "
        "establish that members of the relevant classes exist. "
        "An empty-class interpretation is a counterexample. "
        "Explain this result naturally and concisely. "
        "Do not claim to have run a general-purpose theorem prover."
    )
