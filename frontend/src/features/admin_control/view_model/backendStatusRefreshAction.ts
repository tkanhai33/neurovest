import { fetchBackendStatus } from "../client";
import { backendStatusRefreshState } from "./backendStatusRefreshState";

export const backendStatusRefreshActionState = {
  phase: "phase_38q_enable_manual_backend_status_refresh_button_contract",
  actionShellOnly: false,
  manualOnly: true,
  readOnly: true,
  autoFetchEnabled: false,
  pollingEnabled: false,
  intervalEnabled: false,
  uiFetchEnabled: true,
  backendCallsEnabled: false,
  runtimeEnabled: false,
  brokerCallsEnabled: false,
  tradingEnabled: false,
  mutationEnabled: false,
  providerCallsEnabled: false,
  aiCallsEnabled: false
} as const;

export function getBackendStatusRefreshActionLabel() {
  return backendStatusRefreshState.manualOnly
    ? "Manual refresh action locked"
    : "Manual refresh unavailable";
}

export function getBackendStatusRefreshActionContract() {
  return {
    action: "manual_backend_status_refresh",
    implementation: fetchBackendStatus.name,
    readOnly: backendStatusRefreshActionState.readOnly,
    manualOnly: backendStatusRefreshActionState.manualOnly,
    uiFetchEnabled: backendStatusRefreshActionState.uiFetchEnabled,
    backendCallsEnabled: backendStatusRefreshActionState.backendCallsEnabled
  } as const;
}
