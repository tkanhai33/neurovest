"use client";

import Link from "next/link";
import {
  FormEvent,
  useState,
} from "react";
import {
  useRouter,
} from "next/navigation";

import {
  Button,
  Input,
  Panel,
  StatusMessage,
} from "../../components/ui";

export default function RegisterPage() {
  const router = useRouter();

  const [error, setError] =
    useState<string | null>(null);

  const [submitting, setSubmitting] =
    useState(false);

  async function submit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setError(null);

    const form =
      new FormData(event.currentTarget);

    const email = String(
      form.get("email") || "",
    ).trim();

    const password = String(
      form.get("password") || "",
    );

    const confirmation = String(
      form.get("confirmation") || "",
    );

    if (password !== confirmation) {
      setError(
        "The passwords do not match.",
      );
      return;
    }

    setSubmitting(true);

    try {
      const response = await fetch(
        "/api/auth/register",
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          cache: "no-store",
          body: JSON.stringify({
            email,
            password,
            terms_accepted:
              form.get("termsAccepted") === "accepted",
            terms_version:
              "neurovest-beta-terms-2026-10-09-v1",
          }),
        },
      );

      if (!response.ok) {
        let detail =
          "The account could not be created.";

        try {
          const failure =
            (await response.json()) as {
              detail?: string;
            };

          if (
            typeof failure.detail ===
              "string" &&
            failure.detail.trim()
          ) {
            detail = failure.detail;
          }
        } catch {
          detail =
            "The account could not be created.";
        }

        setError(detail);
        return;
      }

      router.replace(
        "/login?registered=1",
      );
      router.refresh();
    } catch {
      setError(
        "Registration is temporarily unavailable.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#020617] px-4 py-10 text-white sm:px-6 sm:py-16">
      <div className="landing-grid pointer-events-none absolute inset-0 opacity-30" />
      <div className="landing-orb landing-orb-cyan" />
      <div className="landing-orb landing-orb-violet" />

      <div className="relative z-10 w-full max-w-6xl">
        <Panel
          variant="elevated"
          className="overflow-hidden p-0"
        >
          <div className="grid lg:grid-cols-[0.9fr_1.1fr]">
            <section className="border-b border-white/[0.07] p-7 sm:p-9 lg:border-b-0 lg:border-r lg:p-12">
              <Link
                href="/"
                className="nv-eyebrow inline-flex transition hover:text-white"
              >
                ← NeuroVest
              </Link>

              <p className="nv-eyebrow mt-10">
                New account
              </p>

              <h1 className="nv-page-title mt-3">
                Create your account
              </h1>

              <p className="nv-page-description mt-4 max-w-lg">
                Join NeuroVest and access your authenticated investing
                workspace, research strategies, portfolio visibility,
                risk systems, and Neuro.
              </p>

              <div className="mt-8 grid gap-3">
                {[
                  "Simulation-first environment",
                  "Server-authoritative security",
                  "Private browser session",
                  "Controlled execution boundaries",
                ].map(
                  (
                    item,
                  ) => (
                    <div
                      key={item}
                      className="flex items-center gap-3 rounded-xl border border-white/[0.07] bg-white/[0.025] px-4 py-3 text-sm font-semibold text-slate-400"
                    >
                      <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-cyan-300" />
                      <span>
                        {item}
                      </span>
                    </div>
                  ),
                )}
              </div>
            </section>


            <section className="p-7 sm:p-9 lg:p-12">
              <p className="nv-eyebrow">
                Registration
              </p>

              <h2 className="nv-section-title">
                Register for NeuroVest
              </h2>

              <p className="nv-section-description">
                Create credentials for your personal NeuroVest account.
              </p>


              <form
                className="mt-8 space-y-5"
                onSubmit={submit}
              >
                <label className="block">
                  <span className="nv-eyebrow">
                    Email
                  </span>

                  <Input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    disabled={submitting}
                    className="mt-2"
                  />
                </label>


                <label className="block">
                  <span className="nv-eyebrow">
                    Password
                  </span>

                  <Input
                    id="password"
                    name="password"
                    type="password"
                    autoComplete="new-password"
                    minLength={12}
                    required
                    disabled={submitting}
                    className="mt-2"
                  />

                  <p className="mt-2 text-xs font-semibold text-slate-500">
                    Use at least 12 characters.
                  </p>
                </label>


                <label className="block">
                  <span className="nv-eyebrow">
                    Confirm password
                  </span>

                  <Input
                    id="confirmation"
                    name="confirmation"
                    type="password"
                    autoComplete="new-password"
                    minLength={12}
                    required
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
                      ? "Creating account…"
                      : "Create account"
                  }
                </Button>
              
          <label
            data-testid="beta-policy-acknowledgement"
            className="flex items-start gap-3 rounded-2xl border border-white/[0.08] bg-white/[0.025] p-4 text-sm leading-6 text-slate-400"
          >
            <input
              type="checkbox"
              name="termsAccepted"
              value="accepted"
              required
              disabled={submitting}
              className="mt-1 h-4 w-4 rounded border-slate-600 bg-slate-950 text-cyan-300 focus:ring-cyan-300"
            />
            <span>
              I have read and agree to the{" "}
              <a
                href="/terms"
                className="font-semibold text-cyan-300 underline underline-offset-4 hover:text-cyan-200"
              >
                NeuroVest Beta Terms
              </a>
              {" "}and acknowledge the{" "}
              <a
                href="/privacy"
                className="font-semibold text-cyan-300 underline underline-offset-4 hover:text-cyan-200"
              >
                Privacy Notice
              </a>
              . Brokerage connections are read-only and all order
              activity remains paper-only.
            </span>
          </label>

        </form>


              <div className="mt-8 flex flex-wrap items-center justify-between gap-3 border-t border-white/[0.07] pt-6 text-sm">
                <Link
                  href="/"
                  className="font-semibold text-slate-500 transition hover:text-slate-200"
                >
                  Return home
                </Link>

                <Link
                  href="/login"
                  className="font-black text-cyan-300 transition hover:text-cyan-100"
                >
                  Already registered? Sign in
                </Link>
              </div>
            </section>
          </div>
        </Panel>
      </div>
    </main>
  );
}
