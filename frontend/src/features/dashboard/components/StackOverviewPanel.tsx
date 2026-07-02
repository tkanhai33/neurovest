import { Card, Badge } from "../../../components/ui";
import { dashboardStacks } from "../contracts/dashboardState";

export function StackOverviewPanel() {
  return (
    <Card>
      <h2>Certified Stack Overview</h2>
      <p className="nv-muted">Every stack is present as a static locked shell.</p>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
        {dashboardStacks.map((stack) => (
          <Badge key={stack} label={`${stack}: Certified Shell`} />
        ))}
      </div>
    </Card>
  );
}
