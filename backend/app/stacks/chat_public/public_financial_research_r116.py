"""R116 public financial research. Read-only, no account tools."""
import asyncio
import math
import re
from datetime import datetime, timezone

PREFIX = "R116_PUBLIC_RESEARCH_VERIFIED\n"

TICKERS = re.compile(r"\b[A-Z]{2,5}\b")
COMPARE = re.compile(r"\b(compare|versus|vs\.?)\b", re.I)
CATALYST = re.compile(
    r"\b(why|what caused|what drove|reason|catalyst)\b",
    re.I,
)
MOVEMENT = re.compile(
    r"\b(increase|increased|jump|jumped|surge|surged|"
    r"gain|gained|rise|rose|rally|rallied|fell|"
    r"drop|dropped|decline|declined)\b",
    re.I,
)
MULTIDAY = re.compile(
    r"\b(?:past|last|previous)\s+([2-9])\s+days?\b",
    re.I,
)
GAINERS = re.compile(
    r"\b(gainers?|gained|biggest gains?|"
    r"best performing|top performing)\b",
    re.I,
)
OWNER = re.compile(
    r"\b(my|mine|saved|watchlist|portfolio|holdings|"
    r"research universe)\b", re.I,
)
ACTION = re.compile(
    r"\b(buy|sell|purchase|short|execute|submit|"
    r"place|cancel|liquidate)\b.{0,80}"
    r"\b(shares?|orders?|trades?|positions?|"
    r"contracts?|lots?)\b",
    re.I,
)

STOPWORDS = {
    "THE", "AND", "FOR", "WHY", "HOW", "WHAT",
    "WITH", "FROM", "LAST", "PAST", "DAYS",
    "DAY", "STOCK", "STOCKS", "THOSE",
    # NEUROVEST_G43_R97_CANADIAN_FINANCE_ACRONYMS
    # Tax/account acronyms are not stock tickers by default.
    "RRSP", "TFSA", "CRA", "FHSA", "RESP",
    "CPP", "OAS", "GST", "HST", "SIN",
}


def route(message):
    if not isinstance(message, str):
        return None

    text = message.strip()
    if not text or text.startswith("/"):
        return None
    if OWNER.search(text) or ACTION.search(text):
        return None

    # Biology comparisons must remain ordinary conversation.
    if re.search(
        r"\b(?:DNA|RNA|genetics|chromosome|nucleotide|photosynthesis)\b",
        text, re.I
    ) and not re.search(
        r"\b(?:stock|stocks|ticker|tickers|shares|equity|market)\b",
        text, re.I
    ):
        return None

    # G41_R116_NETWORK_PROTOCOL_DISAMBIGUATION
    # Technical protocol comparisons must not become stock research.
    # Explicit financial questions continue through the stock route.
    protocol_terms = set(re.findall(
        r"\b(?:TCP|UDP|HTTP|HTTPS|TLS|DNS)\b",
        text, re.I,
    ))
    network_context = bool(re.search(
        r"\b(?:network(?:ing)?|protocols?|transport|"
        r"internet|packets?|connections?|ports?|"
        r"latency|reliability|web|tcp/ip)\b",
        text, re.I,
    ))
    finance_context = bool(re.search(
        r"\b(?:stock|stocks|tickers?|shares?|equity|"
        r"quote|market cap|nasdaq|nyse|tsx|"
        r"financial|market price|share price|"
        r"invest(?:ment|ing)?|trading)\b",
        text, re.I,
    ))
    if (
        not finance_context
        and (
            (len(protocol_terms) >= 2 and COMPARE.search(text))
            or (protocol_terms and network_context)
        )
    ):
        return None

    if COMPARE.search(text):
        symbols = list(dict.fromkeys(
            x for x in re.findall(
                r"(?<![A-Za-z])[A-Z]{2,5}(?![A-Za-z])", text
            )
            if x not in STOPWORDS
            and x not in {"DNA", "RNA", "HTTP", "SQL", "HRS"}
        ))
        if 2 <= len(symbols) <= 5:
            return {"kind": "compare", "symbols": symbols}

    if CATALYST.search(text) and MOVEMENT.search(text):
        if re.search(r"\bBiohaven\b", text, re.I):
            return {"kind": "catalyst", "symbol": "BHVN"}
        symbols = [
            x for x in re.findall(
                r"(?<![A-Za-z])[A-Z]{2,5}(?![A-Za-z])", text
            )
            if x not in STOPWORDS
            and x not in {"WHY", "DID", "HRS"}
        ]
        if len(symbols) == 1:
            return {"kind": "catalyst", "symbol": symbols[0]}

    period = re.search(
        r"\b(?:past|last|previous)\s+([2-9])\s+"
        r"(?:trading\s+)?(?:days?|sessions?)\b",
        text, re.I
    )
    if period and re.search(
        r"\b(?:gain|gained|gainers|perform|performing|"
        r"highest|biggest|top|best)\b", text, re.I
    ) and re.search(
        r"\b(?:stocks?|symbols?|markets?|equities|"
        r"gainers?|sessions?)\b", text, re.I
    ):
        return {"kind": "multiday", "days": int(period.group(1))}

    return None

def finite(value):
    try:
        v = float(value)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError, OverflowError):
        return None

