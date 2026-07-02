export function MetricTile({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ background: "var(--panel-soft)", borderRadius: "14px", padding: "16px" }}>
      <div style={{ color: "var(--muted)" }}>{label}</div>
      <strong>{value}</strong>
    </div>
  );
}
