import type {
  ReactNode,
} from "react";

import RoleAwareWorkspaceNav from "../RoleAwareWorkspaceNav";

import WorkspaceContextBar from "./WorkspaceContextBar";

import type {
  WorkspaceKind,
} from "./workspaceConfig";

type AppShellProps = {
  workspace: WorkspaceKind;
  children: ReactNode;
  contextSlot?: ReactNode;
};

export default function AppShell({
  workspace,
  children,
  contextSlot,
}: AppShellProps) {
  return (
    <div
      className="nv-app-shell"
      data-workspace={workspace}
    >
      <div
        className="nv-app-grid"
        aria-hidden="true"
      />

      <div
        className="nv-app-glow nv-app-glow-left"
        aria-hidden="true"
      />

      <div
        className="nv-app-glow nv-app-glow-right"
        aria-hidden="true"
      />

      <header className="nv-app-navigation">
        <RoleAwareWorkspaceNav />
      </header>

      <div className="nv-app-frame">
        <WorkspaceContextBar
          workspace={workspace}
        />

        {contextSlot && (
          <div className="nv-context-slot">
            {contextSlot}
          </div>
        )}

        <div className="nv-app-content">
          {children}
        </div>
      </div>
    </div>
  );
}
