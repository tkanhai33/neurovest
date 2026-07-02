import { Badge, Card } from "../../../components/ui";
import { paperPositionPreviewState } from "../contracts/paperTradingUiState";

export function PaperPositionPlaceholderPanel() {
  return (
    <Card>
      <h2>Paper Position Preview</h2>
      <p className="nv-muted">
        Position cards are visual only. No simulated positions are created or mutated.
      </p>

      <div style={{ display: "grid", gap: "10px", marginTop: "14px" }}>
        {paperPositionPreviewState.map((position) => (
          <div key={position.symbol} className="nv-panel">
            <strong>{position.symbol}</strong>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", marginTop: "8px" }}>
              <Badge label={`Qty: ${position.quantity}`} />
              <Badge label={`Value: ${position.value}`} />
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
