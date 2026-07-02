export function SectionPanel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section style={{ background: "var(--panel)", borderRadius: "16px", padding: "20px" }}>
      <h2>{title}</h2>
      {children}
    </section>
  );
}
