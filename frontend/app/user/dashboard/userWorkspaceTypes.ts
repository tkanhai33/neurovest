export type UserWorkspaceId =
  | "quick"
  | "markets"
  | "portfolio"
  | "orders"
  | "history"
  | "strategies"
  | "options";

export type UserWorkspaceDefinition = {
  id: UserWorkspaceId;
  label: string;
  description: string;
};

export const USER_WORKSPACES:
  readonly UserWorkspaceDefinition[] = [
    {
      id: "quick",
      label: "Quick View",
      description:
        "Portfolio value, cash, holdings, market context, and recent activity.",
    },
    {
      id: "markets",
      label: "Markets",
      description:
        "Quotes, prices, watchlists, and market intelligence.",
    },
    {
      id: "portfolio",
      label: "Portfolio",
      description:
        "Holdings, valuation, exposure, analytics, and performance.",
    },
    {
      id: "orders",
      label: "Orders",
      description:
        "Submit and review controlled paper orders.",
    },
    {
      id: "history",
      label: "History",
      description:
        "Account order records and owner-scoped activity.",
    },
    {
      id: "strategies",
      label: "Strategies",
      description:
        "Read-only strategy decisions, signals, and confidence.",
    },
    {
      id: "options",
      label: "Account",
      description:
        "Account settings, security, subscription, and preferences.",
    },
  ];
