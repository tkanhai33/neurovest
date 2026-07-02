export const dashboardState = {
  phase: "phase_16_dashboard_skeleton",
  dashboardImplemented: false,
  staticOnly: true,
  backendCallsEnabled: false,
  brokerCallsEnabled: false,
  tradingEnabled: false,
  aiCallsEnabled: false,
  runtimeEnabled: false
} as const;

export const dashboardStacks = [
  "Identity/Auth",
  "Safety/Governance",
  "Market Data",
  "Portfolio",
  "Research",
  "Strategy",
  "Risk",
  "Paper Trading",
  "Broker Integration",
  "Runtime",
  "AI Chat",
  "Global Registry"
] as const;
