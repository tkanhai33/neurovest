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

import {
  Button,
  Input,
  Panel,
  StatusMessage,
} from "../../components/ui";

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
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#020617] px-4 py-10 text-white sm:px-6 sm:py-16">
      <div className="landing-grid pointer-events-none absolute inset-0 opacity-30" />
      <div className="landing-orb landing-orb-cyan" />
      <div className="landing-orb landing-orb-violet" />

      <div className="relative z-10 w-full max-w-2xl">
        <Panel
          variant="elevated"
          className="p-7 sm:p-10 lg:p-12"
        >
          <p className="nv-eyebrow">
            Required security step
          </p>

          <h1 className="nv-page-title mt-3">
            Replace temporary password
          </h1>

          <p className="nv-page-description mt-4">
            Temporary credentials cannot continue into the authenticated
            NeuroVest workspace. Create your private replacement password
            to complete account setup.
          </p>


          <div className="mt-6 rounded-xl border border-cyan-400/10 bg-cyan-400/[0.035] p-4">
            <p className="text-sm leading-6 text-slate-400">
              Your new password must contain at least 12 characters,
              including uppercase, lowercase, a number, and a symbol.
            </p>
          </div>


          <form
            onSubmit={submit}
            className="mt-8 space-y-5"
          >
            <label className="block">
              <span className="nv-eyebrow">
                Temporary password
              </span>

              <Input
                name="current_password"
                type="password"
                required
                autoComplete="current-password"
                placeholder="Temporary password"
                disabled={submitting}
                className="mt-2"
              />
            </label>


            <label className="block">
              <span className="nv-eyebrow">
                New password
              </span>

              <Input
                name="new_password"
                type="password"
                required
                minLength={12}
                autoComplete="new-password"
                placeholder="New password"
                disabled={submitting}
                className="mt-2"
              />
            </label>


            <label className="block">
              <span className="nv-eyebrow">
                Confirm new password
              </span>

              <Input
                name="confirmation"
                type="password"
                required
                minLength={12}
                autoComplete="new-password"
                placeholder="Confirm new password"
                disabled={submitting}
                className="mt-2"
              />
            </label>


            {error ? (
              <StatusMessage tone="danger">
                {error}
              </StatusMessage>
            ) : null}


            <Button
              type="submit"
              variant="primary"
              disabled={submitting}
              className="w-full"
            >
              {
                submitting
                  ? "Updating…"
                  : "Replace password"
              }
            </Button>
          </form>
        </Panel>
      </div>
    </main>
  );
}
