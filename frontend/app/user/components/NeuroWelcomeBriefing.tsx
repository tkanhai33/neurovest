"use client";

import Image from "next/image";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  StatusBadge,
} from "../../../components/ui";

type UserSessionProfile = {
  display_name?: string | null;
  displayName?: string | null;
  full_name?: string | null;
  fullName?: string | null;
  name?: string | null;
  username?: string | null;
  email?: string | null;
  role?: string | null;
  subscription_tier?: string | null;
  account_status?: string | null;
  is_active?: boolean | null;
};

type NeuroWelcomeBriefingProps = {
  session?: UserSessionProfile | null;
};

const SESSION_DISMISSAL_KEY =
  "neurovest_neuro_briefing_session_dismissed";

const PERMANENT_DISMISSAL_KEY =
  "neurovest_neuro_briefing_do_not_show";

function cleanName(
  value: unknown,
): string | null {
  if (
    typeof value !== "string"
  ) {
    return null;
  }

  const cleaned =
    value.trim();

  return cleaned
    ? cleaned
    : null;
}

function emailPrefix(
  email: unknown,
): string | null {
  const normalized =
    cleanName(email);

  if (!normalized) {
    return null;
  }

  const prefix =
    normalized.split(
      "@",
    )[0]?.trim();

  return prefix || null;
}

function formatDisplayName(
  value: string,
): string {
  return value
    .replace(
      /[._-]+/g,
      " ",
    )
    .replace(
      /\b\w/g,
      (character) =>
        character.toUpperCase(),
    );
}

function greetingForHour(
  hour: number,
): string {
  if (hour < 12) {
    return "Good morning";
  }

  if (hour < 18) {
    return "Good afternoon";
  }

  return "Good evening";
}

