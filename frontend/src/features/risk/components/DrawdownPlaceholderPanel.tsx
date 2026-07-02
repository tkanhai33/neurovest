import { Card, MetricTile } from "../../../components/ui";
import { drawdownPreviewState } from "../contracts/riskUiState";

export function DrawdownPlaceholderPanel() {
  return (
    <Card>
      <h2>Drawdown Preview</h2>
      <p className="nv-muted">
        Drawdown controls are visible, but no loss math or kill-switch logic runs.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px", marginTop: "14px" }}>
        {drawdownPreviewState.map((item) => (
          <MetricTile key={item.label} label={item.label} value={item.value} />
        ))}
      </div>
    </Card>
  );
}
