#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()

# -----------------------------
# 12A backend market_data service facade
# -----------------------------
service = ROOT / "backend/app/stacks/market_data/market_data_service.py"
service.write_text(r'''from backend.app.stacks.market_data.feed import get_live_price_quote


async def get_live_market_price_for_api(symbol: str):
    return await get_live_price_quote(symbol)
''')

# -----------------------------
# 12B FastAPI route uses service facade only
# -----------------------------
main = ROOT / "backend/app/main.py"
main_text = main.read_text()

main_text = main_text.replace(
    "from backend.app.stacks.market_data.feed import get_live_price_quote",
    "from backend.app.stacks.market_data.market_data_service import get_live_market_price_for_api"
)

main_text = main_text.replace(
    "return await get_live_price_quote(symbol)",
    "return await get_live_market_price_for_api(symbol)"
)

main.write_text(main_text)

# -----------------------------
# 12C frontend marketService.ts
# -----------------------------
services_dir = ROOT / "frontend/services"
services_dir.mkdir(parents=True, exist_ok=True)

market_service = services_dir / "marketService.ts"
market_service.write_text(r'''export type LiveQuote = {
  status?: string;
  symbol?: string;
  price?: number | null;
  provider?: string;
  error?: string;
};

export async function getLivePrice(symbol: string): Promise<LiveQuote> {
  const cleanSymbol = symbol.trim().toUpperCase();

  if (!cleanSymbol) {
    return {
      status: "error",
      symbol: cleanSymbol,
      price: null,
      provider: "frontend_market_service",
      error: "missing_symbol",
    };
  }

  const response = await fetch(`/api/v1/market/live-price/${cleanSymbol}`, {
    cache: "no-store",
  });

  return await response.json();
}

export async function getLivePrices(symbols: string[]): Promise<Record<string, LiveQuote>> {
  const results = await Promise.all(
    symbols.map(async (symbol) => {
      const quote = await getLivePrice(symbol);

      return [
        symbol,
        {
          symbol,
          ...quote,
        },
      ] as const;
    })
  );

  return Object.fromEntries(results);
}
''')

# -----------------------------
# 12D page uses frontend service
# -----------------------------
page = ROOT / "frontend/app/page.tsx"
page_text = page.read_text()

if 'from "../services/marketService"' not in page_text:
    page_text = page_text.replace(
        'import { useCallback, useEffect, useState } from "react";',
        'import { useCallback, useEffect, useState } from "react";\nimport { getLivePrice, getLivePrices, type LiveQuote } from "../services/marketService";'
    )

# remove local LiveQuote type block if present
local_type = '''type LiveQuote = {
  status?: string;
  symbol?: string;
  price?: number | null;
  provider?: string;
  error?: string;
};

'''
page_text = page_text.replace(local_type, "")

# direct single quote fetch -> service
old_single = '''      const response = await fetch(`/api/v1/market/live-price/${cleanSymbol}`, {
        cache: "no-store",
      });

      const data = await response.json();
      setQuote(data);'''

new_single = '''      const data = await getLivePrice(cleanSymbol);
      setQuote(data);'''

page_text = page_text.replace(old_single, new_single)

# direct watchlist fetch -> service
old_watch = '''      const results = await Promise.all(
        WATCHLIST_SYMBOLS.map(async (symbol) => {
          const response = await fetch(`/api/v1/market/live-price/${symbol}`, {
            cache: "no-store",
          });

          const data = await response.json();

          return [
            symbol,
            {
              symbol,
              ...data,
            },
          ] as const;
        })
      );

      setQuotes(Object.fromEntries(results));'''

new_watch = '''      const data = await getLivePrices(WATCHLIST_SYMBOLS);
      setQuotes(data);'''

page_text = page_text.replace(old_watch, new_watch)

page.write_text(page_text)

print("patched Phase 12 service layer alignment")
