import type {
  ReactNode,
} from "react";

type StatCardProps = {
  label: string;
  value: ReactNode;
  detail?: ReactNode;
  accent?:
    | "cyan"
    | "emerald"
    | "amber"
    | "red"
    | "violet";
};

export default function StatCard({
  label,
  value,
  detail,
  accent = "cyan",
}: StatCardProps) {
  return (
    <article
      className="nv-stat-card"
      data-accent={accent}
    >
      <p className="nv-stat-label">
        {label}
      </p>

      <div className="nv-stat-value">
        {value}
      </div>

      {detail && (
        <div className="nv-stat-detail">
          {detail}
        </div>
      )}
    </article>
  );
}
