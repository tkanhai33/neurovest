import type {
  HTMLAttributes,
  ReactNode,
} from "react";

type PageContainerProps =
  HTMLAttributes<HTMLElement> & {
    children: ReactNode;
    density?:
      | "comfortable"
      | "compact";
  };

export default function PageContainer({
  children,
  density = "comfortable",
  className = "",
  ...props
}: PageContainerProps) {
  const densityClass =
    density === "compact"
      ? "nv-page-container-compact"
      : "";

  return (
    <main
      className={[
        "nv-page-container",
        densityClass,
        className,
      ]
        .filter(Boolean)
        .join(" ")}
      {...props}
    >
      {children}
    </main>
  );
}
