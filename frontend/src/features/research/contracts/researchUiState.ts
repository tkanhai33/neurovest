export const researchUiState = {
  phase: "phase_33c_research_ui_composition",
  uiOnly: true,
  backendCallsEnabled: false,
  marketDataCallsEnabled: false,
  aiCallsEnabled: false,
  strategyGenerationEnabled: false,
  tradingEnabled: false
} as const;

export const researchModules = [
  { name: "Indicators", status: "Locked", role: "Technical signal preparation" },
  { name: "Screeners", status: "Locked", role: "Symbol filtering preparation" },
  { name: "Backtests", status: "Locked", role: "Historical validation preparation" },
  { name: "News Summary", status: "Locked", role: "Research context preparation" },
  { name: "Historical Comparison", status: "Locked", role: "Pattern comparison preparation" }
] as const;

export const indicatorPreviewState = [
  { label: "RSI", value: "Locked" },
  { label: "MACD", value: "Locked" },
  { label: "EMA", value: "Locked" },
  { label: "ATR", value: "Locked" },
  { label: "Volume Trend", value: "Preview Only" }
] as const;

export const screenerPreviewState = [
  { label: "Momentum", value: "Locked" },
  { label: "Defensive", value: "Locked" },
  { label: "Dividend", value: "Preview" },
  { label: "ETF", value: "Preview" }
] as const;

export const backtestPreviewState = {
  selectedSymbol: "RY.TO",
  strategyFamily: "Preview Only",
  dateRange: "Locked",
  executionStatus: "No backtest execution",
  resultStatus: "No results generated"
} as const;

export const newsResearchPreviewState = [
  { source: "Market News", status: "Locked", note: "No external request" },
  { source: "AI Summary", status: "Locked", note: "No model call" },
  { source: "Historical Context", status: "Locked", note: "No comparison run" }
] as const;
