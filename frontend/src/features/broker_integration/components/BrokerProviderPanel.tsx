import { Card, MetricTile } from "../../../components/ui";

export function BrokerProviderPanel() {
  return (
    <Card>
      <h2>Provider Boundary</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px" }}>
        <MetricTile label="Provider" value="SnapTrade" />
        <MetricTile label="Mode" value="Skeleton" />
        <MetricTile label="Calls" value="Locked" />
      </div>
    </Card>
  );
}
