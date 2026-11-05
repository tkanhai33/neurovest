export type StrategyContribution = {
  strategy_name: string;
  evaluator_id?: string;
  status?: string;
  decision: string;
  confidence?: number;
  reason?: string;
};

export type StrategyDecision = {
  status?: string;
  symbol: string;
  decision?: string;
  signal?: string;
  confidence?: number;
  provider?: string;
  strategy_name?: string;
  enabled_strategy_name?: string;
  enabled_strategy_names?: string[];
  enabled_strategy_count?: number;
  evaluator_id?: string;
  buy_votes?: number;
  sell_votes?: number;
  hold_votes?: number;
  net_vote?: number;
  directional_votes?: number;
  winning_votes?: number;
  eligible_results?: number;
  received_results?: number;
  abstaining_results?: number;
  mean_winner_confidence?: number;
  consensus_ratio?: number;
  participation_ratio?: number;
  contributing_strategies?: string[];
  abstaining_strategies?: string[];
  strategy_results?: StrategyContribution[];
  execution_enabled?: boolean;
  owner_strategy_applied?: boolean;
  owner_strategy_reason?: string;
  reason?: string;
  short_window?: number;
  long_window?: number;
  minimum_bars?: number;
  received_bars?: number;
  previous_fast_sma?: number;
  previous_slow_sma?: number;
  current_fast_sma?: number;
  current_slow_sma?: number;
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
