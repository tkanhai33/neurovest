export const backendStatusRefreshButtonState = {
  phase: "phase_38q_enable_manual_backend_status_refresh_button_contract",
  buttonShellOnly: false,
  manualOnly: true,
  readOnly: true,
  autoFetchEnabled: false,
  pollingEnabled: false,
  intervalEnabled: false,
  clickFetchEnabled: true,
  uiFetchEnabled: false,
  backendCallsEnabled: false,
  runtimeEnabled: false,
  brokerCallsEnabled: false,
  tradingEnabled: false,
  mutationEnabled: false,
  providerCallsEnabled: false,
  aiCallsEnabled: false
} as const;

export const backendStatusRefreshButtonLabel = "Refresh Backend Status";
