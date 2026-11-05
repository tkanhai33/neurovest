"use client";

import {
  useEffect,
  useState,
  type FormEvent,
} from "react";

import { csrfHeaders } from "../../../lib/clientCsrf";

type AccountProfile = {
  display_name: string | null;
  email: string;
  profile_editable_fields: string[];
};

function errorMessage(value: unknown, fallback: string): string {
  if (
    value &&
    typeof value === "object" &&
    "detail" in value &&
    typeof value.detail === "string"
  ) {
    return value.detail;
  }
  return fallback;
}

// F12_PROFILE_SESSION_RECOVERY_V1
// Profile changes never rotate credentials by themselves.
// Recover only when the existing access token is rejected.
async function fetchProfileWithSessionRecovery(
  url: string,
  options: RequestInit
): Promise<Response> {
  const first = await fetch(url, {
    ...options,
    credentials: "same-origin",
  });

  if (first.status !== 401) {
    return first;
  }

  // Use NeuroVest's existing refresh endpoint.
  // Its backend validation still enforces session and
  // credential-generation revocation.
  let refreshed: Response;

  try {
    refreshed = await fetch("/api/auth/refresh", {
      method: "POST",
      headers: {
        ...csrfHeaders(),
      },
      credentials: "same-origin",
      cache: "no-store",
    });
  } catch {
    return first;
  }

  if (!refreshed.ok) {
    return first;
  }

  // The refresh route installs updated authentication cookies.
  // Retry the original request once; never loop.
  return fetch(url, {
    ...options,
    credentials: "same-origin",
  });
}

