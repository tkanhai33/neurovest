export const backendStatusBridgeContract = {
  phase: "phase_37e_read_only_backend_status_bridge_contract",
  frontendOnly: true,
  bridgeOnly: true,
  endpointPath: "/admin-control/backend-status",
  method: "GET",
  readOnly: true,
  fetchEnabled: false,
  backendCallsEnabled: false,
  runtimeEnabled: false,
  brokerCallsEnabled: false,
  tradingEnabled: false,
  mutationEnabled: false,
  providerCallsEnabled: false,
  aiCallsEnabled: false
} as const;

export type BackendStatusBridgeResponse = {
  stack: string;
  phase: string;
  read_only: boolean;
  backend_online: boolean;
  runtime_enabled: boolean;
  broker_calls_enabled: boolean;
  trading_enabled: boolean;
  mutation_enabled: boolean;
  provider_calls_enabled: boolean;
  ai_calls_enabled: boolean;
};
