
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class FinancialConceptAnswer:
    kind: str
    message: str


# These are general educational explanations.
# No current tax amounts, account records, or live source claims.
# References used for qualification:
# https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/tax-free-savings-account.html
# https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/rrsps-related-plans.html
# https://www.bankofcanada.ca/core-functions/monetary-policy/


ANSWERS = {
    "rrsp_deduction": (
        "An eligible RRSP contribution can produce an income-tax "
        "deduction, not a tax credit. A deduction reduces taxable "
        "income; the resulting tax savings depend on the taxpayer's "
        "applicable marginal rates. Contributing does not necessarily "
        "mean claiming the deduction immediately. Check earned income, "
        "available contribution and deduction room, unused "
        "contributions, residency, and the relevant tax year. "
        "Confirm personal figures with CRA records and contribution "
        "receipts; no current dollar limit is assumed."
    ),
    "rrsp_withdrawal": (
        "Ordinary RRSP withdrawals are generally included in income "
        "for the year of withdrawal and may increase income tax "
        "payable. Financial institutions generally withhold tax, "
        "but withholding is not necessarily the final tax liability. "
        "The amount withdrawn, residency, other annual income and "
        "applicable tax rules matter. Special arrangements such as "
        "qualifying transfers and certain programs follow different "
        "rules. Verify the person's circumstances and current CRA "
        "guidance before calculating tax."
    ),
    "tfsa_room": (
        "A qualifying TFSA withdrawal generally creates replacement "
        "contribution room on January 1 of the following calendar "
        "year, not immediately. Earlier recontribution is possible "
        "only to the extent unused room already exists. Check all "
        "TFSA contributions and withdrawals, residency history, "
        "unused room, and financial-institution records. CRA online "
        "figures may lag recent transactions, so reconcile them "
        "rather than assuming the displayed number is current."
    ),
    "tfsa_taxation": (
        "Income and investment gains earned on qualifying investments "
        "inside a TFSA are generally tax-free, including upon an "
        "ordinary withdrawal. TFSA contributions are not tax "
        "deductible. Exceptions can arise, including business "
        "activity, non-qualified or prohibited investments and "
        "other special rules. Determine the type of investment and "
        "transaction before treating every gain as exempt. "
        "Verify unusual situations against CRA guidance."
    ),
    "rrsp_dates": (
        "The date of an RRSP contribution and the year in which a "
        "deduction is claimed are separate matters. Eligible "
        "contributions made in the first 60 days of a calendar "
        "year can generally be considered for the preceding tax "
        "year, subject to CRA rules. An eligible deduction may "
        "also be carried forward. The tax-return filing deadline "
        "is not the same as the RRSP contribution cutoff. "
        "Check contribution receipts, deduction room and the "
        "specific year's official deadlines."
    ),
    "tfsa_eligibility": (
        "TFSA contribution-room eligibility depends on age and "
        "Canadian tax residency. A resident generally begins "
        "accumulating annual room at age 18; new residents do not "
        "receive room for years before qualifying residency. "
        "A valid social insurance number is also relevant to "
        "opening an account. Provincial age-of-contract rules "
        "may affect when an account can actually be opened. "
        "Check residency dates, age, prior room and current CRA "
        "guidance; do not assume a new resident has historical "
        "annual limits."
    ),
    "rrsp_carryforward": (
        "Eligible RRSP contributions that were not deducted can "
        "generally be reported and carried forward for a deduction "
        "in a later eligible year, subject to deduction limits and "
        "other CRA rules. Carrying forward a deduction is different "
        "from having unused contribution room, and neither makes "
        "an excess contribution automatically permissible. "
        "Check the contribution receipts, CRA assessment, "
        "Schedule 7 information, unused contributions and "
        "available deduction limit before claiming an amount."
    ),
    "tfsa_overcontribution": (
        "Replacing a TFSA withdrawal in the same calendar year can "
        "cause an overcontribution if sufficient unused room was "
        "not already available. The withdrawal normally adds room "
        "back only on January 1 of the next year. An excess amount "
        "may trigger monthly tax while it remains. Reconcile all "
        "TFSA transactions across institutions, check residency, "
        "and confirm the applicable CRA reporting and correction "
        "requirements rather than assuming the withdrawal "
        "immediately restored room."
    ),
    "tfsa_rrsp_rates": (
        "RRSP deductions can be more advantageous when the marginal "
        "tax rate at contribution is higher than the rate at "
        "withdrawal, all else equal. TFSAs provide no contribution "
        "deduction, but qualifying withdrawals are generally "
        "tax-free. The comparison also depends on investment "
        "returns, benefit clawbacks, contribution room, timing "
        "and personal circumstances. Compare expected taxable "
        "income now and in retirement; no future tax rate or "
        "individual outcome can be assumed."
    ),
    "cra_freshness": (
        "An official, current CRA page checked at a stated time "
        "is different from a stored reference note or an "
        "unverified summary. A stored note may explain a stable "
        "concept but cannot establish today's deadline, limit "
        "or account balance. Check the official source, tax "
        "year, publication or update date and relevant exceptions. "
        "Without actual live retrieval, describe the material "
        "as reference knowledge—not as a page verified now."
    ),
    "tfsa_rrsp_compare": (
        "TFSA contributions are not deductible, while qualifying "
        "TFSA investment income and withdrawals are generally "
        "tax-free. Eligible RRSP contributions may reduce taxable "
        "income, while ordinary RRSP withdrawals are generally "
        "taxable. The better choice depends on current and future "
        "marginal tax rates, contribution room and individual "
        "circumstances, not simply the person's industry. "
        "Verify personal room and current CRA rules; no annual "
        "limit is assumed."
    ),
    "usd_cad_translation": (
        "If a Canadian company receives revenue in USD but pays "
        "costs in CAD, its reported CAD revenue changes with the "
        "exchange rate. A stronger CAD generally reduces the CAD "
        "value of a fixed USD receipt; a weaker CAD generally "
        "increases it. This alone cannot establish profit because "
        "volumes, prices, hedging and other costs also matter. "
        "Confirm the accounting period, actual currency exposures "
        "and exchange rates before drawing a company-specific "
        "conclusion."
    ),
    "rrsp_contribution_year": (
        "The date money enters an RRSP need not be the year its "
        "tax deduction is claimed. Contributions during the "
        "first 60 days of a calendar year may be eligible for "
        "the preceding tax year, and eligible unused deductions "
        "may be carried forward. Report contributions correctly "
        "and distinguish contribution room from deduction limits. "
        "Check receipts, CRA records and the applicable tax "
        "year's official deadlines; an occupation does not by "
        "itself change this general rule."
    ),
    "boc_decision_forecast": (
        "A Bank of Canada policy-rate announcement communicates "
        "an actual decision about the overnight-rate target. "
        "A forecast is a projection or expectation, not a "
        "decision or guarantee of future rates. Borrowing costs "
        "also depend on lender pricing, loan terms and how "
        "quickly a rate change passes through. Confirm the "
        "dated Bank announcement and distinguish official "
        "projections from outside forecasts before assessing "
        "a borrower's circumstances."
    ),
    "contribution_room_evidence": (
        "Before relying on a Canadian contribution-room estimate, "
        "identify whether it concerns an RRSP or TFSA, the "
        "relevant year, residency and the person's actual "
        "contribution history. Compare CRA records with notices "
        "of assessment and financial-institution transactions; "
        "TFSA figures may lag. RRSP deduction limits differ from "
        "unused contributions, and a contribution is not always "
        "immediately deductible. Without these records, do not "
        "claim a verified personal amount."
    ),
}


