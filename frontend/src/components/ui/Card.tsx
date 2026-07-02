export function Card({ children }: { children: React.ReactNode }) {
  return (
    <section style={{ background: "var(--panel)", borderRadius: "14px", padding: "18px" }}>
      {children}
    </section>
  );
}
