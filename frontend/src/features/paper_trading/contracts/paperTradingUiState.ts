export const paperTradingUiState = {
  phase: "phase_23_paper_trading_ui_skeleton",
  uiOnly: true,
  backendCallsEnabled: false,
  simulatedOrderEngineEnabled: false,
  simulatedFillEngineEnabled: false,
  pnlLogicEnabled: false,
  brokerCallsEnabled: false,
  tradingEnabled: false
} as const;

export const paperTradingModules = [
  "Paper Account",
  "Simulated Orders",
  "Simulated Fills",
  "Paper Positions",
  "Paper PnL"
] as const;
