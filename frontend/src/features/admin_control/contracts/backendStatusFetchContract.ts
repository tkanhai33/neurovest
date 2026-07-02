import type { BackendStatusBridgeResponse } from "./backendStatusBridgeContract";

export const backendStatusFetchContract = {
  phase: "phase_38a_controlled_real_backend_status_fetch_contract",
  readOnly: true,
  controlledFetchContractOnly: true,
  endpointPath: "/admin-control/backend-status",
  method: "GET",
  fetchImplementationEnabled: false,
  uiFetchEnabled: false,
  backendCallsEnabled: false,
  runtimeEnabled: false,
  brokerCallsEnabled: false,
  tradingEnabled: false,
  mutationEnabled: false,
  providerCallsEnabled: false,
  aiCallsEnabled: false
} as const;

export type ControlledBackendStatusFetchResponse = BackendStatusBridgeResponse;
