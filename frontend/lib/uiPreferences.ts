export const UI_PREFERENCE_VERSION =
  "neurovest_ui_preferences_v1";

export type SafeUiPreferences = {
  activeWorkspace?: string;
};

const ALLOWED_WORKSPACES = new Set([
  "overview",
  "market",
  "graph",
  "observability",
  "learning",
  "chat",
]);

function readCookie(
  name: string
): string | null {
  if (typeof document === "undefined") {
    return null;
  }

  for (
    const part
    of document.cookie.split(";")
  ) {
    const [
      rawName,
      ...rawValue
    ] = part.trim().split("=");

    if (rawName === name) {
      return decodeURIComponent(
        rawValue.join("=")
      );
    }
  }

  return null;
}

function storageKey(): string | null {
  const scope = readCookie(
    "neurovest_preference_scope"
  );

  return scope
    ? `${UI_PREFERENCE_VERSION}:${scope}`
    : null;
}

export function loadSafeUiPreferences():
  SafeUiPreferences {
  const key = storageKey();

  if (
    !key ||
    typeof window === "undefined"
  ) {
    return {};
  }

  try {
    const parsed = JSON.parse(
      window.localStorage.getItem(key) ||
        "{}"
    ) as SafeUiPreferences;

    return {
      activeWorkspace:
        typeof parsed.activeWorkspace ===
          "string" &&
        ALLOWED_WORKSPACES.has(
          parsed.activeWorkspace
        )
          ? parsed.activeWorkspace
          : undefined,
    };
  } catch {
    return {};
  }
}

export function saveSafeUiPreferences(
  preferences: SafeUiPreferences
): void {
  const key = storageKey();

  if (
    !key ||
    typeof window === "undefined"
  ) {
    return;
  }

  const safe: SafeUiPreferences = {};

  if (
    preferences.activeWorkspace &&
    ALLOWED_WORKSPACES.has(
      preferences.activeWorkspace
    )
  ) {
    safe.activeWorkspace =
      preferences.activeWorkspace;
  }

  window.localStorage.setItem(
    key,
    JSON.stringify(safe)
  );
}
