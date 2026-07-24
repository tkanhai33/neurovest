"use client";

import {
  FormEvent,
  useState,
} from "react";

import {
  useRouter,
} from "next/navigation";

import {
  csrfHeaders,
} from "../../lib/clientCsrf";

export default function ChangePasswordPage() {
  const router = useRouter();

  const [error, setError] =
    useState<string | null>(null);

  const [submitting, setSubmitting] =
    useState(false);

  async function submit(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    setError(null);
    setSubmitting(true);

    const form = new FormData(
      event.currentTarget
    );

    const currentPassword = String(
      form.get("current_password") || ""
    );

    const newPassword = String(
      form.get("new_password") || ""
    );

    const confirmation = String(
      form.get("confirmation") || ""
    );

    if (newPassword !== confirmation) {
      setSubmitting(false);
      setError(
        "The new passwords do not match."
      );
      return;
    }

    const response = await fetch(
      "/api/auth/change-password",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...csrfHeaders(),
        },
        cache: "no-store",
        body: JSON.stringify({
          current_password:
            currentPassword,
          new_password:
            newPassword,
        }),
      }
    );

    if (!response.ok) {
      setSubmitting(false);
      setError(
        "The password could not be replaced. " +
        "Use at least 12 characters with uppercase, " +
        "lowercase, a number, and a symbol."
      );
      return;
    }

    router.replace(
      "/login?passwordChanged=1"
    );

    router.refresh();
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#020617] px-6 py-16 text-white">
      <section className="w-full max-w-xl rounded-[2rem] border border-white/10 bg-slate-950/80 p-8 shadow-2xl backdrop-blur-xl sm:p-12">
        <p className="text-xs font-black uppercase tracking-[0.3em] text-cyan-300">
          Required security step
        </p>

        <h1 className="mt-4 text-4xl font-black">
          Replace temporary password
        </h1>

        <p className="mt-4 leading-7 text-slate-400">
          Your temporary credentials cannot access
          the NeuroVest dashboard. Create a private
          replacement password to continue.
        </p>

        <form
          onSubmit={submit}
          className="mt-9 space-y-5"
        >
          <input
            name="current_password"
            type="password"
            required
            autoComplete="current-password"
            placeholder="Temporary password"
            className="w-full rounded-2xl border border-slate-700 bg-slate-900 px-4 py-4"
          />

          <input
            name="new_password"
            type="password"
            required
            minLength={12}
            autoComplete="new-password"
            placeholder="New password"
            className="w-full rounded-2xl border border-slate-700 bg-slate-900 px-4 py-4"
          />

          <input
            name="confirmation"
            type="password"
            required
            minLength={12}
            autoComplete="new-password"
            placeholder="Confirm new password"
            className="w-full rounded-2xl border border-slate-700 bg-slate-900 px-4 py-4"
          />

          {error && (
            <div
              role="alert"
              className="rounded-2xl border border-red-300/20 bg-red-400/5 p-4 text-sm text-red-200"
            >
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-2xl bg-cyan-300 px-5 py-4 font-black text-slate-950 disabled:opacity-60"
          >
            {submitting
              ? "Updating…"
              : "Replace password"}
          </button>
        </form>
      </section>
    </main>
  );
}
