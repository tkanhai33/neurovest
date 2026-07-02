import { Badge, Card } from "../../../components/ui";
import { newsResearchPreviewState } from "../contracts/researchUiState";

export function NewsResearchPlaceholderPanel() {
  return (
    <Card>
      <h2>News / Research Preview</h2>
      <p className="nv-muted">
        News, summaries, and AI context are visual only during this phase.
      </p>

      <div style={{ display: "grid", gap: "10px", marginTop: "14px" }}>
        {newsResearchPreviewState.map((item) => (
          <div key={item.source} className="nv-panel">
            <strong>{item.source}</strong>
            <p className="nv-muted" style={{ margin: "6px 0 10px" }}>{item.note}</p>
            <Badge label={item.status} />
          </div>
        ))}
      </div>
    </Card>
  );
}
