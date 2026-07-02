export const strategyUiState = {
  phase: "phase_33d_strategy_ui_composition",
  uiOnly: true,
  backendCallsEnabled: false,
  signalGenerationEnabled: false,
  scoringEnabled: false,
  promotionEnabled: false,
  tradingEnabled: false
} as const;

export const strategyModules = [
  { name: "Signals", status: "Locked", role: "Directional signal preparation" },
  { name: "Candidates", status: "Locked", role: "Strategy candidate review" },
  { name: "Scoring", status: "Locked", role: "Performance score preparation" },
  { name: "Version Lineage", status: "Locked", role: "Parent-child strategy tracking" },
  { name: "Promotion Review", status: "Locked", role: "Manual approval gate" }
] as const;

export const signalPreviewState = {
  symbol: "RY.TO",
  direction: "Locked",
  confidence: "Disabled",
  strategyFamily: "Preview Only",
  riskLinked: "Locked"
} as const;

export const candidatePreviewState = [
  { name: "Momentum Candidate", family: "Momentum", score: "Locked", status: "Preview" },
  { name: "Defensive Candidate", family: "Defensive", score: "Locked", status: "Preview" },
  { name: "ETF Rotation Candidate", family: "Rotation", score: "Locked", status: "Preview" }
] as const;

export const lineagePreviewState = [
  { label: "Parent Strategy", value: "Locked" },
  { label: "Candidate Version", value: "Preview Only" },
  { label: "Promotion Status", value: "Manual approval locked" },
  { label: "Overwrite Policy", value: "Never overwrite parent" }
] as const;
