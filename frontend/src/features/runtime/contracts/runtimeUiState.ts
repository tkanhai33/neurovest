export const runtimeUiState = {
  phase: "phase_33f_runtime_visualization_composition",
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
  { name: "Runtime Status", status: "Locked", role: "Top-level engine readiness view" },
  { name: "Scheduler", status: "Locked", role: "No background jobs or loops" },
  { name: "Workflow", status: "Locked", role: "No workflow execution" },
  { name: "Event Log", status: "Preview", role: "Static runtime event visibility" },
  { name: "Mutation", status: "Locked", role: "No AI, strategy, or runtime mutation" }
] as const;

export const runtimeStatusPreviewState = [
  { label: "Runtime", value: "Locked" },
  { label: "Scheduler", value: "Disabled" },
  { label: "Background Loops", value: "Disabled" },
  { label: "Workflow Execution", value: "Locked" },
  { label: "Trading", value: "Locked" }
] as const;

export const schedulerLockState = [
  "No background loops",
  "No scheduled jobs",
  "No runtime execution",
  "No broker automation"
] as const;

export const workflowPreviewState = [
  { step: "Market Data", status: "Visual only" },
  { step: "Research", status: "Visual only" },
  { step: "Strategy", status: "Visual only" },
  { step: "Risk", status: "Visual only" },
  { step: "Broker", status: "Locked" }
] as const;

export const runtimeEventPreviewState = [
  { event: "Phase 33A Market UI", status: "Committed" },
  { event: "Phase 33B Portfolio UI", status: "Committed" },
  { event: "Phase 33C Research UI", status: "Committed" },
  { event: "Phase 33D Strategy UI", status: "Committed" },
  { event: "Phase 33E Risk UI", status: "Committed" }
] as const;

export const mutationLockState = [
  "AI mutation disabled",
  "Strategy mutation disabled",
  "Runtime mutation disabled",
  "Learning writes disabled"
] as const;