def compare_sync(symbols):
    import yfinance as yf
    lines = [
        "Public stock comparison — latest available daily adjusted closes",
        "Retrieved: " + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "",
    ]
    results = []
    for symbol in symbols:
        try:
            bars = yf.Ticker(symbol).history(
                period="10d", interval="1d", auto_adjust=True
            )
            if bars is None or "Close" not in bars:
                raise ValueError("missing historical close")
            closes = bars["Close"].dropna()
            if len(closes) < 2:
                raise ValueError("insufficient daily closes")
            latest = finite(closes.iloc[-1])
            previous = finite(closes.iloc[-2])
            if latest is None or previous is None or previous <= 0 or latest <= 0:
                raise ValueError("invalid close")
            latest_date = str(closes.index[-1].date())
            previous_date = str(closes.index[-2].date())
            change = (latest / previous - 1) * 100
            results.append((symbol, change))
            lines.append(
                f"{symbol}: {latest:.2f} (adjusted close, currency not verified) | "
                f"Previous: {previous:.2f} | Change: {change:+.2f}% "
                f"| {previous_date} to {latest_date}"
            )
        except Exception:
            lines.append(symbol + ": daily price comparison unavailable")
    if not results:
        return None
    if len(results) > 1:
        winner = max(results, key=lambda item: item[1])
        lines.append(
            f"Highest daily return among successfully compared symbols: "
            f"{winner[0]} ({winner[1]:+.2f}%)."
        )
    lines += [
        "",
        "Source: Yahoo Finance via yfinance adjusted daily closing prices.",
        "This compares daily closes, not live quotes or intraday price movement.",
        "Currencies were not independently verified; raw cross-currency prices "
        "must not be interpreted as directly comparable company values.",
        "The comparison covers only the requested symbols with usable history.",
        "No saved research universe, account modification, or trading operation was used.",
    ]
    return "\n".join(lines)


def catalyst_sync(symbol):
    return (
        f"I cannot verify the specific catalyst behind {symbol}'s "
        f"recent price movement using available dated news evidence. "
        f"Price changes alone do not establish causation. "
        f"No specific catalyst has been confirmed by this lookup."
    )

def multiday_sync(days):
    import yfinance as yf

    screen = yf.screen("day_gainers", count=10)
    if not isinstance(screen, dict):
        return None
    quotes = screen.get("quotes")
    if not isinstance(quotes, list):
        return None

    symbols = []
    for item in quotes:
        if isinstance(item, dict):
            sym = item.get("symbol")
            if (
                isinstance(sym, str)
                and re.fullmatch(r"[A-Z]{1,5}", sym)
                and sym not in symbols
            ):
                symbols.append(sym)

    results = []
    for symbol in symbols[:10]:
        try:
            frame = yf.Ticker(symbol).history(
                period="1mo",
                interval="1d",
                auto_adjust=True,
            )
            closes = frame["Close"].dropna()
            if len(closes) <= days:
                continue
            start = finite(closes.iloc[-(days + 1)])
            end = finite(closes.iloc[-1])
            if start is None or end is None or start <= 0:
                continue
            start_date = str(closes.index[-(days + 1)].date())
            end_date = str(closes.index[-1].date())
            results.append((
                symbol, (end / start - 1) * 100,
                start_date, end_date,
            ))
        except Exception:
            continue

    if not results:
        return None

    results.sort(key=lambda x: x[1], reverse=True)
    lines = [
        f"Performance across {days} completed daily-bar intervals",
        "Candidate universe: Yahoo Finance day-gainers screen "
        f"({len(symbols)} symbols identified; "
        f"{len(results)} with usable history).",
        "",
    ]
    for i, (symbol, change, start, end) in enumerate(
        results[:10], 1
    ):
        lines.append(
            f"{i}. {symbol}: {change:+.2f}% "
            f"({start} to {end})"
        )

    lines.extend([
        "",
        "Highest gain within this screened candidate set: "
        + results[0][0],
        "Source: Yahoo Finance via yfinance daily adjusted prices.",
        "This is NOT an exhaustive market-wide ranking.",
        "Daily-bar intervals are trading sessions, not "
        "necessarily calendar days or a rolling-hour window.",
        "Symbols missing historical data were excluded.",
    ])
    return "\n".join(lines)

async def answer(message, *, executor=None):
    decision = route(message)
    if decision is None:
        return None

    kind = decision["kind"]
    task = {
        "compare": (
            compare_sync,
            (decision.get("symbols"),),
        ),
        "catalyst": (
            catalyst_sync,
            (decision.get("symbol"),),
        ),
        "multiday": (
            multiday_sync,
            (decision.get("days"),),
        ),
    }[kind]

    try:
        if executor is not None:
            result = await asyncio.to_thread(
                executor, kind, decision
            )
        else:
            result = await asyncio.wait_for(
                asyncio.to_thread(task[0], *task[1]),
                timeout=15,
            )
    except Exception:
        result = None

    if not isinstance(result, str) or not result.strip():
        result = (
            "I recognized this public financial research "
            "request, but the provider did not supply enough "
            "reliable evidence to answer it. I will not invent "
            "prices, rankings, or reasons for price movements."
        )

    return PREFIX + result
