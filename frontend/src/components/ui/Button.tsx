export function Button({ label }: { label: string }) {
  return (
    <button style={{ padding: "10px 14px", borderRadius: "10px", border: "0", cursor: "default" }}>
      {label}
    </button>
  );
}
