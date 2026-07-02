export const marketDataUiState = {
  phase: "phase_18_market_data_ui_skeleton",
  uiOnly: true,
  providerCallsEnabled: false,
  backendCallsEnabled: false,
  tradingEnabled: false,
  brokerCallsEnabled: false
} as const;

export const marketSymbols = [
  "RY.TO",
  "SHOP.TO",
  "VFV.TO",
  "VUN.TO",
  "BTC-CAD"
] as const;
