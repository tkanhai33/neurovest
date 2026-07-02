import { Badge, Card, StatusPill } from "../../../components/ui";
import { researchModules, researchUiState } from "../contracts/researchUiState";

export function ResearchOverviewPanel() {
  return (
    <Card>
      <h2>Research Overview</h2>
      <p className="nv-muted">
        Research modules are composed for visibility only. Calculations and AI analysis remain locked.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))", gap: "12px", marginTop: "14px" }}>
        {researchModules.map((module) => (
          <div key={module.name} className="nv-panel">
            <strong>{module.name}</strong>
            <p className="nv-muted" style={{ margin: "6px 0 10px" }}>{module.role}</p>
            <Badge label={module.status} />
          </div>
        ))}
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginTop: "14px" }}>
        <StatusPill label={`UI Only: ${researchUiState.uiOnly ? "True" : "False"}`} />
        <StatusPill label={`Market Data Calls: ${researchUiState.marketDataCallsEnabled ? "Enabled" : "Locked"}`} />
        <StatusPill label={`AI Calls: ${researchUiState.aiCallsEnabled ? "Enabled" : "Locked"}`} />
      </div>
    </Card>
  );
}
