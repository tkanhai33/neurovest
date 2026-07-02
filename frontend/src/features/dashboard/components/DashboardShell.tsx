import { CommandGridPanel } from "./CommandGridPanel";
import { DashboardHeroPanel } from "./DashboardHeroPanel";
import { PhaseProgressPanel } from "./PhaseProgressPanel";
import { StackOverviewPanel } from "./StackOverviewPanel";
import { SystemLockPanel } from "./SystemLockPanel";
import { SystemFlowMapPanel } from "./SystemFlowMapPanel";

export function DashboardShell() {
  return (
    <div className="nv-grid">
      <DashboardHeroPanel />
      <CommandGridPanel />
      <SystemFlowMapPanel />
      <PhaseProgressPanel />
      <SystemLockPanel />
      <StackOverviewPanel />
    </div>
  );
}
