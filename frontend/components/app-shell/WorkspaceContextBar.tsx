import LogoutButton from "../../app/components/auth/LogoutButton";

import type {
  WorkspaceKind,
} from "./workspaceConfig";

import {
  workspaceThemes,
} from "./workspaceConfig";

type WorkspaceContextBarProps = {
  workspace: WorkspaceKind;
};

export default function WorkspaceContextBar({
  workspace,
}: WorkspaceContextBarProps) {
  const theme =
    workspaceThemes[workspace];

  return (
    <div
      className="nv-context-bar"
      data-workspace={workspace}
    >
      <div className="nv-context-primary">
        <span
          className="nv-status-dot"
          aria-hidden="true"
        />

        <div>
          <p className="nv-context-eyebrow">
            {theme.eyebrow}
          </p>

          <p className="nv-context-description">
            {theme.description}
          </p>
        </div>
      </div>

      {workspace === "user" ? (
        <div className="nv-user-context-logout">
          <LogoutButton />
        </div>
      ) : (
        <div className="nv-context-statuses">
          <span className="nv-context-status">
            <span>Environment</span>
            <strong>
              {theme.environment}
            </strong>
          </span>

          <span className="nv-context-status">
            <span>Runtime</span>
            <strong>
              {theme.status}
            </strong>
          </span>

          <span className="nv-context-status">
            <span>Execution</span>
            <strong>Disabled</strong>
          </span>
        </div>
      )}
    </div>
  );
}
