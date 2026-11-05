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

const PRIVATE_CACHE_KEYS = [
  "neurovest_chat_thread_v1",
  "neurovest_request_metrics_v1",
];

function clearPrivateBrowserCaches() {
  for (const key of PRIVATE_CACHE_KEYS) {
    window.localStorage.removeItem(key);
    window.sessionStorage.removeItem(key);
  }
}

export default function LoginPage() {
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

    const form =
      new FormData(event.currentTarget);

    const response = await fetch(
      "/api/auth/login",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        cache: "no-store",
        body: JSON.stringify({
          email: String(
            form.get("email") || ""
          ),
          password: String(
            form.get("password") || ""
          ),
        }),
      }
    );

    if (!response.ok) {
      let detail =
        "Sign-in could not be completed.";

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
          "Sign-in could not be completed.";
      }

      setSubmitting(false);
      setError(detail);
      return;
    }

    clearPrivateBrowserCaches();

    const result = (await response.json()) as {
      redirect?: string;
    };

    const requested =
      new URLSearchParams(
        window.location.search
      ).get("next");

    const approvedDestinations = [
      "/dashboard",
      "/user",
      "/admin",
      "/change-password",
    ];

    const requestedIsApproved =
      typeof requested === "string" &&
      approvedDestinations.some(
        (prefix) =>
          requested === prefix ||
          requested.startsWith(
            `${prefix}/`
          ),
      );

    const destination =
      result.redirect ===
        "/change-password"
        ? "/change-password"
        : requestedIsApproved
          ? requested
          : result.redirect ||
            "/user/dashboard";

    router.replace(destination);
    router.refresh();
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
                Secure access
              </p>

              <h1 className="nv-page-title mt-3">
                Welcome back
              </h1>

              <p className="nv-page-description mt-4 max-w-lg">
                Sign in to access your authenticated NeuroVest workspace,
                portfolio state, strategy intelligence, and controlled runtime.
              </p>

              <div className="mt-8 grid gap-3">
                {[
                  "Server-authoritative authentication",
                  "HttpOnly browser-session cookies",
                  "Refresh-token rotation",
                  "Broker and live execution remain controlled",
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
                Account access
              </p>

              <h2 className="nv-section-title">
                Sign in to NeuroVest
              </h2>

              <p className="nv-section-description">
                Use the credentials associated with your NeuroVest account.
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
                    autoComplete="current-password"
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
                      ? "Authenticating…"
                      : "Sign in"
                  }
                </Button>
              </form>


              <div className="mt-8 flex flex-wrap items-center justify-between gap-3 border-t border-white/[0.07] pt-6 text-sm">
                <Link
                  href="/"
                  className="font-semibold text-slate-500 transition hover:text-slate-200"
                >
                  Return home
                </Link>

                <Link
                  href="/register"
                  className="font-black text-cyan-300 transition hover:text-cyan-100"
                >
                  Create account
                </Link>
              </div>
            </section>
          </div>
        </Panel>
      </div>
    </main>
  );
}
