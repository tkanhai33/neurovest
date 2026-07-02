import { Badge, Card, StatusPill } from "../../../components/ui";
import { riskModules, riskUiState } from "../contracts/riskUiState";

export function RiskOverviewPanel() {
  return (
    <Card>
      <h2>Risk Overview</h2>
      <p className="nv-muted">
        Risk modules are composed for visibility only. Risk math, approvals, broker paths, and trading remain locked.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))", gap: "12px", marginTop: "14px" }}>
        {riskModules.map((module) => (
          <div key={module.name} className="nv-panel">
            <strong>{module.name}</strong>
            <p className="nv-muted" style={{ margin: "6px 0 10px" }}>{module.role}</p>
            <Badge label={module.status} />
          </div>
        ))}
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginTop: "14px" }}>
        <StatusPill label={`UI Only: ${riskUiState.uiOnly ? "True" : "False"}`} />
        <StatusPill label={`Risk Math: ${riskUiState.riskMathEnabled ? "Enabled" : "Locked"}`} />
        <StatusPill label={`Approvals: ${riskUiState.approvalEngineEnabled ? "Enabled" : "Locked"}`} />
        <StatusPill label={`Trading: ${riskUiState.tradingEnabled ? "Enabled" : "Locked"}`} />
      </div>
    </Card>
  );
}
