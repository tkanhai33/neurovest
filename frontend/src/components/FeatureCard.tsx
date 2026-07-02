export function FeatureCard({
  title,
  status
}: {
  title: string;
  status: string;
}) {
  return (
    <section style={{ background: "var(--panel)", padding: "18px", borderRadius: "14px" }}>
      <h2 style={{ marginTop: 0 }}>{title}</h2>
      <p style={{ color: "var(--muted)" }}>{status}</p>
    </section>
  );
}
