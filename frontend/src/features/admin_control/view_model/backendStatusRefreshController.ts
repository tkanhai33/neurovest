import { getBackendStatusRefreshActionContract } from "./backendStatusRefreshAction";
import {
  backendStatusRequestState,
  backendStatusRequestStateLabels
} from "./backendStatusRequestState";

export const backendStatusRefreshControllerState = {
  phase: "phase_38o_manual_backend_status_refresh_request_controller_shell",
  controllerShellOnly: true,
  manualOnly: true,
  readOnly: true,
  buttonEnabled: false,
  requestTransitionsEnabled: false,
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

export function getBackendStatusRefreshControllerPreview() {
  const action = getBackendStatusRefreshActionContract();

  return {
    action: action.action,
    implementation: action.implementation,
    currentStatus: backendStatusRequestState.status,
    currentLabel: backendStatusRequestStateLabels[backendStatusRequestState.status],
    nextAllowedStates: [
      backendStatusRequestStateLabels.loading,
      backendStatusRequestStateLabels.success,
      backendStatusRequestStateLabels.error
    ],
    readOnly: backendStatusRefreshControllerState.readOnly,
    manualOnly: backendStatusRefreshControllerState.manualOnly,
    buttonEnabled: backendStatusRefreshControllerState.buttonEnabled,
    requestTransitionsEnabled: backendStatusRefreshControllerState.requestTransitionsEnabled,
    backendCallsEnabled: backendStatusRefreshControllerState.backendCallsEnabled
  } as const;
}
