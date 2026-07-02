import { Badge, Card } from "../../../components/ui";
import { brokerOrderLockState } from "../contracts/brokerIntegrationUiState";

export function BrokerOrderLockedPanel() {
  return (
    <Card>
      <h2>Order Submission Locked</h2>
      <p className="nv-muted">
        Order submission, execution, canary mode, and live trading are fully locked.
      </p>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginTop: "14px" }}>
        {brokerOrderLockState.map((item) => (
          <Badge key={item} label={item} />
        ))}
      </div>
    </Card>
  );
}
