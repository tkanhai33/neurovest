"""R115-E read-only market discovery."""
import asyncio
import math
import re
from datetime import datetime, timezone

PREFIX = "R115_MARKET_DISCOVERY_VERIFIED\n"

OWNER = re.compile(
    r"\b(my|mine|saved|watchlist|portfolio|holdings|"
    r"research universe|our universe)\b", re.I
)
EXECUTION = re.compile(
    r"\b(buy|sell|purchase|short|execute|submit|place|"
    r"cancel|close|liquidate)\b.{0,70}"
    r"\b(shares?|stocks?|orders?|trades?|positions?|"
    r"contracts?|lots?)\b|"
    r"\b(place|execute|submit|cancel)\s+"
    r"(?:an?\s+|the\s+)?(?:order|trade)\b", re.I
)
UP = re.compile(
    r"\b(gainers?|winners?|rising|biggest\s+gains?|"
    r"best[ -]performing|top[ -]performing|performed\s+best|performing\s+best|most\s+up|"
    r"highest\s+returns?)\b", re.I
)
DOWN = re.compile(
    r"\b(losers?|decliners?|falling|biggest\s+losses?|"
    r"worst[ -]performing|bottom[ -]performing|performed\s+worst|performing\s+worst|"
    r"most\s+down|lowest\s+returns?)\b", re.I
)
MARKET = re.compile(
    r"\b(stocks?|shares?|equities|companies|tickers?|"
    r"market|sectors?|etfs?)\b", re.I
)
BARE = re.compile(
    r"^(?:(?:show|find|list|give me|what are|who are)\s+"
    r"(?:me\s+|the\s+)?)?(?:top|biggest)\s+"
    r"(?:stock\s+|market\s+)?(?:gainers|losers)"
    r"(?:\s+(?:today|this week|yesterday|now))?\??$", re.I
)
ROLLING = re.compile(
    r"\b(?:past|last|previous)\s+24\s*(?:hours?|hrs?)\b", re.I
)

def classify_market_discovery(message):
    if not isinstance(message, str):
        return None
    text = message.strip()
    if not text or text.startswith("/") or EXECUTION.search(text):
        return None
    if OWNER.search(text):
        return None
    if not (MARKET.search(text) or BARE.fullmatch(text)):
        return None
    up, down = bool(UP.search(text)), bool(DOWN.search(text))
    if up == down:
        return None
    return {
        "route": "market_discovery",
        "direction": "gainers" if up else "losers",
        "scope": (
            "sector" if re.search(r"\bsectors?\b", text, re.I)
            else "etf" if re.search(r"\betfs?\b", text, re.I)
            else "equity"
        ),
        "region": (
            "canada" if re.search(r"\b(canada|canadian|tsx|ts\s*x)\b", text, re.I)
            else "us" if re.search(r"\b(us|u\.s\.|united states|american)\b", text, re.I)
            else "unspecified"
        ),
        "rolling_24h_requested": bool(ROLLING.search(text)),
    }

def _screen(name):
    import yfinance as yf
    if not callable(getattr(yf, "screen", None)):
        raise RuntimeError("yfinance_screen_unavailable")
    return yf.screen(name, count=15)

def _number(value):
    if isinstance(value, bool):
        return None
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return value if math.isfinite(value) else None

def render_screen(decision, response, now=None):
    now = now or datetime.now(timezone.utc)
    if not isinstance(response, dict):
        return None
    try:
        if isinstance(response.get("quotes"), list):
            quotes = response["quotes"]
        else:
            quotes = response["finance"]["result"][0]["quotes"]
    except (KeyError, IndexError, TypeError, AttributeError):
        return None
    if not isinstance(quotes, list):
        return None

    direction = decision["direction"]
    records = []
    seen = set()
    for q in quotes:
        if not isinstance(q, dict):
            continue
        symbol = q.get("symbol")
        change = _number(q.get("regularMarketChangePercent"))
        if (
            not isinstance(symbol, str)
            or not re.fullmatch(r"[A-Za-z0-9.^-]{1,16}", symbol)
            or symbol.upper() in seen
            or change is None
        ):
            continue
        if direction == "gainers" and change <= 0:
            continue
        if direction == "losers" and change >= 0:
            continue
        seen.add(symbol.upper())
        records.append((symbol.upper(), change, q))

    records.sort(key=lambda r: r[1], reverse=direction == "gainers")
    if not records:
        return None

    label = "gainers" if direction == "gainers" else "losers"
    lines = [
        "Yahoo Finance screened U.S. equity day " + label,
        "Retrieved: " + now.strftime("%Y-%m-%d %H:%M UTC"),
        "",
    ]
    for index, (symbol, change, q) in enumerate(records[:5], 1):
        name = str(q.get("shortName") or q.get("longName") or symbol)
        name = re.sub(r"[\r\n|]+", " ", name).strip()[:75]
        price = _number(q.get("regularMarketPrice"))
        currency = str(q.get("currency") or "").upper()
        line = f"{index}. {symbol} — {name}: {change:+.2f}%"
        if price is not None and re.fullmatch(r"[A-Z]{3}", currency):
            line += f" | {price:.2f} {currency}"
        timestamp = _number(q.get("regularMarketTime"))
        if timestamp is not None and 946684800 <= timestamp <= now.timestamp() + 300:
            line += " | Quote: " + datetime.fromtimestamp(
                timestamp, timezone.utc
            ).strftime("%Y-%m-%d %H:%M UTC")
        lines.append(line)

    lines += [
        "",
        "Source: Yahoo Finance via yfinance predefined day_" + label + " screen.",
        "Coverage: filtered U.S. equities; not an exhaustive global or all-U.S.-stock ranking.",
        "Screen percentage changes are provider-reported daily/session changes.",
        "Data may be delayed. Retrieval time does not prove exchange-real-time pricing.",
        "No account holdings, saved research universe, or broker orders were used.",
    ]
    if decision["rolling_24h_requested"]:
        lines.append(
            "Important: this is not a verified rolling 24-hour ranking. "
            "The requested 24-hour comparison is unavailable from this screen."
        )
    return "\n".join(lines)

async def market_discovery_evidence(message, *, fetcher=None):
    decision = classify_market_discovery(message)
    if decision is None:
        return None

    def verified(text):
        return PREFIX + text

    if decision["scope"] != "equity":
        return verified(
            "I recognized a " + decision["scope"] +
            " performance request, but the available U.S. equity screener "
            "cannot verify that ranking. I will not substitute a stock list."
        )
    if decision["region"] == "canada":
        return verified(
            "I recognized a Canadian market-performance request, but "
            "this U.S. equity screen cannot verify Canadian gainers or losers. "
            "I will not substitute U.S. rankings."
        )

    name = "day_" + decision["direction"]
    try:
        response = await asyncio.wait_for(
            asyncio.to_thread(fetcher or _screen, name),
            timeout=8.0,
        )
    except Exception:
        response = None

    result = render_screen(decision, response)
    if result is None:
        return verified(
            "I recognized your market " + decision["direction"] +
            " request, but the market screener did not provide enough "
            "validated data. I cannot confirm a ranking right now."
        )
    return verified(result)
