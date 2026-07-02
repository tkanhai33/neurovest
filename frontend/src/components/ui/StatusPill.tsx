export function StatusPill({ label }: { label: string }) {
  return (
    <span style={{ color: "var(--safe)", border: "1px solid var(--safe)", borderRadius: "999px", padding: "4px 10px" }}>
      {label}
    </span>
  );
}
