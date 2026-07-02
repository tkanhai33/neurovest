import { BrokerIntegrationPanel } from "../../features/broker_integration/components";
import { DashboardShell } from "../../features/dashboard/components";
import { MarketDataPanel } from "../../features/market_data/components";
import { NeuroChatPanel } from "../../features/ai_chat/components";
import { PaperTradingPanel } from "../../features/paper_trading/components";
import { PortfolioPanel } from "../../features/portfolio/components";
import { ResearchPanel } from "../../features/research/components";
import { RiskPanel } from "../../features/risk/components";
import { RuntimePanel } from "../../features/runtime/components";
import { StrategyPanel } from "../../features/strategy/components";

export type IntegratedFeatureKey =
  | "dashboard"
  | "market_data"
  | "portfolio"
  | "research"
  | "strategy"
  | "risk"
  | "paper_trading"
  | "broker_integration"
  | "runtime"
  | "ai_chat";

export const featureIntegrationState = {
  phase: "phase_26_frontend_integration_registry",
  integrationOnly: true,
  backendCallsEnabled: false,
  brokerCallsEnabled: false,
  providerCallsEnabled: false,
  aiCallsEnabled: false,
  runtimeExecutionEnabled: false,
  tradingEnabled: false
} as const;

export const integratedFeatures = [
  { key: "dashboard", label: "Dashboard", component: DashboardShell, locked: true },
  { key: "market_data", label: "Market Data", component: MarketDataPanel, locked: true },
  { key: "portfolio", label: "Portfolio", component: PortfolioPanel, locked: true },
  { key: "research", label: "Research", component: ResearchPanel, locked: true },
  { key: "strategy", label: "Strategy", component: StrategyPanel, locked: true },
  { key: "risk", label: "Risk", component: RiskPanel, locked: true },
  { key: "paper_trading", label: "Paper Trading", component: PaperTradingPanel, locked: true },
  { key: "broker_integration", label: "Broker Integration", component: BrokerIntegrationPanel, locked: true },
  { key: "runtime", label: "Runtime", component: RuntimePanel, locked: true },
  { key: "ai_chat", label: "Neuro Chat", component: NeuroChatPanel, locked: true }
] as const;