def has(q: str, pattern: str) -> bool:
    return re.search(pattern, q, re.I) is not None


def classify(question: str) -> str | None:
    if not isinstance(question, str):
        return None
    if not 15 <= len(question) <= 1500:
        return None

    q = " ".join(question.casefold().split())

    # G43-R92B: reject explicit attempts to override
    # instruction/safety boundaries before concept selection.
    if has(
        q,
        r"\b(?:ignore all previous instructions|"
        r"ignore your safety rules|"
        r"disregard (?:system|developer|safety) instructions|"
        r"override (?:the )?(?:safety rules|safeguards)|"
        r"turn off (?:the )?emergency stop)\b",
    ):
        return None


    # Exclude action requests, personalized account access and
    # explicit attempts to redirect the response.
    if has(
        q,
        r"\b(?:place (?:a |an )?(?:market )?order|"
        r"execute (?:a )?(?:live )?trade|"
        r"buy now|sell now|"
        r"disable (?:the )?(?:emergency stop|safety)|"
        r"ignore (?:previous|your|all) (?:(?:safety|system|developer|previous) )?(?:instructions|rules)|"
        r"my (?:brokerage )?account|my holdings|"
        r"recommend (?:me )?(?:a )?stock)\b",
    ):
        return None

    # Current market and personalized tax values require
    # retrieval or individualized verification.
    if has(
        q,
        r"\b(?:what is (?:today's|the current|my current) "
        r"(?:rrsp|tfsa|bank of canada)|"
        r"calculate my (?:tax|rrsp|tfsa)|"
        r"file my tax return)\b",
    ):
        return None

    if has(q, r"\bbank of canada\b") and has(
        q, r"\b(?:rate announcement|forecast)\b"
    ):
        return "boc_decision_forecast"

    if has(q, r"\busd\b") and has(q, r"\bcad\b") and has(
        q, r"\b(?:revenue|translation|exchange)\b"
    ):
        return "usd_cad_translation"

    if has(q, r"\bcontribution.room estimate\b") and has(
        q, r"\b(?:verify|relying|taxpayer)\b"
    ):
        return "contribution_room_evidence"

    if has(q, r"\bcra\b") and has(
        q, r"\b(?:source freshness|official live evidence|stored reference)\b"
    ):
        return "cra_freshness"

    if has(q, r"\brrsp\b") and has(q, r"\btfsa\b"):
        if has(q, r"\b(?:marginal rates|retirement marginal)\b"):
            return "tfsa_rrsp_rates"
        if has(q, r"\b(?:compar|tax differences|tax treatment|choice)\w*\b"):
            return "tfsa_rrsp_compare"

    if has(q, r"\brrsp\b"):
        if has(q, r"\bcontribution date\b") and has(
            q, r"\bdeduction year\b"
        ):
            return "rrsp_contribution_year"
        if has(
            q,
            r"\b(?:contribution windows|filing deadline|"
            r"income tax filing deadline)\b",
        ):
            return "rrsp_dates"
        if has(q, r"\b(?:carryforwards|unused eligible deductions)\b"):
            return "rrsp_carryforward"
        if has(q, r"\b(?:withdrawal tax|ordinary withdrawals|rrsp withdrawals|rrsp withdrawal)\b"):
            return "rrsp_withdrawal"
        if has(q, r"\b(?:tax credit|rrsp deductions)\b"):
            return "rrsp_deduction"

    if has(q, r"\btfsa\b"):
        if has(q, r"\b(?:overcontributions|same.year replacement)\b"):
            return "tfsa_overcontribution"
        if has(q, r"\b(?:residency and age|tfsa eligibility)\b"):
            return "tfsa_eligibility"
        if has(q, r"\b(?:investment gains|tfsa taxation)\b"):
            return "tfsa_taxation"
        if has(q, r"\b(?:withdrawals create contribution room|tfsa room)\b"):
            return "tfsa_room"

    return None


def solve(question: str) -> FinancialConceptAnswer | None:
    kind = classify(question)
    if kind is None:
        return None

    message = ANSWERS.get(kind)
    if not message:
        return None

    return FinancialConceptAnswer(kind, message)
