import { Badge, Card } from "../../../components/ui";
import { brokerAuthLockState } from "../contracts/brokerIntegrationUiState";

export function BrokerAuthLockedPanel() {
  return (
    <Card>
      <h2>Authentication Locked</h2>
      <p className="nv-muted">
        Broker authentication and token storage remain disabled until contracts certify read-only integration.
      </p>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginTop: "14px" }}>
        {brokerAuthLockState.map((item) => (
          <Badge key={item} label={item} />
        ))}
      </div>
    </Card>
  );
}
