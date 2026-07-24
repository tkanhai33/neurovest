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
    return {
      status: "error",
      symbol: cleanSymbol,
      allowed: false,
      gate: "risk",
      provider: "frontend_risk_service",
      error: "missing_symbol",
    };
  }

  const response = await fetch(`/api/v1/risk/gate/${cleanSymbol}`, {
    cache: "no-store",
  });

  return await response.json();
}
