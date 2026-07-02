import {
  backendStatusFetchContract,
  type ControlledBackendStatusFetchResponse
} from "../contracts/backendStatusFetchContract";

export const backendStatusClientState = {
  phase: "phase_38b_controlled_backend_status_client_shell",
  clientShellOnly: true,
  readOnly: true,
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

export function getBackendStatusClientContract() {
  return backendStatusFetchContract;
}

export type BackendStatusClientResponse = ControlledBackendStatusFetchResponse;
