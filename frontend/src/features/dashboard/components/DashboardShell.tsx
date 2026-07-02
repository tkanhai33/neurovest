import { PageHeader } from "../../../components/ui";
import { PhaseProgressPanel } from "./PhaseProgressPanel";
import { StackOverviewPanel } from "./StackOverviewPanel";
import { SystemLockPanel } from "./SystemLockPanel";

export function DashboardShell() {
  return (
    <div style={{ display: "grid", gap: "18px" }}>
      <PageHeader
        title="NeuroVest Dashboard"
        subtitle="Static dashboard skeleton. All execution paths remain locked."
      />
      <PhaseProgressPanel />
      <SystemLockPanel />
      <StackOverviewPanel />
    </div>
  );
}
