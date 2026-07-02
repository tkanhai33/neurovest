import { Card, Badge } from "../../../components/ui";
import { dashboardStacks } from "../contracts/dashboardState";

export function StackOverviewPanel() {
  return (
    <Card>
      <h2>Stack Overview</h2>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
        {dashboardStacks.map((stack) => (
          <Badge key={stack} label={`${stack}: Skeleton`} />
        ))}
      </div>
    </Card>
  );
}
