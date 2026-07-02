export const brokerIntegrationUiState = {
  phase: "phase_24_broker_integration_ui_skeleton",
  uiOnly: true,
  backendCallsEnabled: false,
  brokerCallsEnabled: false,
  authFlowEnabled: false,
  tokenStorageEnabled: false,
  accountSyncEnabled: false,
  orderSubmissionEnabled: false,
  liveTradingEnabled: false
} as const;

export const brokerIntegrationModules = [
  "Provider Boundary",
  "Connection Status",
  "Auth Locked",
  "Read-Only Account",
  "Order Submission Locked"
] as const;
