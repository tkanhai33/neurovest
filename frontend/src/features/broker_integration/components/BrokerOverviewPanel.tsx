import { Card, Badge } from "../../../components/ui";
import { brokerIntegrationModules } from "../contracts/brokerIntegrationUiState";

export function BrokerOverviewPanel() {
  return (
    <Card>
      <h2>Broker Integration Overview</h2>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
        {brokerIntegrationModules.map((module) => (
          <Badge key={module} label={`${module}: Locked`} />
        ))}
      </div>
    </Card>
  );
}
