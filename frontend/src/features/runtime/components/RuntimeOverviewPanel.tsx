import { Badge, Card, StatusPill } from "../../../components/ui";
import { runtimeModules, runtimeUiState } from "../contracts/runtimeUiState";

export function RuntimeOverviewPanel() {
  return (
    <Card>
      <h2>Runtime Overview</h2>
      <p className="nv-muted">
        Runtime is visualized only. Scheduler, workflows, mutation, broker paths, and trading remain locked.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))", gap: "12px", marginTop: "14px" }}>
        {runtimeModules.map((module) => (
          <div key={module.name} className="nv-panel">
            <strong>{module.name}</strong>
            <p className="nv-muted" style={{ margin: "6px 0 10px" }}>{module.role}</p>
            <Badge label={module.status} />
          </div>
        ))}
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginTop: "14px" }}>
        <StatusPill label={`UI Only: ${runtimeUiState.uiOnly ? "True" : "False"}`} />
        <StatusPill label={`Scheduler: ${runtimeUiState.schedulerEnabled ? "Enabled" : "Locked"}`} />
        <StatusPill label={`Workflows: ${runtimeUiState.workflowExecutionEnabled ? "Enabled" : "Locked"}`} />
        <StatusPill label={`Mutation: ${runtimeUiState.mutationEnabled ? "Enabled" : "Locked"}`} />
      </div>
    </Card>
  );
}
