import { Card, MetricTile } from "../../../components/ui";
import { brokerProviderPreviewState } from "../contracts/brokerIntegrationUiState";

export function BrokerProviderPanel() {
  return (
    <Card>
      <h2>Provider Boundary</h2>
      <p className="nv-muted">
        SnapTrade is represented as the broker boundary, but no broker request is made.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px", marginTop: "14px" }}>
        {brokerProviderPreviewState.map((item) => (
          <MetricTile key={item.label} label={item.label} value={item.value} />
        ))}
      </div>
    </Card>
  );
}
