import type {
  ButtonHTMLAttributes,
  ReactNode,
} from "react";

type ButtonProps =
  ButtonHTMLAttributes<HTMLButtonElement> & {
    children: ReactNode;
    variant?:
      | "primary"
      | "secondary"
      | "ghost"
      | "danger";
    size?: "sm" | "md" | "lg";
  };

export default function Button({
  children,
  variant = "primary",
  size = "md",
  className = "",
  type = "button",
  ...props
}: ButtonProps) {
  return (
    <button
      type={type}
      className={
        `nv-button nv-button-${variant} ` +
        `nv-button-${size} ${className}`
      }
      {...props}
    >
      {children}
    </button>
  );
}
