import { Card, Badge } from "../../../components/ui";
import { riskModules } from "../contracts/riskUiState";

export function RiskOverviewPanel() {
  return (
    <Card>
      <h2>Risk Overview</h2>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
        {riskModules.map((module) => (
          <Badge key={module} label={`${module}: Locked`} />
        ))}
      </div>
    </Card>
  );
}
