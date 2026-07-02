import { Card, MetricTile } from "../../../components/ui";

export function BrokerAccountPlaceholderPanel() {
  return (
    <Card>
      <h2>Read-Only Account Placeholder</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px" }}>
        <MetricTile label="Account Sync" value="Locked" />
        <MetricTile label="Positions" value="Disabled" />
        <MetricTile label="Balances" value="Disabled" />
      </div>
    </Card>
  );
}
