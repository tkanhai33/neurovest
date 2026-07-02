import { Badge, Card } from "../../../components/ui";
import { holdingsPreviewState } from "../contracts/portfolioUiState";

export function HoldingsPlaceholderPanel() {
  return (
    <Card>
      <h2>Holdings Preview</h2>
      <p className="nv-muted">
        Holdings layout is ready, but quantities and values remain locked.
      </p>

      <div style={{ display: "grid", gap: "10px", marginTop: "14px" }}>
        {holdingsPreviewState.map((holding) => (
          <div key={holding.symbol} className="nv-panel">
            <strong>{holding.symbol}</strong>
            <p className="nv-muted" style={{ margin: "6px 0 10px" }}>{holding.name}</p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
              <Badge label={`Weight: ${holding.weight}`} />
              <Badge label={`Qty: ${holding.quantity}`} />
              <Badge label={`Value: ${holding.value}`} />
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
