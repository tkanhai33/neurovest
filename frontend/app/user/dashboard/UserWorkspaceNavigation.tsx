"use client";

import {
  USER_WORKSPACES,
  type UserWorkspaceId,
} from "./userWorkspaceTypes";

type UserWorkspaceNavigationProps = {
  activeWorkspace: UserWorkspaceId;
  onChange: (
    workspace: UserWorkspaceId,
  ) => void;
};

export default function UserWorkspaceNavigation({
  activeWorkspace,
  onChange,
}: UserWorkspaceNavigationProps) {
  return (
    <div className="nv-user-investing-navigation">
      <div className="nv-user-investing-navigation-heading">
        <div>
          <p className="nv-eyebrow">
            Your investing tools
          </p>

          <h2 className="nv-section-title">
            Explore your investments
          </h2>

          <p className="nv-section-description">
            Navigate your portfolio, markets, paper orders,
            strategies, history, and account options.
          </p>
        </div>
      </div>

      <div
        role="tablist"
        aria-label="User investing workspaces"
        className="nv-user-investing-tabs"
      >
        {USER_WORKSPACES.map(
          (workspace) => {
            const active =
              activeWorkspace === workspace.id;

            return (
              <button
                key={workspace.id}
                type="button"
                role="tab"
                aria-selected={active}
                title={workspace.description}
                onClick={(event) => {
                    const tab = event.currentTarget;
                    const strip = tab.parentElement;
                    if (strip) {
                      const left = tab.offsetLeft - strip.offsetLeft;
                      const right = left + tab.offsetWidth;
                      if (left < strip.scrollLeft) {
                        strip.scrollTo({ left, behavior: "smooth" });
                      } else if (right > strip.scrollLeft + strip.clientWidth) {
                        strip.scrollTo({
                          left: right - strip.clientWidth,
                          behavior: "smooth",
                        });
                      }
                    }
                    onChange(workspace.id);
                }}
                className={[
                  "nv-user-investing-tab min-h-11 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300",
                  active
                    ? "nv-user-investing-tab-active"
                    : "",
                ].join(" ")}
              >
                <span>
                  {workspace.label}
                </span>

                <small>
                  {workspace.description}
                </small>
              </button>
            );
          },
        )}
      </div>
    </div>
  );
}
