export function MetricTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="nv-metric">
      <div className="nv-muted">{label}</div>
      <strong>{value}</strong>
    </div>
  );
}
