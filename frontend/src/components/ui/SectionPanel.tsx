export function SectionPanel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="nv-panel">
      <h2>{title}</h2>
      {children}
    </section>
  );
}
