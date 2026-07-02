export const backendStatusRefreshState = {
  phase: "phase_38h_manual_backend_status_refresh_ui_shell",
  refreshShellOnly: true,
  manualOnly: true,
  autoFetchEnabled: false,
  pollingEnabled: false,
  intervalEnabled: false,
  uiFetchEnabled: false,
  backendCallsEnabled: false,
  runtimeEnabled: false,
  brokerCallsEnabled: false,
  tradingEnabled: false,
  mutationEnabled: false,
  providerCallsEnabled: false,
  aiCallsEnabled: false
} as const;

export const backendStatusRefreshLabel = "Manual refresh locked";
