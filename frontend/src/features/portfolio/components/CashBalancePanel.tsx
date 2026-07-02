import { Card, MetricTile } from "../../../components/ui";

export function CashBalancePanel() {
  return (
    <Card>
      <h2>Cash & Balance</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px" }}>
        <MetricTile label="Currency" value="CAD" />
        <MetricTile label="Available Cash" value="Locked" />
        <MetricTile label="Buying Power" value="Disabled" />
      </div>
    </Card>
  );
}
