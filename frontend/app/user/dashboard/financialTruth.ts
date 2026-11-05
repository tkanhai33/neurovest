export type FinancialState =
  | "not_connected"
  | "unavailable"
  | "awaiting_data"
  | "verified";

export type BalanceInput = {
  status?: string;
  balance_count?: number;
  cash_total?: string | null;
  balances?: Array<{
    currency?: string;
    cash_amount?: string | null;
  }>;
};

export type PortfolioInput = {
  status?: string;
  position_count?: number;
  positions?: Array<{
    currency?: string | null;
    market_value?: string | null;
    unrealized_gain?: string | null;
  }>;
};

export type FinancialResult = {
  state: FinancialState;
  cash: number | null;
  marketValue: number | null;
  unrealizedGain: number | null;
  accountValue: number | null;
};

function amount(value: unknown): number | null {
  if (
    typeof value !== "string" &&
    typeof value !== "number"
  ) {
    return null;
  }

  if (typeof value === "string" && !value.trim()) {
    return null;
  }

  const result = Number(value);

  return Number.isFinite(result) ? result : null;
}

function total(
  values: unknown[],
): number | null {
  const parsed = values.map(amount);

  if (parsed.some((value) => value === null)) {
    return null;
  }

  return (parsed as number[]).reduce(
    (sum, value) => sum + value,
    0,
  );
}

export function financialTruth(
  connection: "connected" | "not_connected" | "unavailable",
  balances: BalanceInput | null,
  portfolio: PortfolioInput | null,
): FinancialResult {
  const empty = (
    state: FinancialState,
  ): FinancialResult => ({
    state,
    cash: null,
    marketValue: null,
    unrealizedGain: null,
    accountValue: null,
  });

  if (connection === "not_connected") {
    return empty("not_connected");
  }

  if (connection !== "connected") {
    return empty("unavailable");
  }

  if (!balances || !portfolio) {
    return empty("unavailable");
  }

  if (
    balances.status !== "ok" ||
    portfolio.status !== "ok"
  ) {
    return empty("unavailable");
  }

  if (
    !Array.isArray(balances.balances) ||
    !Array.isArray(portfolio.positions) ||
    balances.balance_count !== balances.balances.length ||
    portfolio.position_count !== portfolio.positions.length
  ) {
    return empty("unavailable");
  }

  if (balances.balances.length === 0) {
    return empty("awaiting_data");
  }

  // This isolated contract intentionally supports only a
  // single known CAD denomination. Multi-currency portfolio
  // conversions need separately verified FX handling.
  const currencies = [
    ...balances.balances.map((item) => item.currency),
    ...portfolio.positions.map((item) => item.currency),
  ];

  if (
    currencies.some(
      (currency) => currency?.toUpperCase() !== "CAD",
    )
  ) {
    return empty("unavailable");
  }

  const cash = total(
    balances.balances.map((row) => row.cash_amount),
  );

  const marketValue = total(
    portfolio.positions.map((row) => row.market_value),
  );

  const unrealizedGain =
    portfolio.positions.length === 0
      ? 0
      : total(
          portfolio.positions.map(
            (row) => row.unrealized_gain,
          ),
        );

  if (
    cash === null ||
    marketValue === null
  ) {
    return empty("unavailable");
  }

  return {
    state: "verified",
    cash,
    marketValue,
    unrealizedGain,
    accountValue: cash + marketValue,
  };
}
