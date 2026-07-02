export const strategyUiState = {
  phase: "phase_21_strategy_ui_skeleton",
  uiOnly: true,
  backendCallsEnabled: false,
  signalGenerationEnabled: false,
  scoringEnabled: false,
  promotionEnabled: false,
  tradingEnabled: false
} as const;

export const strategyModules = [
  "Signals",
  "Candidates",
  "Scoring",
  "Version Lineage",
  "Promotion Review"
] as const;
