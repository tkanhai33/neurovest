import { CommandGridPanel } from "./CommandGridPanel";
import { DashboardHeroPanel } from "./DashboardHeroPanel";
import { PhaseProgressPanel } from "./PhaseProgressPanel";
import { StackOverviewPanel } from "./StackOverviewPanel";
import { SystemLockPanel } from "./SystemLockPanel";
import { SystemFlowMapPanel } from "./SystemFlowMapPanel";
import { RoleVisibilityPreviewPanel } from "./RoleVisibilityPreviewPanel";
import { RoleSurfaceSummaryPanel } from "./RoleSurfaceSummaryPanel";

export function DashboardShell() {
  return (
    <div className="nv-grid">
      <DashboardHeroPanel />
      <CommandGridPanel />
      <SystemFlowMapPanel />
      <RoleVisibilityPreviewPanel />
      <RoleSurfaceSummaryPanel />
      <PhaseProgressPanel />
      <SystemLockPanel />
      <StackOverviewPanel />
    </div>
  );
}
