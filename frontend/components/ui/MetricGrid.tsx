import type {
  HTMLAttributes,
  ReactNode,
} from "react";

type MetricGridProps =
  HTMLAttributes<HTMLDivElement> & {
    children: ReactNode;
    columns?:
      | 2
      | 3
      | 4
      | 5;
  };

const columnClasses = {
  2: "nv-metric-grid-2",
  3: "nv-metric-grid-3",
  4: "nv-metric-grid-4",
  5: "nv-metric-grid-5",
} as const;

export default function MetricGrid({
  children,
  columns = 3,
  className = "",
  ...props
}: MetricGridProps) {
  return (
    <div
      className={[
        "nv-metric-grid",
        columnClasses[columns],
        className,
      ]
        .filter(Boolean)
        .join(" ")}
      {...props}
    >
      {children}
    </div>
  );
}
