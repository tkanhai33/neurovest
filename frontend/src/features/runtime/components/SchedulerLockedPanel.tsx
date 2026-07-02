import { Badge, Card } from "../../../components/ui";
import { schedulerLockState } from "../contracts/runtimeUiState";

export function SchedulerLockedPanel() {
  return (
    <Card>
      <h2>Scheduler Locked</h2>
      <p className="nv-muted">
        Scheduler visualization exists, but no jobs, loops, or runtime actions are enabled.
      </p>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginTop: "14px" }}>
        {schedulerLockState.map((item) => (
          <Badge key={item} label={item} />
        ))}
      </div>
    </Card>
  );
}