export default function AccountSecurityPanel() {
  const [profile, setProfile] = useState<AccountProfile | null>(null);
  const [displayName, setDisplayName] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [changing, setChanging] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  useEffect(() => {
    let active = true;

    async function loadProfile() {
      try {
        const response = await fetchProfileWithSessionRecovery("/api/account/profile", {
          cache: "no-store",
        });

        const payload: unknown = await response.json();

        if (!active) return;

        if (!response.ok) {
          setError(errorMessage(payload, "Unable to load account profile"));
          return;
        }

        const data = payload as AccountProfile;

        setProfile(data);
        setDisplayName(data.display_name ?? "");
      } catch {
        if (active) setError("Unable to load account profile.");
      } finally {
        if (active) setLoading(false);
      }
    }

    void loadProfile();

    return () => {
      active = false;
    };
  }, []);

  async function saveProfile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setMessage("");

    try {
      const response = await fetchProfileWithSessionRecovery("/api/account/profile", {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          ...csrfHeaders(),
        },
        cache: "no-store",
        body: JSON.stringify({
          display_name: displayName.trim() || null,
        }),
      });

      const payload: unknown = await response.json();

      if (!response.ok) {
        setError(errorMessage(payload, "Unable to save profile."));
        return;
      }

      const updated = payload as AccountProfile;
      setProfile(updated);
      setDisplayName(updated.display_name ?? "");
      setMessage("Profile updated successfully.");
    } catch {
      setError("Unable to save profile.");
    } finally {
      setSaving(false);
    }
  }

  async function changePassword(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setMessage("");

    if (newPassword !== confirmPassword) {
      setError("New passwords do not match.");
      return;
    }

    if (newPassword.length < 12) {
      setError("Your new password must contain at least 12 characters.");
      return;
    }

    if (currentPassword === newPassword) {
      setError("Choose a different password.");
      return;
    }

    setChanging(true);

    try {
      const response = await fetch("/api/account/password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...csrfHeaders(),
        },
        cache: "no-store",
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
        }),
      });

      const payload: unknown = await response.json();

      if (!response.ok) {
        setError(
          errorMessage(payload, "Password could not be changed.")
        );
        return;
      }

      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");

      // The backend invalidates existing credential generations.
      // The proxy clears the browser session.
      window.location.assign("/login?passwordChanged=1");
    } catch {
      setError("Password change failed. Please try again.");
    } finally {
      setChanging(false);
    }
  }

  const fieldClass =
    "mt-2 w-full rounded-xl border border-slate-700 " +
    "bg-slate-950/70 px-4 py-3 text-sm text-white " +
    "outline-none placeholder:text-slate-500 " +
    "focus:border-cyan-400 disabled:opacity-50";

  const buttonClass =
    "rounded-xl bg-cyan-500 px-5 py-3 text-sm " +
    "font-semibold text-slate-950 transition hover:bg-cyan-400 " +
    "disabled:cursor-not-allowed disabled:opacity-50";

  return (
    <section
      id="profile-security"
      aria-label="Profile and security"
      className="w-full scroll-mt-24"
    >
      <div className="mb-6">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-400">
          Account management
        </p>
        <h2 className="mt-2 text-2xl font-bold text-white">
          Profile &amp; Security
        </h2>
        <p className="mt-2 text-sm text-slate-400">
          Manage your account details and protect your NeuroVest sign-in.
        </p>
      </div>

      {error && (
        <div role="alert" className="mb-5 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-200">
          {error}
        </div>
      )}

      {message && (
        <div role="status" className="mb-5 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4 text-sm text-emerald-200">
          {message}
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-white/10 bg-slate-900/70 p-6">
          <h3 className="text-lg font-semibold text-white">
            Your profile
          </h3>
          <p className="mt-1 text-sm text-slate-400">
            Your email is tied to your account. Your display name can be edited.
          </p>

          {loading ? (
            <p className="mt-6 text-sm text-slate-400">
              Loading account...
            </p>
          ) : profile ? (
            <form onSubmit={saveProfile} className="mt-6 space-y-5">
              <label className="block text-sm text-slate-300">
                Email address
                <input
                  type="email"
                  value={profile.email}
                  readOnly
                  className={`${fieldClass} cursor-not-allowed opacity-70`}
                />
              </label>

              <label className="block text-sm text-slate-300">
                Display name
                <input
                  type="text"
                  value={displayName}
                  onChange={(event) => setDisplayName(event.target.value)}
                  maxLength={100}
                  autoComplete="nickname"
                  className={fieldClass}
                  placeholder="Enter your display name"
                />
              </label>

              <button
                type="submit"
                disabled={saving}
                className={buttonClass}
              >
                {saving ? "Saving..." : "Save profile"}
              </button>
            </form>
          ) : (
            <p className="mt-6 text-sm text-slate-400">
              Profile unavailable. Please sign in again if your session expired.
            </p>
          )}
        </div>

        <div className="rounded-2xl border border-white/10 bg-slate-900/70 p-6">
          <h3 className="text-lg font-semibold text-white">
            Change password
          </h3>
          <p className="mt-1 text-sm text-slate-400">
            Changing your password signs out existing sessions.
            You will need to sign in again.
          </p>

          <form onSubmit={changePassword} className="mt-6 space-y-4">
            <label className="block text-sm text-slate-300">
              Current password
              <input
                type="password"
                value={currentPassword}
                onChange={(event) => setCurrentPassword(event.target.value)}
                autoComplete="current-password"
                required
                disabled={changing}
                className={fieldClass}
              />
            </label>

            <label className="block text-sm text-slate-300">
              New password
              <input
                type="password"
                value={newPassword}
                onChange={(event) => setNewPassword(event.target.value)}
                autoComplete="new-password"
                required
                minLength={12}
                disabled={changing}
                className={fieldClass}
              />
            </label>

            <label className="block text-sm text-slate-300">
              Confirm new password
              <input
                type="password"
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                autoComplete="new-password"
                required
                minLength={12}
                disabled={changing}
                className={fieldClass}
              />
            </label>

            <p className="text-xs leading-5 text-slate-400">
              Minimum 12 characters, including uppercase,
              lowercase, a number and a symbol.
            </p>

            <button
              type="submit"
              disabled={changing}
              className={buttonClass}
            >
              {changing ? "Updating password..." : "Change password"}
            </button>
          </form>
        </div>
      </div>
    </section>
  );
}
