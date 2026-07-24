export type WorkspaceKind =
  | "user"
  | "admin"
  | "developer";

export type WorkspaceTheme = {
  eyebrow: string;
  label: string;
  description: string;
  accent: "cyan" | "violet" | "amber";
  environment: string;
  status: string;
};

export const workspaceThemes:
  Record<WorkspaceKind, WorkspaceTheme> = {
    user: {
      eyebrow: "Personal workspace",
      label: "NeuroVest",
      description:
        "Portfolio intelligence, market context, and Neuro.",
      accent: "cyan",
      environment: "Simulation",
      status: "Protected",
    },

    admin: {
      eyebrow: "Administrative workspace",
      label: "NeuroVest Control",
      description:
        "Identity, sessions, support, and platform oversight.",
      accent: "violet",
      environment: "Controlled",
      status: "Authorized",
    },

    developer: {
      eyebrow: "Developer workspace",
      label: "NeuroVest Console",
      description:
        "Runtime, architecture, market systems, and diagnostics.",
      accent: "amber",
      environment: "Development",
      status: "Observed",
    },
  };
