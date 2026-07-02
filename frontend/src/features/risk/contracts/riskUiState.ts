export const riskUiState = {
  phase: "phase_33e_risk_ui_composition",
  uiOnly: true,
  backendCallsEnabled: false,
  riskMathEnabled: false,
  approvalEngineEnabled: false,
  tradingEnabled: false,
  brokerCallsEnabled: false
} as const;

export const riskModules = [
  { name: "Exposure Limits", status: "Locked", role: "Portfolio, sector, and symbol exposure control" },
  { name: "Drawdown Limits", status: "Locked", role: "Daily loss and hard-stop protection" },
  { name: "Daily Trade Limits", status: "Locked", role: "Maximum trade count enforcement" },
  { name: "Approval Decisions", status: "Locked", role: "Manual and automated approval gate" },
  { name: "Position Sizing", status: "Locked", role: "Risk-adjusted order sizing" }
] as const;

export const exposurePreviewState = [
  { label: "Portfolio Exposure", value: "Locked" },
  { label: "Sector Exposure", value: "Locked" },
  { label: "Symbol Exposure", value: "Locked" },
  { label: "Broker Exposure", value: "No broker call" }
] as const;

export const drawdownPreviewState = [
  { label: "Daily Drawdown", value: "Locked" },
  { label: "Soft Limit", value: "Disabled" },
  { label: "Hard Limit", value: "Disabled" },
  { label: "Kill Switch", value: "Locked" }
] as const;

export const dailyLimitPreviewState = {
  maxTrades: "10",
  usedToday: "Locked",
  remaining: "Disabled",
  resetWindow: "TSX session aware later",
  enforcement: "Preview only"
} as const;

export const approvalPreviewState = [
  { label: "Strategy Approval", value: "Locked" },
  { label: "Risk Approval", value: "Locked" },
  { label: "Broker Approval", value: "Locked" },
  { label: "Runtime Approval", value: "Locked" }
] as const;
