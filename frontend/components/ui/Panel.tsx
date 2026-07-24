import type {
  HTMLAttributes,
  ReactNode,
} from "react";

type PanelProps =
  HTMLAttributes<HTMLElement> & {
    children: ReactNode;
    variant?:
      | "default"
      | "elevated"
      | "muted";
  };

export default function Panel({
  children,
  variant = "default",
  className = "",
  ...props
}: PanelProps) {
  return (
    <section
      className={
        `nv-panel nv-panel-${variant} ${className}`
      }
      {...props}
    >
      {children}
    </section>
  );
}
