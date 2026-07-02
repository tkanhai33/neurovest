export const marketDataUiState = {
  phase: "phase_33a_market_data_ui_composition",
  uiOnly: true,
  providerCallsEnabled: false,
  backendCallsEnabled: false,
  tradingEnabled: false,
  brokerCallsEnabled: false
} as const;

export const marketProviders = [
  { name: "yfinance", status: "Locked", role: "Free market data provider" },
  { name: "Finnhub", status: "Locked", role: "Supplemental provider" },
  { name: "Backend API", status: "Locked", role: "Contract bridge pending" }
] as const;

export const marketSymbols = [
  { symbol: "RY.TO", name: "Royal Bank of Canada", exchange: "TSX", currency: "CAD", state: "Watchlisted" },
  { symbol: "SHOP.TO", name: "Shopify", exchange: "TSX", currency: "CAD", state: "Watchlisted" },
  { symbol: "VFV.TO", name: "Vanguard S&P 500 Index ETF", exchange: "TSX", currency: "CAD", state: "Watchlisted" },
  { symbol: "VUN.TO", name: "Vanguard U.S. Total Market Index ETF", exchange: "TSX", currency: "CAD", state: "Watchlisted" },
  { symbol: "BTC-CAD", name: "Bitcoin CAD", exchange: "Crypto", currency: "CAD", state: "Watchlisted" }
] as const;

export const quotePreviewState = {
  selectedSymbol: "RY.TO",
  lastPrice: "Locked",
  currency: "CAD",
  provider: "Provider calls disabled",
  freshness: "No live request",
  contractStatus: "Read-only UI preview"
} as const;

export const candlePreviewState = {
  selectedSymbol: "RY.TO",
  interval: "1D",
  range: "30D",
  chartStatus: "Chart shell only",
  dataStatus: "No candles requested"
} as const;
