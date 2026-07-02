import { Badge, Card, StatusPill } from "../../../components/ui";
import { paperTradingModules, paperTradingUiState } from "../contracts/paperTradingUiState";

export function PaperTradingOverviewPanel() {
  return (
    <Card>
      <h2>Paper Trading Overview</h2>
      <p className="nv-muted">
        Paper trading is visual only. Orders, fills, positions, PnL, broker paths, and trading remain locked.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))", gap: "12px", marginTop: "14px" }}>
        {paperTradingModules.map((module) => (
          <div key={module.name} className="nv-panel">
            <strong>{module.name}</strong>
            <p className="nv-muted" style={{ margin: "6px 0 10px" }}>{module.role}</p>
            <Badge label={module.status} />
          </div>
        ))}
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginTop: "14px" }}>
        <StatusPill label={`UI Only: ${paperTradingUiState.uiOnly ? "True" : "False"}`} />
        <StatusPill label={`Orders: ${paperTradingUiState.simulatedOrderEngineEnabled ? "Enabled" : "Locked"}`} />
        <StatusPill label={`Fills: ${paperTradingUiState.simulatedFillEngineEnabled ? "Enabled" : "Locked"}`} />
        <StatusPill label={`Trading: ${paperTradingUiState.tradingEnabled ? "Enabled" : "Locked"}`} />
      </div>
    </Card>
  );
}
