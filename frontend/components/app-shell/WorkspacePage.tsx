import type {
  ReactNode,
} from "react";

import PageContainer from "../ui/PageContainer";

type WorkspacePageProps = {
  children?: ReactNode;
  className?: string;
  context?: ReactNode;
  floating?: ReactNode;
  footer?: ReactNode;
  header: ReactNode;
  metrics?: ReactNode;
  navigation?: ReactNode;
  primary: ReactNode;
  status?: ReactNode;
  testId?: string;
  top?: ReactNode;
};

export default function WorkspacePage({
  children,
  className = "",
  context,
  floating,
  footer,
  header,
  metrics,
  navigation,
  primary,
  status,
  testId,
  top,
}: WorkspacePageProps) {
  return (
    <PageContainer
      data-testid={testId}
      className={className}
    >
      <main className="nv-workspace-page">
        {top && (
          <section className="nv-workspace-top">
            {top}
          </section>
        )}

        <section className="nv-workspace-page-header">
          {header}
        </section>

        {status && (
          <section
            className="nv-workspace-status-strip"
            aria-label="Workspace status"
          >
            {status}
          </section>
        )}

        {context && (
          <section className="nv-workspace-context">
            {context}
          </section>
        )}

        {navigation && (
          <nav
            className="nv-workspace-navigation"
            aria-label="Workspace navigation"
          >
            {navigation}
          </nav>
        )}

        {metrics && (
          <section className="nv-workspace-metrics">
            {metrics}
          </section>
        )}

        <section className="nv-workspace-primary">
          {primary}
        </section>

        {children}

        {footer && (
          <footer className="nv-workspace-footer">
            {footer}
          </footer>
        )}

        {floating}
      </main>
    </PageContainer>
  );
}
