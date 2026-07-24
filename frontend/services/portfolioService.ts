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
  const response = await fetch("/api/v1/portfolio/positions", {
    cache: "no-store",
  });

  return await response.json();
}
