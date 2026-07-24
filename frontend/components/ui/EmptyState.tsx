import type {
  ReactNode,
} from "react";

type EmptyStateProps = {
  title: string;
  description: string;
  action?: ReactNode;
};

export default function EmptyState({
  title,
  description,
  action,
}: EmptyStateProps) {
  return (
    <div className="nv-empty-state">
      <div
        className="nv-empty-state-mark"
        aria-hidden="true"
      >
        N
      </div>

      <h2 className="nv-empty-state-title">
        {title}
      </h2>

      <p className="nv-empty-state-description">
        {description}
      </p>

      {action && (
        <div className="nv-empty-state-action">
          {action}
        </div>
      )}
    </div>
  );
}
