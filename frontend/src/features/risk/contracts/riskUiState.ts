export const riskUiState = {
  phase: "phase_22_risk_ui_skeleton",
  uiOnly: true,
  backendCallsEnabled: false,
  riskMathEnabled: false,
  approvalEngineEnabled: false,
  tradingEnabled: false,
  brokerCallsEnabled: false
} as const;

export const riskModules = [
  "Exposure Limits",
  "Drawdown Limits",
  "Daily Trade Limits",
  "Approval Decisions",
  "Position Sizing"
] as const;
