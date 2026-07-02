export const backendStatusUiState = {
  phase: "phase_37b_read_only_backend_status_frontend_contract_mirror",
  frontendOnly: true,
  readOnly: true,
  backendCallsEnabled: false,
  runtimeEnabled: false,
  brokerCallsEnabled: false,
  tradingEnabled: false,
  mutationEnabled: false,
  providerCallsEnabled: false,
  aiCallsEnabled: false
} as const;

export const backendStatusPreviewState = {
  stack: "admin_control",
  phase: "phase_37a_read_only_backend_status_contract",
  readOnly: true,
  backendOnline: "Preview only",
  runtimeEnabled: false,
  brokerCallsEnabled: false,
  tradingEnabled: false,
  mutationEnabled: false,
  providerCallsEnabled: false,
  aiCallsEnabled: false
} as const;
