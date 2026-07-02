export const backendStatusRequestState = {
  phase: "phase_38m_backend_status_refresh_request_state_shell",
  requestStateShellOnly: true,
  status: "idle",
  loading: false,
  success: false,
  error: null,
  readOnly: true,
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

export const backendStatusRequestStateLabels = {
  idle: "Idle",
  loading: "Loading",
  success: "Success",
  error: "Error"
} as const;
