import { getBackendStatusRefreshControllerPreview } from "./backendStatusRefreshController";

export const backendStatusButtonClickHandlerState = {
  phase: "phase_38r_button_click_wiring_shell",
  clickHandlerShellOnly: true,
  manualOnly: true,
  readOnly: true,
  buttonClickWiringPrepared: true,
  clickHandlerEnabled: false,
  invokesFetch: false,
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

export function getBackendStatusButtonClickPreview() {
  const controller = getBackendStatusRefreshControllerPreview();

  return {
    action: controller.action,
    currentStatus: controller.currentStatus,
    currentLabel: controller.currentLabel,
    buttonClickWiringPrepared: backendStatusButtonClickHandlerState.buttonClickWiringPrepared,
    clickHandlerEnabled: backendStatusButtonClickHandlerState.clickHandlerEnabled,
    invokesFetch: backendStatusButtonClickHandlerState.invokesFetch,
    requestTransitionsEnabled: backendStatusButtonClickHandlerState.requestTransitionsEnabled,
    readOnly: backendStatusButtonClickHandlerState.readOnly,
    manualOnly: backendStatusButtonClickHandlerState.manualOnly,
    backendCallsEnabled: backendStatusButtonClickHandlerState.backendCallsEnabled
  } as const;
}
