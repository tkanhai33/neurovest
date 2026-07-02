import { PageHeader } from "../../../components/ui";
import { BacktestPlaceholderPanel } from "./BacktestPlaceholderPanel";
import { IndicatorPlaceholderPanel } from "./IndicatorPlaceholderPanel";
import { NewsResearchPlaceholderPanel } from "./NewsResearchPlaceholderPanel";
import { ResearchOverviewPanel } from "./ResearchOverviewPanel";
import { ScreenerPlaceholderPanel } from "./ScreenerPlaceholderPanel";

export function ResearchPanel() {
  return (
    <div style={{ display: "grid", gap: "18px" }}>
      <PageHeader
        title="Research"
        subtitle="Static research UI skeleton. Calculations, screeners, backtests, news calls, and AI analysis are locked."
      />
      <ResearchOverviewPanel />
      <IndicatorPlaceholderPanel />
      <ScreenerPlaceholderPanel />
      <BacktestPlaceholderPanel />
      <NewsResearchPlaceholderPanel />
    </div>
  );
}
