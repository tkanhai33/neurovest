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

export const dashboardSystemFlow = [
  { name: "Market Data", role: "Symbols, providers, quotes, and candles", status: "Visual only", visibility: "Shared foundation" },
  { name: "Research", role: "Indicators, screeners, news, and comparisons", status: "Visual only", visibility: "Shared foundation" },
  { name: "Strategy", role: "Signals, candidates, scoring, and lineage", status: "Visual only", visibility: "Shared foundation" },
  { name: "Risk", role: "Exposure, limits, drawdown, and approvals", status: "Visual only", visibility: "Shared foundation" },
  { name: "Runtime", role: "Scheduler, workflows, event log, and locks", status: "Locked", visibility: "Shared foundation" },
  { name: "Broker", role: "SnapTrade boundary, account sync, and order locks", status: "Locked", visibility: "Shared foundation" },
  { name: "Paper Trading", role: "Simulated account, orders, fills, positions, and PnL", status: "Locked", visibility: "Shared foundation" },
  { name: "Portfolio", role: "Holdings, cash, allocation, and account summary", status: "Visual only", visibility: "Shared foundation" }
] as const;
