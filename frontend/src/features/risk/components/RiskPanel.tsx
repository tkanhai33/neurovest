import { PageHeader } from "../../../components/ui";
import { ApprovalDecisionPlaceholderPanel } from "./ApprovalDecisionPlaceholderPanel";
import { DailyLimitPlaceholderPanel } from "./DailyLimitPlaceholderPanel";
import { DrawdownPlaceholderPanel } from "./DrawdownPlaceholderPanel";
import { ExposurePlaceholderPanel } from "./ExposurePlaceholderPanel";
import { RiskOverviewPanel } from "./RiskOverviewPanel";

export function RiskPanel() {
  return (
    <div style={{ display: "grid", gap: "18px" }}>
      <PageHeader
        title="Risk"
        subtitle="Static risk UI skeleton. Risk math, approvals, trading, and broker paths are locked."
      />
      <RiskOverviewPanel />
      <ExposurePlaceholderPanel />
      <DrawdownPlaceholderPanel />
      <DailyLimitPlaceholderPanel />
      <ApprovalDecisionPlaceholderPanel />
    </div>
  );
}
