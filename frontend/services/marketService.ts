export type LiveQuote = {
  status?: string;
  symbol?: string;
  price?: number | null;
  open_price?: number | null;
  open?: number | null;
  previous_close?: number | null;
  regularMarketOpen?: number | null;
  provider?: string;
  currency?: string;
  error?: string;
};

export async function getLivePrice(
  symbol: string,
): Promise<LiveQuote> {
  const cleanSymbol =
    symbol.trim().toUpperCase();

  if (!cleanSymbol) {
    return {
      status: "error",
      symbol: cleanSymbol,
      price: null,
      provider:
        "frontend_market_service",
      error: "missing_symbol",
    };
  }

  const response = await fetch(
    `/api/v1/market/live-price/${encodeURIComponent(
      cleanSymbol,
    )}`,
    {
      cache: "no-store",
    },
  );

  const payload =
    (await response.json()) as
      LiveQuote;

  return {
    symbol: cleanSymbol,
    ...payload,
  };
}

export async function getLivePrices(
  symbols: string[],
): Promise<Record<string, LiveQuote>> {
  const cleanSymbols = [
    ...new Set(
      symbols
        .map((symbol) =>
          symbol.trim().toUpperCase(),
        )
        .filter(Boolean),
    ),
  ];

  if (cleanSymbols.length === 0) {
    return {};
  }

  const response = await fetch(
    `/api/v1/market/live-prices?symbols=${encodeURIComponent(
      cleanSymbols.join(","),
    )}`,
    {
      cache: "no-store",
    },
  );

  const payload = (await response.json()) as {
    quotes?: Record<string, LiveQuote>;
    error?: string;
  };

  return Object.fromEntries(
    cleanSymbols.map((symbol) => [
      symbol,
      payload.quotes?.[symbol] ?? {
        status: "error",
        symbol,
        price: null,
        provider: "frontend_market_service",
        error:
          payload.error ??
          "bulk_quote_unavailable",
      },
    ]),
  );
}
