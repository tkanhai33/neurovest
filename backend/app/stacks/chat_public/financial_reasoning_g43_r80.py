from __future__ import annotations

import re
from dataclasses import dataclass

@dataclass(frozen=True)
class FinancialAnswer:
    kind: str
    message: str

def has(text: str, pattern: str) -> bool:
    return re.search(pattern, text, re.I) is not None

def solve(question: str) -> FinancialAnswer | None:
    if not isinstance(question, str):
        return None
    if not 15 <= len(question) <= 1500:
        return None

    q = question.strip().casefold()

    # Never interpret requests for execution, account
    # operations or personalized advice as a static
    # financial concept explanation.
    if has(
        q,
        r"\b(?:buy\s+now|sell\s+now|place\s+(?:an?\s+)?order|"
        r"execute\s+(?:a\s+)?trade|my\s+(?:account|holdings)|"
        r"recommend\s+(?:a\s+)?stock)\b",
    ):
        return None

    stronger = has(
        q,
        r"\b(?:cad|canadian dollar)\b",
    ) and has(
        q,
        r"\b(?:strengthens?|stronger|appreciates?|"
        r"appreciation)\b",
    )

    usd = has(
        q,
        r"\b(?:usd|u\.s\.\s*dollars?|us\s+dollars?)\b",
    ) or has(
        q,
        r"\b(?:us|u\.s\.)\s+"
        r"(?:components?|parts?|inputs?|materials?)\b",
    )

    # Currency effects: these are separate mechanisms.
    # Do not equate foreign-revenue translation with
    # competitiveness or with total profit.
    if stronger and usd:
        imports = has(
            q,
            r"\b(?:imports?|importing|components?|"
            r"raw\s+materials?)\b",
        )
        exports = has(
            q,
            r"\b(?:exports?|exporter|exporting|"
            r"finished\s+goods|foreign\s+sales)\b",
        )

        if imports and exports:
            return FinancialAnswer(
                "cad_import_export",
                "When CAD appreciates against USD, a fixed "
                "USD purchase price costs fewer Canadian dollars, "
                "so USD-denominated imported components become "
                "cheaper in CAD. Conversely, a fixed USD export "
                "sale converts into fewer Canadian dollars of "
                "revenue, not more. If the exporter raises its "
                "USD prices to protect its CAD margins, buyers "
                "may face higher prices and demand could weaken. "
                "If USD selling prices remain unchanged, buyers "
                "do not automatically pay more USD. The net "
                "profit effect depends on the relative import "
                "and export exposures, operating costs, pricing "
                "power, volumes and currency hedging.",
            )

        if exports and has(
            q,
            r"\b(?:revenues?|receipts?|"
            r"competitiv\w*|selling\s+price)\b",
        ):
            return FinancialAnswer(
                "cad_export",
                "With CAD appreciating against USD, an "
                "unchanged USD selling price converts into "
                "fewer CAD of revenue per unit. The foreign "
                "buyer's USD price does not rise automatically, "
                "so price competitiveness does not change "
                "solely from that unchanged USD sticker price. "
                "Raising the USD price to protect CAD revenue "
                "could reduce competitiveness. Profit effects "
                "also depend on costs, sales volume, pricing "
                "power, and any USD-denominated inputs or "
                "currency hedging.",
            )

    rrsp = has(q, r"\brrsp\b")
    tfsa = has(q, r"\btfsa\b")

    if rrsp and tfsa and has(
        q,
        r"\b(?:contribut\w*|tax\w*|deduct\w*|"
        r"withdraw\w*|compare)\b",
    ):
        return FinancialAnswer(
            "tfsa_rrsp_tax",
            "TFSA contributions are not deductible from "
            "Canadian taxable income, and qualifying TFSA "
            "withdrawals are generally tax-free. Eligible "
            "RRSP contributions may be deducted subject to "
            "the applicable deduction limit and other CRA "
            "rules. RRSP withdrawals are generally taxable "
            "as income. Contribution room, overcontributions "
            "and withdrawal-related rules matter for both "
            "accounts. Check CRA records and current guidance "
            "for personal limits; no annual dollar limit is "
            "assumed here.",
        )

    if rrsp and has(q, r"\bjanuary\b") and has(
        q,
        r"\b(?:previous|prior|preceding|last)\b",
    ) and has(
        q,
        r"\b(?:tax\s+year|return|deduct\w*|"
        r"first[\s-]*60[\s-]*days)\b",
    ):
        return FinancialAnswer(
            "rrsp_first_60",
            "Generally, an RRSP contribution made in January "
            "falls within the first 60 days of the calendar "
            "year and may be eligible for deduction on the "
            "previous tax year's return. A contribution in "
            "that period can instead be carried forward "
            "for deduction in a later eligible year; "
            "contributing and claiming a deduction are "
            "not the same decision. Available RRSP "
            "contribution room, the deduction limit and "
            "other CRA rules still apply. Verify the "
            "specific year's first-60-days deadline "
            "and personal limits with the Canada Revenue "
            "Agency. The deadline is generally in early "
            "March, not automatically early February.",
        )

    return None
