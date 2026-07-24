import type {
  ReactNode,
} from "react";

type StatusBadgeProps = {
  children: ReactNode;
  tone?:
    | "neutral"
    | "info"
    | "success"
    | "warning"
    | "danger"
    | "violet";
};

export default function StatusBadge({
  children,
  tone = "neutral",
}: StatusBadgeProps) {
  return (
    <span
      className="nv-status-badge"
      data-tone={tone}
    >
      {children}
    </span>
  );
}
