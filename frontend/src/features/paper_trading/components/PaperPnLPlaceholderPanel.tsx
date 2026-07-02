import { Card, MetricTile } from "../../../components/ui";
import { paperPnlPreviewState } from "../contracts/paperTradingUiState";

export function PaperPnLPlaceholderPanel() {
  return (
    <Card>
      <h2>Paper PnL Preview</h2>
      <p className="nv-muted">
        PnL layout is ready, but no calculations are active.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px", marginTop: "14px" }}>
        {paperPnlPreviewState.map((item) => (
          <MetricTile key={item.label} label={item.label} value={item.value} />
        ))}
      </div>
    </Card>
  );
}
