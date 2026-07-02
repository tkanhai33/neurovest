import { PageHeader } from "../../../components/ui";
import { AllocationPlaceholderPanel } from "./AllocationPlaceholderPanel";
import { CashBalancePanel } from "./CashBalancePanel";
import { HoldingsPlaceholderPanel } from "./HoldingsPlaceholderPanel";
import { PortfolioSummaryPanel } from "./PortfolioSummaryPanel";

export function PortfolioPanel() {
  return (
    <div style={{ display: "grid", gap: "18px" }}>
      <PageHeader
        title="Portfolio"
        subtitle="Static portfolio UI skeleton. Broker, backend, and mutation paths are locked."
      />
      <PortfolioSummaryPanel />
      <CashBalancePanel />
      <HoldingsPlaceholderPanel />
      <AllocationPlaceholderPanel />
    </div>
  );
}
