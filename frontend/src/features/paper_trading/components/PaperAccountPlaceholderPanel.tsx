import { Card, MetricTile } from "../../../components/ui";
import { paperAccountPreviewState } from "../contracts/paperTradingUiState";

export function PaperAccountPlaceholderPanel() {
  return (
    <Card>
      <h2>Paper Account Preview</h2>
      <p className="nv-muted">
        Paper account layout is ready, but no simulated account state is active.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px", marginTop: "14px" }}>
        {paperAccountPreviewState.map((item) => (
          <MetricTile key={item.label} label={item.label} value={item.value} />
        ))}
      </div>
    </Card>
  );
}
