export const brokerIntegrationUiState = {
  phase: "phase_33g_broker_integration_ui_composition",
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
  { name: "Provider Boundary", status: "Locked", role: "SnapTrade boundary visibility" },
  { name: "Connection Status", status: "Locked", role: "No broker connection active" },
  { name: "Auth Locked", status: "Locked", role: "No auth flow or token storage" },
  { name: "Read-Only Account", status: "Locked", role: "No account sync or balance reads" },
  { name: "Order Submission", status: "Locked", role: "No orders, execution, or live trading" }
] as const;

export const brokerProviderPreviewState = [
  { label: "Provider", value: "SnapTrade" },
  { label: "Mode", value: "UI Preview" },
  { label: "Calls", value: "Locked" },
  { label: "Access", value: "No broker request" }
] as const;

export const brokerConnectionPreviewState = [
  "Not connected",
  "Read-only locked",
  "Account sync locked",
  "Live trading locked"
] as const;

export const brokerAuthLockState = [
  "Auth flow disabled",
  "Token storage disabled",
  "Secrets handling disabled",
  "Broker session disabled"
] as const;

export const brokerAccountPreviewState = [
  { label: "Account Sync", value: "Locked" },
  { label: "Positions", value: "Disabled" },
  { label: "Balances", value: "Disabled" },
  { label: "Holdings Source", value: "No broker call" }
] as const;

export const brokerOrderLockState = [
  "Orders disabled",
  "Execution disabled",
  "Canary disabled",
  "Live trading disabled"
] as const;
