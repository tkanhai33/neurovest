import { Card, MetricTile, StatusPill } from "../../../components/ui";
import { quotePreviewState } from "../contracts/marketDataUiState";

export function QuotePlaceholderPanel() {
  return (
    <Card>
      <h2>Quote Preview</h2>
      <p className="nv-muted">
        Quote layout is composed, but no backend or provider request is made.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px", marginTop: "14px" }}>
        <MetricTile label="Selected Symbol" value={quotePreviewState.selectedSymbol} />
        <MetricTile label="Last Price" value={quotePreviewState.lastPrice} />
        <MetricTile label="Currency" value={quotePreviewState.currency} />
        <MetricTile label="Provider" value={quotePreviewState.provider} />
        <MetricTile label="Freshness" value={quotePreviewState.freshness} />
      </div>

      <div style={{ marginTop: "14px" }}>
        <StatusPill label={quotePreviewState.contractStatus} />
      </div>
    </Card>
  );
}
