export const runtimeUiState = {
  phase: "phase_25_runtime_ui_skeleton",
  uiOnly: true,
  backendCallsEnabled: false,
  schedulerEnabled: false,
  backgroundLoopsEnabled: false,
  workflowExecutionEnabled: false,
  mutationEnabled: false,
  brokerCallsEnabled: false,
  tradingEnabled: false
} as const;

export const runtimeModules = [
  "Runtime Status",
  "Scheduler Locked",
  "Workflow Placeholder",
  "Event Log Placeholder",
  "Mutation Locked"
] as const;
