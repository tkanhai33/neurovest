import { Card, MetricTile } from "../../../components/ui";
import { backtestPreviewState } from "../contracts/researchUiState";

export function BacktestPlaceholderPanel() {
  return (
    <Card>
      <h2>Backtest Preview</h2>
      <p className="nv-muted">
        Backtest shell is composed, but execution remains locked.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px", marginTop: "14px" }}>
        <MetricTile label="Symbol" value={backtestPreviewState.selectedSymbol} />
        <MetricTile label="Strategy Family" value={backtestPreviewState.strategyFamily} />
        <MetricTile label="Date Range" value={backtestPreviewState.dateRange} />
        <MetricTile label="Execution" value={backtestPreviewState.executionStatus} />
        <MetricTile label="Result" value={backtestPreviewState.resultStatus} />
      </div>
    </Card>
  );
}
