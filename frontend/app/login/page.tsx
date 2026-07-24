"use client";

import Link from "next/link";
import {
  FormEvent,
  useState,
} from "react";
import {
  useRouter,
} from "next/navigation";

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
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#020617] px-6 py-16 text-white">
      <div className="landing-grid pointer-events-none absolute inset-0 opacity-40" />
      <div className="landing-orb landing-orb-cyan" />
      <div className="landing-orb landing-orb-violet" />

      <section className="relative z-10 w-full max-w-[1120px] overflow-hidden rounded-[2.5rem] border border-white/10 bg-slate-950/70 shadow-[0_0_100px_rgba(34,211,238,0.08)] backdrop-blur-xl">
        <div className="grid lg:grid-cols-[0.9fr_1.1fr]">
          <div className="border-b border-white/5 p-8 lg:border-b-0 lg:border-r lg:p-12">
            <Link
              href="/"
              className="text-xs font-black uppercase tracking-[0.34em] text-cyan-300"
            >
              ← NeuroVest
            </Link>

            <h1 className="mt-10 text-4xl font-black tracking-[-0.04em] text-white sm:text-5xl">
              Welcome back.
            </h1>

            <p className="mt-5 text-base leading-7 text-slate-400">
              Sign in to access the controlled dashboard,
              runtime graph, and read-only intelligence
              systems.
            </p>

            <div className="mt-10 space-y-3">
              {[
                "Server-authoritative authentication",
                "HttpOnly browser-session cookies",
                "Refresh-token rotation",
                "Broker and live execution disabled",
              ].map((item) => (
                <div
                  key={item}
                  className="flex items-center gap-3 rounded-xl border border-white/5 bg-white/[0.025] px-4 py-3 text-sm text-slate-300"
                >
                  <span className="h-1.5 w-1.5 rounded-full bg-cyan-300" />
                  {item}
                </div>
              ))}
            </div>
          </div>

          <div className="p-8 lg:p-12">
            <p className="text-xs font-black uppercase tracking-[0.3em] text-fuchsia-300">
              Secure access
            </p>

            <h2 className="mt-3 text-3xl font-black text-white">
              Sign in to NeuroVest
            </h2>

            <form
              className="mt-9 space-y-5"
              onSubmit={submit}
            >
              <div>
                <label
                  htmlFor="email"
                  className="mb-2 block text-xs font-black uppercase tracking-[0.2em] text-slate-400"
                >
                  Email
                </label>

                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  disabled={submitting}
                  className="w-full rounded-2xl border border-slate-700 bg-slate-900/70 px-4 py-4 text-sm text-white outline-none transition focus:border-cyan-300/60 focus:ring-4 focus:ring-cyan-300/5"
                />
              </div>

              <div>
                <label
                  htmlFor="password"
                  className="mb-2 block text-xs font-black uppercase tracking-[0.2em] text-slate-400"
                >
                  Password
                </label>

                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  disabled={submitting}
                  className="w-full rounded-2xl border border-slate-700 bg-slate-900/70 px-4 py-4 text-sm text-white outline-none transition focus:border-cyan-300/60 focus:ring-4 focus:ring-cyan-300/5"
                />
              </div>

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
                className="w-full rounded-2xl bg-cyan-300 px-5 py-4 text-sm font-black text-slate-950 transition hover:bg-cyan-200 disabled:cursor-wait disabled:opacity-60"
              >
                {submitting
                  ? "Authenticating…"
                  : "Sign in"}
              </button>
            </form>

            <div className="mt-8 flex items-center justify-between border-t border-white/5 pt-6 text-xs text-slate-500">
              <Link
                href="/"
                className="hover:text-white"
              >
                Return home
              </Link>

              <Link
                href="/register"
                className="font-bold text-cyan-200 hover:text-cyan-100"
              >
                Create account
              </Link>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
