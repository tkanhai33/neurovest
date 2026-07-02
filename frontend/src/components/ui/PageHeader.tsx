export function PageHeader({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <header>
      <h1>{title}</h1>
      <p style={{ color: "var(--muted)" }}>{subtitle}</p>
    </header>
  );
}
