import { Card, MetricTile } from "../../../components/ui";
import { brokerAccountPreviewState } from "../contracts/brokerIntegrationUiState";

export function BrokerAccountPlaceholderPanel() {
  return (
    <Card>
      <h2>Read-Only Account Preview</h2>
      <p className="nv-muted">
        Account layout is ready, but positions, balances, and holdings remain disconnected.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px", marginTop: "14px" }}>
        {brokerAccountPreviewState.map((item) => (
          <MetricTile key={item.label} label={item.label} value={item.value} />
        ))}
      </div>
    </Card>
  );
}
