export const researchUiState = {
  phase: "phase_20_research_ui_skeleton",
  uiOnly: true,
  backendCallsEnabled: false,
  marketDataCallsEnabled: false,
  aiCallsEnabled: false,
  strategyGenerationEnabled: false,
  tradingEnabled: false
} as const;

export const researchModules = [
  "Indicators",
  "Screeners",
  "Backtests",
  "News Summary",
  "Historical Comparison"
] as const;
