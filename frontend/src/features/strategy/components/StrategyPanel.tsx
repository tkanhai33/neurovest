import { PageHeader } from "../../../components/ui";
import { CandidatePlaceholderPanel } from "./CandidatePlaceholderPanel";
import { SignalPlaceholderPanel } from "./SignalPlaceholderPanel";
import { StrategyOverviewPanel } from "./StrategyOverviewPanel";
import { VersionLineagePlaceholderPanel } from "./VersionLineagePlaceholderPanel";

export function StrategyPanel() {
  return (
    <div style={{ display: "grid", gap: "18px" }}>
      <PageHeader
        title="Strategy"
        subtitle="Static strategy UI skeleton. Signals, scoring, promotion, risk, and trading integration are locked."
      />
      <StrategyOverviewPanel />
      <SignalPlaceholderPanel />
      <CandidatePlaceholderPanel />
      <VersionLineagePlaceholderPanel />
    </div>
  );
}
