import type {
  ReactNode,
} from "react";

type SectionHeaderProps = {
  eyebrow?: string;
  title: string;
  description?: string;
  badge?: ReactNode;
  actions?: ReactNode;
  className?: string;
};

export default function SectionHeader({
  eyebrow,
  title,
  description,
  badge,
  actions,
  className = "",
}: SectionHeaderProps) {
  return (
    <header
      className={[
        "nv-section-header",
        className,
      ]
        .filter(Boolean)
        .join(" ")}
    >
      <div className="nv-section-header-copy">
        {eyebrow ? (
          <p className="nv-eyebrow">
            {eyebrow}
          </p>
        ) : null}

        <h2 className="nv-section-title">
          {title}
        </h2>

        {description ? (
          <p className="nv-section-description">
            {description}
          </p>
        ) : null}
      </div>

      {badge || actions ? (
        <div className="nv-section-header-actions">
          {badge}
          {actions}
        </div>
      ) : null}
    </header>
  );
}
