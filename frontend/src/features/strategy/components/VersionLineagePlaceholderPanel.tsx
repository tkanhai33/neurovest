import { Card } from "../../../components/ui";

export function VersionLineagePlaceholderPanel() {
  return (
    <Card>
      <h2>Version / Lineage Placeholder</h2>
      <p style={{ color: "var(--muted)" }}>
        Strategy versions, parent lineage, and promotion review are locked during the skeleton phase.
      </p>
    </Card>
  );
}
