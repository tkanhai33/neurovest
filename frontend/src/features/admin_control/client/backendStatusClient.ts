import {
  backendStatusFetchContract,
  type ControlledBackendStatusFetchResponse
} from "../contracts/backendStatusFetchContract";

export const backendStatusClientState = {
  phase: "phase_38f_read_only_backend_status_fetch_implementation",
  clientShellOnly: false,
  readOnly: true,
  fetchImplementationEnabled: true,
  manualFetchOnly: true,
  uiFetchEnabled: false,
  pollingEnabled: false,
  backendCallsEnabled: true,
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

export async function fetchBackendStatus(): Promise<ControlledBackendStatusFetchResponse> {
  const response = await fetch(backendStatusFetchContract.endpointPath, {
    method: backendStatusFetchContract.method
  });

  if (!response.ok) {
    throw new Error("Backend status request failed");
  }

  return response.json() as Promise<ControlledBackendStatusFetchResponse>;
}

export type BackendStatusClientResponse = ControlledBackendStatusFetchResponse;
