import { Badge, Card, StatusPill } from "../../../components/ui";
import { strategyModules, strategyUiState } from "../contracts/strategyUiState";

export function StrategyOverviewPanel() {
  return (
    <Card>
      <h2>Strategy Overview</h2>
      <p className="nv-muted">
        Strategy modules are composed for visibility only. Signals, scoring, and promotion remain locked.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))", gap: "12px", marginTop: "14px" }}>
        {strategyModules.map((module) => (
          <div key={module.name} className="nv-panel">
            <strong>{module.name}</strong>
            <p className="nv-muted" style={{ margin: "6px 0 10px" }}>{module.role}</p>
            <Badge label={module.status} />
          </div>
        ))}
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginTop: "14px" }}>
        <StatusPill label={`UI Only: ${strategyUiState.uiOnly ? "True" : "False"}`} />
        <StatusPill label={`Signal Generation: ${strategyUiState.signalGenerationEnabled ? "Enabled" : "Locked"}`} />
        <StatusPill label={`Promotion: ${strategyUiState.promotionEnabled ? "Enabled" : "Locked"}`} />
      </div>
    </Card>
  );
}
