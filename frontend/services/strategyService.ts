export type StrategyDecision = {
  status?: string;
  symbol: string;
  decision?: string;
  signal?: string;
  confidence?: number;
  provider?: string;
  error?: string;
};

export async function getStrategyDecision(symbol: string): Promise<StrategyDecision> {
  const cleanSymbol = symbol.trim().toUpperCase();

  if (!cleanSymbol) {
    return {
      status: "error",
      symbol: cleanSymbol,
      decision: "hold",
      confidence: 0,
      provider: "frontend_strategy_service",
      error: "missing_symbol",
    };
  }

  const response = await fetch(`/api/v1/strategy/decision/${cleanSymbol}`, {
    cache: "no-store",
  });

  return await response.json();
}
