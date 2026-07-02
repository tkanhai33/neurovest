import { PageHeader } from "../../../components/ui";
import { EventLogPlaceholderPanel } from "./EventLogPlaceholderPanel";
import { MutationLockedPanel } from "./MutationLockedPanel";
import { RuntimeOverviewPanel } from "./RuntimeOverviewPanel";
import { RuntimeStatusPanel } from "./RuntimeStatusPanel";
import { SchedulerLockedPanel } from "./SchedulerLockedPanel";
import { WorkflowPlaceholderPanel } from "./WorkflowPlaceholderPanel";

export function RuntimePanel() {
  return (
    <div style={{ display: "grid", gap: "18px" }}>
      <PageHeader
        title="Runtime"
        subtitle="Static runtime UI skeleton. Scheduler, loops, workflows, mutation, broker, and trading paths are locked."
      />
      <RuntimeOverviewPanel />
      <RuntimeStatusPanel />
      <SchedulerLockedPanel />
      <WorkflowPlaceholderPanel />
      <EventLogPlaceholderPanel />
      <MutationLockedPanel />
    </div>
  );
}
