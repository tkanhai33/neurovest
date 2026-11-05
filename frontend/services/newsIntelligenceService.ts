export type NewsIntelligenceItem = {
  id: number;
  symbol: string | null;
  headline: string;
  summary: string | null;
  source_name: string | null;
  source_url: string | null;
  published_at: string | null;
  created_at: string;
};


export type NewsIntelligenceResponse = {
  items: NewsIntelligenceItem[];
  count: number;
};


export async function fetchNewsIntelligence(
  options?: {
    symbol?: string;
    limit?: number;
    signal?: AbortSignal;
  },
): Promise<NewsIntelligenceResponse> {
  const params = new URLSearchParams();

  if (options?.symbol) {
    params.set(
      "symbol",
      options.symbol,
    );
  }

  if (options?.limit) {
    params.set(
      "limit",
      String(
        options.limit,
      ),
    );
  }

  const suffix = params.toString();

  const response = await fetch(
    `/api/v1/news${suffix ? `?${suffix}` : ""}`,
    {
      method: "GET",
      credentials: "include",
      cache: "no-store",
      signal: options?.signal,
    },
  );

  if (!response.ok) {
    throw new Error(
      `News Intelligence request failed: ${response.status}`,
    );
  }

  return (
    await response.json()
  ) as NewsIntelligenceResponse;
}
