import { Badge, Card } from "../../../components/ui";
import { candidatePreviewState } from "../contracts/strategyUiState";

export function CandidatePlaceholderPanel() {
  return (
    <Card>
      <h2>Candidate Preview</h2>
      <p className="nv-muted">
        Candidate cards are visual only. Scoring and generation remain locked.
      </p>

      <div style={{ display: "grid", gap: "10px", marginTop: "14px" }}>
        {candidatePreviewState.map((candidate) => (
          <div key={candidate.name} className="nv-panel">
            <strong>{candidate.name}</strong>
            <p className="nv-muted" style={{ margin: "6px 0 10px" }}>{candidate.family}</p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
              <Badge label={`Score: ${candidate.score}`} />
              <Badge label={candidate.status} />
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
