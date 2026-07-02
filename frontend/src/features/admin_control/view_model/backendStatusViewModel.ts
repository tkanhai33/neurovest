import { backendStatusClientState } from "../client";
import { backendStatusPreviewState } from "../contracts/backendStatusUiState";

export const backendStatusViewModelState = {
  phase: "phase_38c_controlled_backend_status_view_model_shell",
  viewModelOnly: true,
  readOnly: true,
  usesPreviewStateOnly: true,
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

export const backendStatusDisplayModel = {
  stack: backendStatusPreviewState.stack,
  backend: backendStatusPreviewState.backendOnline,
  runtime: backendStatusPreviewState.runtimeEnabled ? "Enabled" : "Locked",
  brokerCalls: backendStatusPreviewState.brokerCallsEnabled ? "Enabled" : "Locked",
  trading: backendStatusPreviewState.tradingEnabled ? "Enabled" : "Locked",
  mutation: backendStatusPreviewState.mutationEnabled ? "Enabled" : "Locked",
  providers: backendStatusPreviewState.providerCallsEnabled ? "Enabled" : "Locked",
  aiCalls: backendStatusPreviewState.aiCallsEnabled ? "Enabled" : "Locked",
  client: backendStatusClientState.clientShellOnly ? "Client shell only" : "Client active"
} as const;
