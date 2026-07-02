import { Badge, Card, StatusPill } from "../../../components/ui";
import { brokerIntegrationModules, brokerIntegrationUiState } from "../contracts/brokerIntegrationUiState";

export function BrokerOverviewPanel() {
  return (
    <Card>
      <h2>Broker Integration Overview</h2>
      <p className="nv-muted">
        Broker integration is visualized only. Auth, token storage, account sync, orders, and live trading remain locked.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))", gap: "12px", marginTop: "14px" }}>
        {brokerIntegrationModules.map((module) => (
          <div key={module.name} className="nv-panel">
            <strong>{module.name}</strong>
            <p className="nv-muted" style={{ margin: "6px 0 10px" }}>{module.role}</p>
            <Badge label={module.status} />
          </div>
        ))}
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginTop: "14px" }}>
        <StatusPill label={`UI Only: ${brokerIntegrationUiState.uiOnly ? "True" : "False"}`} />
        <StatusPill label={`Broker Calls: ${brokerIntegrationUiState.brokerCallsEnabled ? "Enabled" : "Locked"}`} />
        <StatusPill label={`Orders: ${brokerIntegrationUiState.orderSubmissionEnabled ? "Enabled" : "Locked"}`} />
        <StatusPill label={`Live: ${brokerIntegrationUiState.liveTradingEnabled ? "Enabled" : "Locked"}`} />
      </div>
    </Card>
  );
}
