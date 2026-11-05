import type {
  ReactNode,
} from "react";

import type {
  UserWorkspaceId,
} from "./userWorkspaceTypes";

type UserWorkspaceRouterProps = {
  activeWorkspace: UserWorkspaceId;
  history: ReactNode;
  markets: ReactNode;
  options: ReactNode;
  orders: ReactNode;
  portfolio: ReactNode;
  quick: ReactNode;
  strategies: ReactNode;
};

export default function UserWorkspaceRouter({
  activeWorkspace,
  history,
  markets,
  options,
  orders,
  portfolio,
  quick,
  strategies,
}: UserWorkspaceRouterProps) {
  const workspaceMap:
    Record<UserWorkspaceId, ReactNode> = {
      quick,
      markets,
      portfolio,
      orders,
      history,
      strategies,
      options,
    };

  return (
    <section
      aria-live="polite"
      className="nv-user-investing-workspace"
      data-active-workspace={activeWorkspace}
    >
      {workspaceMap[activeWorkspace]}
    </section>
  );
}
