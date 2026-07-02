import { Card, Badge } from "../../../components/ui";
import { researchModules } from "../contracts/researchUiState";

export function ResearchOverviewPanel() {
  return (
    <Card>
      <h2>Research Overview</h2>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
        {researchModules.map((module) => (
          <Badge key={module} label={`${module}: Locked`} />
        ))}
      </div>
    </Card>
  );
}
