import { Card, Badge } from "../../../components/ui";
import { runtimeModules } from "../contracts/runtimeUiState";

export function RuntimeOverviewPanel() {
  return (
    <Card>
      <h2>Runtime Overview</h2>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
        {runtimeModules.map((module) => (
          <Badge key={module} label={`${module}: Locked`} />
        ))}
      </div>
    </Card>
  );
}
