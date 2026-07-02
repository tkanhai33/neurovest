import { Badge, Card } from "../../../components/ui";
import { simulatedOrderLockState } from "../contracts/paperTradingUiState";

export function SimulatedOrderPlaceholderPanel() {
  return (
    <Card>
      <h2>Simulated Order Preview</h2>
      <p className="nv-muted">
        Simulated order creation is fully locked until the paper trading engine is certified.
      </p>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginTop: "14px" }}>
        {simulatedOrderLockState.map((item) => (
          <Badge key={item} label={item} />
        ))}
      </div>
    </Card>
  );
}
