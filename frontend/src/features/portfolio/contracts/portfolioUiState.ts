export const portfolioUiState = {
  phase: "phase_33b_portfolio_ui_composition",
  uiOnly: true,
  backendCallsEnabled: false,
  brokerCallsEnabled: false,
  tradingEnabled: false,
  runtimeEnabled: false
} as const;

export const portfolioSummaryState = {
  accountName: "NeuroVest Paper Portfolio",
  totalEquity: "Locked",
  cashAvailable: "Preview Only",
  dailyPnL: "No broker call",
  buyingPower: "Locked",
  dataStatus: "Static UI composition"
} as const;

export const cashBalanceState = {
  currency: "CAD",
  cash: "Preview Only",
  settledCash: "Locked",
  unsettledCash: "Locked",
  source: "No backend request"
} as const;

export const holdingsPreviewState = [
  { symbol: "RY.TO", name: "Royal Bank of Canada", weight: "Preview", quantity: "Locked", value: "Locked" },
  { symbol: "SHOP.TO", name: "Shopify", weight: "Preview", quantity: "Locked", value: "Locked" },
  { symbol: "VFV.TO", name: "Vanguard S&P 500 Index ETF", weight: "Preview", quantity: "Locked", value: "Locked" },
  { symbol: "VUN.TO", name: "Vanguard U.S. Total Market Index ETF", weight: "Preview", quantity: "Locked", value: "Locked" }
] as const;

export const allocationPreviewState = [
  { label: "Canadian Equities", value: "Preview" },
  { label: "US Index Exposure", value: "Preview" },
  { label: "Cash", value: "Preview" },
  { label: "Crypto", value: "Locked" }
] as const;
