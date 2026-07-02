import { Card, StatusPill } from "../../../components/ui";

export function SchedulerLockedPanel() {
  return (
    <Card>
      <h2>Scheduler Locked</h2>
      <StatusPill label="No Background Loops" />
      <StatusPill label="No Scheduled Jobs" />
      <StatusPill label="No Runtime Execution" />
    </Card>
  );
}
