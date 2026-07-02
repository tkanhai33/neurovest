import { Card, MetricTile } from "../../../components/ui";
import { cashBalanceState } from "../contracts/portfolioUiState";

export function CashBalancePanel() {
  return (
    <Card>
      <h2>Cash Balance</h2>
      <p className="nv-muted">
        Cash state is static until portfolio services and broker read paths are certified.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px", marginTop: "14px" }}>
        <MetricTile label="Currency" value={cashBalanceState.currency} />
        <MetricTile label="Cash" value={cashBalanceState.cash} />
        <MetricTile label="Settled Cash" value={cashBalanceState.settledCash} />
        <MetricTile label="Unsettled Cash" value={cashBalanceState.unsettledCash} />
        <MetricTile label="Source" value={cashBalanceState.source} />
      </div>
    </Card>
  );
}
