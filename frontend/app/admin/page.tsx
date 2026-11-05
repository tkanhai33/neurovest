import Link from "next/link";

import PageHeader from "../../components/app-shell/PageHeader";
import WorkspacePage from "../../components/app-shell/WorkspacePage";

import {
  Panel,
  StatusBadge,
} from "../../components/ui";

type AdminWorkspaceCard = {
  capability: string;
  description: string;
  href: string;
  status: string;
  title: string;
  tone:
    | "info"
    | "success"
    | "warning"
    | "violet";
};

const workspaces: AdminWorkspaceCard[] = [
  {
    title: "Execution Control",
    description:
      "Review the server-authoritative operating mode, enable controlled paper simulation, lock execution, or activate the persistent emergency stop.",
    href: "/admin/execution-control",
    status: "Safety control",
    tone: "warning",
    capability:
      "SAFE · SIMULATION · LOCKED · EMERGENCY STOP",
  },
  {
    title: "User Management",
    description:
      "Manage canonical identities, account access, password controls, temporary credentials, and account closure.",
    href: "/admin/users",
    status: "Operational",
    tone: "success",
    capability: "Identity operations",
  },
  {
    title: "Session Administration",
    description:
      "Inspect authenticated sessions and manage controlled session-revocation workflows.",
    href: "/admin/sessions",
    status: "Restricted",
    tone: "warning",
    capability: "Access control",
  },
  {
    title: "Decision Audit",
    description:
      "Review immutable decisions, administrative events, and read-only system history.",
    href: "/admin/audit",
    status: "Read only",
    tone: "info",
    capability: "Audit ledger",
  },
  {
    title: "Support Tickets",
    description:
      "Review user-reported issues and controlled support workflows.",
    href: "/admin/tickets",
    status: "Available",
    tone: "info",
    capability: "Support operations",
  },
  {
    title: "User Statistics",
    description:
      "Inspect aggregate platform usage and account-level operational statistics.",
    href: "/admin/user-stats",
    status: "Available",
    tone: "violet",
    capability: "Platform reporting",
  },
  {
    title: "User Workspace Preview",
    description:
      "Inspect the customer-facing workspace without changing authenticated role truth.",
    href: "/admin/user-dashboard",
    status: "Preview",
    tone: "violet",
    capability: "Controlled preview",
  },
];

export default function AdminPage() {
  const header = (
    <PageHeader
      eyebrow="NeuroVest Administration"
      title="Platform operations."
      description="Identity, access, support, audit, and account oversight within a controlled administrative boundary."
      badge={
        <StatusBadge tone="violet">
          Elevated access
        </StatusBadge>
      }
      actions={
        <Link
          href="/admin/users"
          className="nv-button nv-button-primary nv-button-lg"
        >
          Manage users
        </Link>
      }
    />
  );

  const status = (
    <>
      <Panel
        variant="elevated"
        className="nv-workspace-status-item"
      >
        <p className="nv-stat-label">
          Authorization
        </p>

        <p className="nv-workspace-status-value">
          Server authoritative
        </p>

        <p className="nv-workspace-status-description">
          Administrative access is resolved from the authenticated backend identity.
        </p>
      </Panel>

      <Panel
        variant="elevated"
        className="nv-workspace-status-item"
      >
        <p className="nv-stat-label">
          Execution policy
        </p>

        <p className="nv-workspace-status-value">
          Trading disabled
        </p>

        <p className="nv-workspace-status-description">
          Administrative controls cannot activate broker execution.
        </p>
      </Panel>

      <Panel
        variant="elevated"
        className="nv-workspace-status-item"
      >
        <p className="nv-stat-label">
          Environment
        </p>

        <p className="nv-workspace-status-value">
          Controlled development
        </p>

        <p className="nv-workspace-status-description">
          Administrative services are operating inside the qualified environment.
        </p>
      </Panel>
    </>
  );

  const navigation = (
    <>
      <div className="nv-workspace-section-heading">
        <div>
          <p className="nv-eyebrow">
            Administrative workspace
          </p>

          <h2 className="nv-section-title">
            Operations directory
          </h2>

          <p className="nv-section-description">
            Select the operational area required for the current administrative task.
          </p>
        </div>

        <StatusBadge tone="success">
          Identity services connected
        </StatusBadge>
      </div>

      <div className="nv-admin-directory">
        {workspaces.map(
          (workspace) => (
            <Link
              key={workspace.href}
              href={workspace.href}
              className="nv-admin-directory-link"
            >
              <Panel
                variant="default"
                className="nv-admin-directory-card"
              >
                <div className="nv-admin-directory-card-top">
                  <StatusBadge
                    tone={workspace.tone}
                  >
                    {workspace.status}
                  </StatusBadge>

                  <span
                    aria-hidden="true"
                    className="nv-admin-directory-arrow"
                  >
                    →
                  </span>
                </div>

                <h3 className="nv-admin-directory-title">
                  {workspace.title}
                </h3>

                <p className="nv-admin-directory-description">
                  {workspace.description}
                </p>

                <p className="nv-admin-directory-capability">
                  {workspace.capability}
                </p>
              </Panel>
            </Link>
          ),
        )}
      </div>
    </>
  );

  const primary = (
    <Panel
      variant="muted"
      className="nv-admin-control-summary"
    >
      <div>
        <p className="nv-eyebrow">
          Control summary
        </p>

        <h2 className="nv-section-title">
          Administrative activity remains explicit and auditable.
        </h2>

        <p className="nv-section-description">
          Sensitive operations require authenticated permissions, same-origin validation,
          CSRF protection, and deliberate confirmation. Protected accounts and developer
          systems remain governed by backend policy.
        </p>
      </div>

      <div className="nv-admin-control-badges">
        <StatusBadge tone="success">
          CSRF protected
        </StatusBadge>

        <StatusBadge tone="info">
          Role enforced
        </StatusBadge>

        <StatusBadge tone="warning">
          Confirmation required
        </StatusBadge>
      </div>
    </Panel>
  );

  const footer = (
    <div className="nv-workspace-policy-line">
      <span>Administrative safety boundary</span>

      <span>
        Authenticated access · Explicit actions · Auditable changes · No live execution
      </span>
    </div>
  );

  return (
    <WorkspacePage
      testId="admin-dashboard"
      className="nv-admin-dashboard"
      header={header}
      status={status}
      navigation={navigation}
      primary={primary}
      footer={footer}
    />
  );
}
