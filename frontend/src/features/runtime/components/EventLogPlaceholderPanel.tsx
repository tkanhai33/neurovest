import { Badge, Card } from "../../../components/ui";
import { runtimeEventPreviewState } from "../contracts/runtimeUiState";

export function EventLogPlaceholderPanel() {
  return (
    <Card>
      <h2>Runtime Event Log Preview</h2>
      <p className="nv-muted">
        Event log is static and reflects UI composition checkpoints only.
      </p>

      <div style={{ display: "grid", gap: "10px", marginTop: "14px" }}>
        {runtimeEventPreviewState.map((item) => (
          <div key={item.event} className="nv-panel">
            <strong>{item.event}</strong>
            <div style={{ marginTop: "8px" }}>
              <Badge label={item.status} />
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
