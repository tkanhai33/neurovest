"""NeuroVest G43-R67: conservative final-answer factual integrity.

Does not claim to prove correctness. Uses scoped known-rule contradictions,
unsupported currency-of-information claims, and explicit fresh-source state.
No model calls, network access, database access, or trading operations.
"""
from __future__ import annotations
import re
from dataclasses import dataclass

@dataclass(frozen=True)
class ClaimFinding:
    code: str
    reason: str
    severity: str = 'critical'

@dataclass(frozen=True)
class ClaimDecision:
    answer: str
    findings: tuple[ClaimFinding, ...]
    changed: bool

CURRENT = re.compile(r'\b(?:current|latest|today|this year|20(?:2[6-9]|3\d))\b', re.I)
FINANCE = re.compile(r'\b(?:TFSA|RRSP|CRA|tax(?:es|ation)?|contribution room|contribution limit|tax bracket)\b', re.I)
NUMBER = re.compile(r'(?:\$\s*\d|\b\d+(?:\.\d+)?\s*%|\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}\b)', re.I)
NEGATES = re.compile(r'\b(?:no|not|never|incorrect|false|isn.t|is not|rather than|instead of)\b', re.I)


def _sentences(answer: str) -> list[str]:
    # Only evaluate small local segments to avoid incorrectly combining opposing clauses.
    return [piece.strip() for piece in re.split(r'(?<=[.!?])\s+|\n+', answer) if piece.strip()]


def assess(question: str, answer: str, *, fresh_official_evidence: bool = False,
           protected_route: bool = False) -> ClaimDecision:
    if not isinstance(answer, str) or not answer.strip():
        return ClaimDecision(answer if isinstance(answer, str) else '', (), False)
    if protected_route or not isinstance(question, str):
        return ClaimDecision(answer, (), False)
    if not FINANCE.search(question):
        return ClaimDecision(answer, (), False)

    issues = []
    segments = _sentences(answer)
    qtfsa = bool(re.search(r'\bTFSA\b', question, re.I))
    qrrsp = bool(re.search(r'\bRRSP\b', question, re.I))

    # These statements contradict established account mechanics; reference material
    # exists in R64, but we do not infer that any page was fetched live.
    for part in segments:
        p = part.casefold()
        if qtfsa and re.search(r'\b(?:tfsa\s+)?(?:original\s+)?contributions?\s+(?:are|is)\s+(?:generally\s+)?taxable\b', p) and not NEGATES.search(p):
            issues.append(ClaimFinding('tfsa_contribution_tax_claim', 'TFSA contribution principal is not generally taxed upon normal withdrawal'))
        if qtfsa and re.search(r'\btfsa\s+(?:contributions?|deposits?)\s+(?:are|is)\s+(?:tax[- ]?)?deductible\b', p) and not NEGATES.search(p):
            issues.append(ClaimFinding('tfsa_deduction_claim', 'TFSA deposits are not income-tax deductible'))
        if qrrsp and re.search(r'\b(?:rrif|rrif\s+payments?|annuit(?:y|ies))\b.{0,95}\b(?:tax[- ]?free|not taxable)\b', p):
            issues.append(ClaimFinding('rrif_tax_exemption_claim', 'RRIF payments are generally taxable; the asserted exemption is unsupported'))
        if qtfsa and re.search(r'\b(?:only\s+)?(?:the\s+)?original\s+contributions?\b.{0,35}\b(?:taxable|taxed)\b', p) and not NEGATES.search(p):
            issues.append(ClaimFinding('tfsa_principal_tax_claim', 'TFSA contribution principal is not ordinarily taxable when withdrawn'))
        if qrrsp and 'june 30' in p and re.search(r'\b(?:tax[- ]?filing|filing|contribution)\b', p) and not re.search(r'\b(?:not|incorrect|false|wrong|misleading)\b', p):
            issues.append(ClaimFinding('unsupported_june_deadline', 'June 30 is not the standard RRSP prior-year contribution deadline or standard individual filing deadline'))

    # Explicitly unsupported live/source claims. A static R64 catalogue is not fresh evidence.
    if CURRENT.search(question) and not fresh_official_evidence:
        if re.search(r'\b(?:verified|confirmed|checked)\b.{0,55}\b(?:CRA|official|current|government)\b', answer, re.I | re.S):
            issues.append(ClaimFinding('unsubstantiated_live_verification', 'Generated text claims current verification without fresh official evidence'))
        # Numbers in a request are not a reason to reject, but asserting a new current
        # financial limit/rate/date without a fresh source must be qualified.
        for part in segments:
            if (NUMBER.search(part) and re.search(r'\b(?:limit|deadline|contribution room|tax rate|tax bracket)\b', part, re.I)
                    and re.search(r'\b(?:is|was|equals?|stands at|set at)\b', part, re.I)
                    and not re.search(r'\b(?:cannot verify|can.t verify|unverified|estimate|hypothetical|example|if|might|may|approximately)\b', part, re.I)):
                issues.append(ClaimFinding('unverified_current_numeric_claim', 'A current financial figure/date requires a fresh authoritative source'))
                break

    if not issues:
        return ClaimDecision(answer, (), False)
    unique = tuple({x.code: x for x in issues}.values())
    # Preserve no unsupported specific correction; do not falsely assert live checking.
    safe = ('I can explain the general rule, but I cannot confirm the specific financial '
            'claim in my draft against sufficiently current authoritative evidence. '
            'I should not present that figure, tax treatment, or deadline as verified. '
            'Please check the applicable CRA guidance before relying on it.')
    return ClaimDecision(safe, unique, True)
