import type {
  ReactNode,
} from "react";

type PageHeaderProps = {
  eyebrow: string;
  title: string;
  description?: string;
  actions?: ReactNode;
  badge?: ReactNode;
};

export default function PageHeader({
  eyebrow,
  title,
  description,
  actions,
  badge,
}: PageHeaderProps) {
  return (
    <header className="nv-page-header">
      <div className="nv-page-header-copy">
        <div className="nv-page-header-meta">
          <p className="nv-eyebrow">
            {eyebrow}
          </p>

          {badge}
        </div>

        <h1 className="nv-page-title">
          {title}
        </h1>

        {description && (
          <p className="nv-page-description">
            {description}
          </p>
        )}
      </div>

      {actions && (
        <div className="nv-page-actions">
          {actions}
        </div>
      )}
    </header>
  );
}
