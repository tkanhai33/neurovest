import { CommandGridPanel } from "./CommandGridPanel";
import { DashboardHeroPanel } from "./DashboardHeroPanel";
import { PhaseProgressPanel } from "./PhaseProgressPanel";
import { StackOverviewPanel } from "./StackOverviewPanel";
import { SystemLockPanel } from "./SystemLockPanel";
import { SystemFlowMapPanel } from "./SystemFlowMapPanel";
import { RoleVisibilityPreviewPanel } from "./RoleVisibilityPreviewPanel";
import { RoleSurfaceSummaryPanel } from "./RoleSurfaceSummaryPanel";
import { RoleDashboardPreviewPanel } from "./RoleDashboardPreviewPanel";
import { DashboardNavigationMatrixPanel } from "./DashboardNavigationMatrixPanel";
import { DeveloperDashboardCompositionPanel } from "./DeveloperDashboardCompositionPanel";
import { AdminDashboardCompositionPanel } from "./AdminDashboardCompositionPanel";
import { UserDashboardCompositionPanel } from "./UserDashboardCompositionPanel";

export function DashboardShell() {
  return (
    <div className="nv-grid">
      <DashboardHeroPanel />
      <CommandGridPanel />
      <SystemFlowMapPanel />
      <RoleVisibilityPreviewPanel />
      <RoleSurfaceSummaryPanel />
      <RoleDashboardPreviewPanel />
      <DashboardNavigationMatrixPanel />
      <DeveloperDashboardCompositionPanel />
      <AdminDashboardCompositionPanel />
      <UserDashboardCompositionPanel />
      <PhaseProgressPanel />
      <SystemLockPanel />
      <StackOverviewPanel />
    </div>
  );
}
