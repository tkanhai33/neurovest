import { Card } from "../../../components/ui";

export function CandidatePlaceholderPanel() {
  return (
    <Card>
      <h2>Candidate Placeholder</h2>
      <div style={{ height: "140px", border: "1px dashed var(--panel-soft)", borderRadius: "14px", display: "grid", placeItems: "center", color: "var(--muted)" }}>
        Candidate scoring locked during skeleton phase
      </div>
    </Card>
  );
}
