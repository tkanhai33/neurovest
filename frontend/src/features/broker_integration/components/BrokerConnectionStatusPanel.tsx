import { Badge, Card } from "../../../components/ui";
import { brokerConnectionPreviewState } from "../contracts/brokerIntegrationUiState";

export function BrokerConnectionStatusPanel() {
  return (
    <Card>
      <h2>Connection Status</h2>
      <p className="nv-muted">
        Connection state is static. No account or provider health request is active.
      </p>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginTop: "14px" }}>
        {brokerConnectionPreviewState.map((item) => (
          <Badge key={item} label={item} />
        ))}
      </div>
    </Card>
  );
}
