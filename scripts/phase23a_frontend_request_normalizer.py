#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()
S = ROOT / "frontend/services"
S.mkdir(parents=True, exist_ok=True)

(S / "requestNormalizer.ts").write_text(r'''type CacheEntry<T> = { expiresAt: number; value: T };

const responseCache = new Map<string, CacheEntry<unknown>>();
const inflight = new Map<string, Promise<unknown>>();

export type RequestOptions = {
  ttlMs?: number;
  method?: "GET" | "POST";
  headers?: Record<string, string>;
  body?: BodyInit | null;
};

export async function normalizedJsonRequest<T>(
  key: string,
  url: string,
  options: RequestOptions = {}
): Promise<T> {
  const method = options.method || "GET";
  const ttlMs = options.ttlMs ?? 3000;
  const cacheKey = `${method}:${key}`;
  const now = Date.now();

  if (method === "GET") {
    const cached = responseCache.get(cacheKey);
    if (cached && cached.expiresAt > now) return cached.value as T;

    const existing = inflight.get(cacheKey);
    if (existing) return existing as Promise<T>;
  }

  const request = fetch(url, {
    method,
    headers: options.headers,
    body: options.body,
    cache: "no-store",
  })
    .then(async (response) => {
      const data = await response.json();

      if (method === "GET") {
        responseCache.set(cacheKey, {
          expiresAt: Date.now() + ttlMs,
          value: data,
        });
      }

      return data as T;
    })
    .finally(() => inflight.delete(cacheKey));

  if (method === "GET") inflight.set(cacheKey, request);

  return request;
}

export function clearRequestNormalizerCache() {
  responseCache.clear();
  inflight.clear();
}
''')

(S / "marketService.ts").write_text(r'''import { normalizedJsonRequest } from "./requestNormalizer";

export type LiveQuote = {
  status?: string;
  symbol?: string;
  price?: number | null;
  provider?: string;
  error?: string;
};

export async function getLivePrice(symbol: string): Promise<LiveQuote> {
  const cleanSymbol = symbol.trim().toUpperCase();

  if (!cleanSymbol) {
    return { status: "error", symbol: cleanSymbol, price: null, provider: "frontend_market_service", error: "missing_symbol" };
  }

  return await normalizedJsonRequest<LiveQuote>(
    `market-live-price:${cleanSymbol}`,
    `/api/v1/market/live-price/${cleanSymbol}`,
    { ttlMs: 10000 }
  );
}

export async function getLivePrices(symbols: string[]): Promise<Record<string, LiveQuote>> {
  const results = await Promise.all(
    symbols.map(async (symbol) => [symbol, { symbol, ...(await getLivePrice(symbol)) }] as const)
  );

  return Object.fromEntries(results);
}
''')

(S / "portfolioService.ts").write_text(r'''import { normalizedJsonRequest } from "./requestNormalizer";

export type PortfolioPosition = {
  id?: string | number;
  symbol: string;
  shares_quantity?: number;
  realized_pnl?: number;
};

export type PortfolioPositionsResponse = {
  status?: string;
  positions: PortfolioPosition[];
  count?: number;
  provider?: string;
  error?: string;
};

export async function getPortfolioPositions(): Promise<PortfolioPositionsResponse> {
  return await normalizedJsonRequest<PortfolioPositionsResponse>(
    "portfolio-positions",
    "/api/v1/portfolio/positions",
    { ttlMs: 5000 }
  );
}
''')

(S / "strategyService.ts").write_text(r'''import { normalizedJsonRequest } from "./requestNormalizer";

export type StrategyDecision = {
  status?: string;
  symbol: string;
  decision?: string;
  signal?: string | { action?: string; status?: string; symbol?: string };
  confidence?: number;
  provider?: string;
  error?: string;
};

export async function getStrategyDecision(symbol: string): Promise<StrategyDecision> {
  const cleanSymbol = symbol.trim().toUpperCase();

  if (!cleanSymbol) {
    return { status: "error", symbol: cleanSymbol, decision: "hold", confidence: 0, provider: "frontend_strategy_service", error: "missing_symbol" };
  }

  return await normalizedJsonRequest<StrategyDecision>(
    `strategy-decision:${cleanSymbol}`,
    `/api/v1/strategy/decision/${cleanSymbol}`,
    { ttlMs: 10000 }
  );
}
''')

(S / "riskService.ts").write_text(r'''import { normalizedJsonRequest } from "./requestNormalizer";

export type RiskGate = {
  status?: string;
  symbol: string;
  allowed?: boolean;
  gate?: string;
  provider?: string;
  error?: string;
};

export async function getRiskGate(symbol: string): Promise<RiskGate> {
  const cleanSymbol = symbol.trim().toUpperCase();

  if (!cleanSymbol) {
    return { status: "error", symbol: cleanSymbol, allowed: false, gate: "risk", provider: "frontend_risk_service", error: "missing_symbol" };
  }

  return await normalizedJsonRequest<RiskGate>(
    `risk-gate:${cleanSymbol}`,
    `/api/v1/risk/gate/${cleanSymbol}`,
    { ttlMs: 10000 }
  );
}
''')

print("hard-wired Phase 23A request normalizer services")
