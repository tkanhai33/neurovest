import { PageHeader } from "../../../components/ui";
import { PaperAccountPlaceholderPanel } from "./PaperAccountPlaceholderPanel";
import { PaperPnLPlaceholderPanel } from "./PaperPnLPlaceholderPanel";
import { PaperPositionPlaceholderPanel } from "./PaperPositionPlaceholderPanel";
import { PaperTradingOverviewPanel } from "./PaperTradingOverviewPanel";
import { SimulatedFillPlaceholderPanel } from "./SimulatedFillPlaceholderPanel";
import { SimulatedOrderPlaceholderPanel } from "./SimulatedOrderPlaceholderPanel";

export function PaperTradingPanel() {
  return (
    <div style={{ display: "grid", gap: "18px" }}>
      <PageHeader
        title="Paper Trading"
        subtitle="Static paper trading UI skeleton. Simulated orders, fills, positions, PnL, and broker paths are locked."
      />
      <PaperTradingOverviewPanel />
      <PaperAccountPlaceholderPanel />
      <SimulatedOrderPlaceholderPanel />
      <SimulatedFillPlaceholderPanel />
      <PaperPositionPlaceholderPanel />
      <PaperPnLPlaceholderPanel />
    </div>
  );
}
