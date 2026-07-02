import { Card, Badge } from "../../../components/ui";
import { paperTradingModules } from "../contracts/paperTradingUiState";

export function PaperTradingOverviewPanel() {
  return (
    <Card>
      <h2>Paper Trading Overview</h2>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
        {paperTradingModules.map((module) => (
          <Badge key={module} label={`${module}: Locked`} />
        ))}
      </div>
    </Card>
  );
}
