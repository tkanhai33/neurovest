import type {
  ReactNode,
} from "react";

type StatusMessageProps = {
  children: ReactNode;
  tone?:
    | "info"
    | "success"
    | "warning"
    | "danger";
};

export default function StatusMessage({
  children,
  tone = "info",
}: StatusMessageProps) {
  return (
    <div
      className="nv-status-message"
      data-tone={tone}
      role={
        tone === "danger"
          ? "alert"
          : "status"
      }
    >
      {children}
    </div>
  );
}
