import { Card, MetricTile } from "../../../components/ui";
import { simulatedFillPreviewState } from "../contracts/paperTradingUiState";

export function SimulatedFillPlaceholderPanel() {
  return (
    <Card>
      <h2>Simulated Fill Preview</h2>
      <p className="nv-muted">
        Fill logic is displayed only. No simulated execution occurs.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px", marginTop: "14px" }}>
        {simulatedFillPreviewState.map((item) => (
          <MetricTile key={item.label} label={item.label} value={item.value} />
        ))}
      </div>
    </Card>
  );
}
