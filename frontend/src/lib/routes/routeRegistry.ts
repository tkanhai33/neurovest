export type FrontendRouteKey =
  | "dashboard"
  | "market_data"
  | "portfolio"
  | "research"
  | "strategy"
  | "risk"
  | "paper_trading"
  | "broker_integration"
  | "runtime"
  | "ai_chat"
  | "admin_control"
  | "settings";

export type FrontendRoute = {
  key: FrontendRouteKey;
  label: string;
  path: string;
  locked: boolean;
};

export const frontendRoutes: readonly FrontendRoute[] = [
  { key: "dashboard", label: "Dashboard", path: "/", locked: true },
  { key: "market_data", label: "Market Data", path: "/market-data", locked: true },
  { key: "portfolio", label: "Portfolio", path: "/portfolio", locked: true },
  { key: "research", label: "Research", path: "/research", locked: true },
  { key: "strategy", label: "Strategy", path: "/strategy", locked: true },
  { key: "risk", label: "Risk", path: "/risk", locked: true },
  { key: "paper_trading", label: "Paper Trading", path: "/paper-trading", locked: true },
  { key: "broker_integration", label: "Broker Integration", path: "/broker-integration", locked: true },
  { key: "runtime", label: "Runtime", path: "/runtime", locked: true },
  { key: "ai_chat", label: "Neuro Chat", path: "/ai-chat", locked: true },
  { key: "admin_control", label: "Admin", path: "/admin", locked: true },
  { key: "settings", label: "Settings", path: "/settings", locked: true }
] as const;
