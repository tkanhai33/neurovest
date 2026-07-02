import { Badge, Card } from "../../../components/ui";
import { dashboardSystemFlow } from "../contracts/dashboardState";

export function SystemFlowMapPanel() {
  return (
    <Card>
      <h2>NeuroVest Brain Map</h2>
      <p className="nv-muted">
        Shared system flow visualization. Role filtering, backend calls, runtime execution, and broker paths remain locked.
      </p>

      <div style={{ display: "grid", gap: "10px", marginTop: "14px" }}>
        {dashboardSystemFlow.map((node, index) => (
          <div key={node.name} className="nv-panel">
            <strong>{index + 1}. {node.name}</strong>
            <p className="nv-muted" style={{ margin: "6px 0 10px" }}>{node.role}</p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
              <Badge label={node.status} />
              <Badge label={node.visibility} />
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
