import { getBackendStatusButtonClickPreview } from "./backendStatusButtonClickHandler";
import { getBackendStatusRefreshControllerPreview } from "./backendStatusRefreshController";

export const backendStatusClickControllerBridgeState = {
  phase: "phase_38u_click_controller_preview_bridge",
  bridgeOnly: true,
  manualOnly: true,
  readOnly: true,
  invokesFetch: false,
  backendCallsEnabled: false,
  uiFetchEnabled: false,
  clickPropagationEnabled: true,
  controllerPreviewEnabled: true
} as const;

export function getBackendStatusClickControllerFlowPreview() {
  const click = getBackendStatusButtonClickPreview();
  const controller = getBackendStatusRefreshControllerPreview();

  return {
    click,
    controller,
    flow: {
      clickToControllerConnected: true,
      executionEnabled: false,
      backendMutationAllowed: false,
      fetchAllowed: false
    },
    state: {
      clickHandlerEnabled: click.clickHandlerEnabled,
      controllerEnabled: controller.requestTransitionsEnabled,
      readOnly: true
    }
  } as const;
}