export default function NeuroWelcomeBriefing({
  session,
}: NeuroWelcomeBriefingProps) {
  const [
    open,
    setOpen,
  ] = useState(false);

  const [
    doNotShowAgain,
    setDoNotShowAgain,
  ] = useState(false);

  const [
    initialized,
    setInitialized,
  ] = useState(false);

  const displayName =
    useMemo(
      () => {
        const candidate =
          cleanName(
            session?.display_name,
          ) ??
          cleanName(
            session?.displayName,
          ) ??
          cleanName(
            session?.full_name,
          ) ??
          cleanName(
            session?.fullName,
          ) ??
          cleanName(
            session?.name,
          ) ??
          cleanName(
            session?.username,
          ) ??
          emailPrefix(
            session?.email,
          );

        return candidate
          ? formatDisplayName(
              candidate,
            )
          : "there";
      },
      [
        session,
      ],
    );

  const greeting =
    useMemo(
      () =>
        greetingForHour(
          new Date().getHours(),
        ),
      [],
    );

  useEffect(() => {
    const initialize =
      window.setTimeout(
        () => {
          const permanentlyDismissed =
            window.localStorage.getItem(
              PERMANENT_DISMISSAL_KEY,
            ) === "true";

          const dismissedThisSession =
            window.sessionStorage.getItem(
              SESSION_DISMISSAL_KEY,
            ) === "true";

          setDoNotShowAgain(
            permanentlyDismissed,
          );

          setOpen(
            !permanentlyDismissed &&
            !dismissedThisSession,
          );

          setInitialized(
            true,
          );
        },
        0,
      );

    return () => {
      window.clearTimeout(
        initialize,
      );
    };
  }, []);

  function closeBriefing(): void {
    window.sessionStorage.setItem(
      SESSION_DISMISSAL_KEY,
      "true",
    );

    if (doNotShowAgain) {
      window.localStorage.setItem(
        PERMANENT_DISMISSAL_KEY,
        "true",
      );
    } else {
      window.localStorage.removeItem(
        PERMANENT_DISMISSAL_KEY,
      );
    }

    setOpen(false);
  }

  function reopenBriefing(): void {
    setOpen(true);
  }

  if (!initialized) {
    return null;
  }

  return (
    <>
      <button
        type="button"
        onClick={reopenBriefing}
        className="fixed bottom-5 left-5 z-40 rounded-2xl border border-cyan-300/20 bg-slate-950/90 px-4 py-3 text-xs font-black uppercase tracking-[0.13em] text-cyan-100 shadow-[0_18px_60px_rgba(0,0,0,0.48)] backdrop-blur transition hover:-translate-y-0.5 hover:border-cyan-300/40 hover:text-white"
      >
        Open Neuro briefing
      </button>

      {open && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="neuro-briefing-title"
          data-testid="neuro-welcome-briefing"
          className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/80 p-4 backdrop-blur-md"
          onMouseDown={(event) => {
            if (
              event.target ===
              event.currentTarget
            ) {
              closeBriefing();
            }
          }}
        >
          <section className="relative grid max-h-[92vh] w-full max-w-5xl overflow-y-auto rounded-[2rem] border border-cyan-300/20 bg-slate-950 shadow-[0_35px_140px_rgba(0,0,0,0.78)] lg:grid-cols-[0.95fr_1.05fr]">
            <button
              type="button"
              aria-label="Close Neuro briefing"
              onClick={closeBriefing}
              className="absolute right-4 top-4 z-20 flex h-10 w-10 items-center justify-center rounded-full border border-white/[0.1] bg-slate-950/75 text-xl font-black text-slate-300 backdrop-blur transition hover:border-cyan-300/30 hover:text-white"
            >
              ×
            </button>

            <div className="relative min-h-[360px] overflow-hidden border-b border-white/[0.07] lg:min-h-[600px] lg:border-b-0 lg:border-r">
              <div
                aria-hidden="true"
                className="absolute inset-0 bg-[radial-gradient(circle_at_50%_34%,rgba(34,211,238,0.18),transparent_37%),radial-gradient(circle_at_70%_70%,rgba(168,85,247,0.16),transparent_40%),linear-gradient(180deg,rgba(2,6,23,0.2),rgba(2,6,23,0.95))]"
              />

              <Image
                src="/images/neuro/neuro-hero.png"
                alt="Neuro robotic wolf guardian"
                fill
                priority
                sizes="(max-width: 1024px) 100vw, 48vw"
                className="object-contain object-center p-4 sm:p-8"
              />

              <div className="absolute bottom-5 left-5 right-5 flex flex-wrap gap-2">
                <StatusBadge tone="success">
                  Simulation active
                </StatusBadge>

                <StatusBadge tone="violet">
                  Account scoped
                </StatusBadge>

                <StatusBadge tone="warning">
                  Live execution disabled
                </StatusBadge>
              </div>
            </div>

            <div className="flex flex-col justify-center p-7 sm:p-10 lg:p-12">
              <p className="nv-eyebrow">
                Neuro account briefing
              </p>

              <h2
                id="neuro-briefing-title"
                className="mt-4 text-4xl font-black tracking-[-0.045em] text-white sm:text-5xl"
              >
                {greeting},{" "}
                <span className="bg-gradient-to-r from-cyan-300 to-fuchsia-400 bg-clip-text text-transparent">
                  {displayName}.
                </span>
              </h2>

              <p className="mt-5 text-base leading-8 text-slate-300">
                Your authenticated paper-trading workspace is ready.
                Portfolio records, order activity, account valuation,
                and analytics remain isolated to your account.
              </p>

              <div className="mt-7 grid gap-3 sm:grid-cols-2">
                <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-4">
                  <p className="nv-stat-label">
                    Account
                  </p>

                  <p className="mt-3 text-lg font-black capitalize text-white">
                    {session?.account_status ??
                      "active"}
                  </p>
                </div>

                <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-4">
                  <p className="nv-stat-label">
                    Subscription
                  </p>

                  <p className="mt-3 text-lg font-black capitalize text-white">
                    {session?.subscription_tier ??
                      "free"}
                  </p>
                </div>

                <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-4">
                  <p className="nv-stat-label">
                    Execution mode
                  </p>

                  <p className="mt-3 text-lg font-black text-cyan-200">
                    Paper only
                  </p>
                </div>

                <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-4">
                  <p className="nv-stat-label">
                    Current protection
                  </p>

                  <p className="mt-3 text-lg font-black text-emerald-200">
                    Owner isolated
                  </p>
                </div>
              </div>

              <div className="mt-7 rounded-2xl border border-cyan-300/10 bg-cyan-300/[0.04] p-5">
                <p className="text-sm font-black uppercase tracking-[0.12em] text-cyan-200">
                  Neuro status
                </p>

                <p className="mt-3 text-sm leading-7 text-slate-300">
                  No live-money broker order can be placed from this
                  workspace. All trading actions remain simulated,
                  authenticated, risk gated, and recorded to the
                  account-scoped ledger.
                </p>
              </div>

              <label className="mt-6 flex cursor-pointer items-start gap-3 rounded-2xl border border-white/[0.08] bg-white/[0.02] p-4">
                <input
                  type="checkbox"
                  checked={doNotShowAgain}
                  onChange={(event) => {
                    setDoNotShowAgain(
                      event.target.checked,
                    );
                  }}
                  className="mt-1 h-4 w-4 accent-cyan-400"
                />

                <span className="text-sm leading-6 text-slate-300">
                  Don&apos;t show this briefing automatically again.
                  You can still reopen it from the workspace.
                </span>
              </label>

              <div className="mt-7 flex flex-wrap justify-end gap-3">
                <button
                  type="button"
                  onClick={closeBriefing}
                  className="nv-button nv-button-primary nv-button-lg"
                >
                  Enter workspace
                </button>
              </div>
            </div>
          </section>
        </div>
      )}
    </>
  );
}
