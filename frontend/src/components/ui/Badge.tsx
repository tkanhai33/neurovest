export function Badge({ label }: { label: string }) {
  return (
    <span style={{ border: "1px solid var(--panel-soft)", borderRadius: "999px", padding: "4px 10px" }}>
      {label}
    </span>
  );
}
