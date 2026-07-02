import { Card, Badge } from "../../../components/ui";
import { strategyModules } from "../contracts/strategyUiState";

export function StrategyOverviewPanel() {
  return (
    <Card>
      <h2>Strategy Overview</h2>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
        {strategyModules.map((module) => (
          <Badge key={module} label={`${module}: Locked`} />
        ))}
      </div>
    </Card>
  );
}
