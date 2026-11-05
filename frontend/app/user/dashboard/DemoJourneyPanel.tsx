"use client";

import {
  useEffect,
  useState,
} from "react";

type DemoWorkspace =
  | "portfolio"
  | "strategies"
  | "orders"
  | "history";

type DemoJourneyPanelProps = {
  onOpenWorkspace: (
    workspace: DemoWorkspace,
  ) => void;
};

type Lesson = {
  label: string;
  title: string;
  description: string;
  purpose: string;
  instructions: readonly string[];
  takeaway: string;
  action: string;
  workspace?: DemoWorkspace;
  href?: string;
  optional?: boolean;
};

const lessons: readonly Lesson[] = [
  {
    label: "Optional",
    title: "Connect brokerage",
    description: "Understand read-only brokerage connections.",
    purpose:
      "A brokerage connection lets NeuroVest display supported account information separately from your simulated portfolio. You do not need to connect one to explore paper trading.",
    instructions: [
      "Open the brokerage connection page.",
      "Review the connection status and read-only explanation.",
      "If you want to connect an account, follow the supported connection workflow.",
      "Return to your dashboard to inspect available brokerage information.",
    ],
    takeaway:
      "NeuroVest does not place live brokerage orders. You can skip this lesson's connection action.",
    action: "Open brokerage connections",
    href: "/user/brokerage",
    optional: true,
  },
  {
    label: "Review",
    title: "Inspect holdings",
    description: "Learn the difference between real and simulated funds.",
    purpose:
      "The Portfolio workspace separates read-only brokerage holdings from your independent NeuroVest paper account.",
    instructions: [
      "Open the Portfolio workspace.",
      "Look for the Brokerage portfolio section and its connection status.",
      "Notice that unavailable brokerage values display as a dash, not as a verified zero.",
      "Scroll to NeuroVest paper portfolio to see simulated cash, positions, and account value.",
    ],
    takeaway:
      "Brokerage values and simulated capital are never the same account or combined into one balance.",
    action: "Open Portfolio",
    workspace: "portfolio",
  },
  {
    label: "Explore",
    title: "Inspect strategy",
    description: "Understand what a strategy decision means.",
    purpose:
      "Strategies help you explore available signals, decisions, and evaluations. A signal is information for review, not a guaranteed outcome.",
    instructions: [
      "Open the Strategies workspace.",
      "Review the available strategies and their reported information.",
      "Inspect any available decisions, signals, or evaluation results.",
      "Check whether information is available before drawing conclusions.",
    ],
    takeaway:
      "Strategy decisions do not automatically authorize live trading or promise a profitable result.",
    action: "Open Strategies",
    workspace: "strategies",
  },
  {
    label: "Simulate",
    title: "Prepare paper order",
    description: "Learn the simulated order workflow.",
    purpose:
      "The Orders workspace is where you review controlled paper-trading actions. A paper order does not trade real funds.",
    instructions: [
      "Open the Orders workspace.",
      "Review the paper-order form and available account information.",
      "Inspect the order details, risk information, and required disclosure.",
      "Only submit a simulated order if you intentionally want to test the paper workflow.",
    ],
    takeaway:
      "You can complete this lesson without submitting an order. Live execution remains disabled.",
    action: "Open Paper Orders",
    workspace: "orders",
  },
  {
    label: "Confirm",
    title: "Review history",
    description: "Find recorded activity and historical observations.",
    purpose:
      "History keeps read-only brokerage account-value observations separate from owner-scoped paper execution records.",
    instructions: [
      "Open the History workspace.",
      "Review the Brokerage account value history section.",
      "Notice that a missing current snapshot does not become an invented balance.",
      "Scroll to Paper execution history to review your simulated activity.",
    ],
    takeaway:
      "An empty history is normal for a new account. Brokerage observations are not paper orders.",
    action: "Open History",
    workspace: "history",
  },
];

const cardClass =
  "rounded-2xl border p-4 text-left transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300";

const progressVersion = "neurovest-onboarding-v1";

type SavedProgress = {
  reviewed: boolean[];
  selected: number | null;
};

function validSelection(value: unknown): number | null {
  return typeof value === "number" &&
    Number.isInteger(value) &&
    value >= 0 &&
    value < lessons.length
      ? value
      : null;
}

function validProgress(value: unknown): value is SavedProgress {
  if (
    typeof value !== "object" ||
    value === null ||
    !("reviewed" in value) ||
    !("selected" in value)
  ) {
    return false;
  }

  const record = value as Record<string, unknown>;

  return Array.isArray(record.reviewed) &&
    record.reviewed.length === lessons.length &&
    record.reviewed.every((item) => typeof item === "boolean") &&
    (record.selected === null ||
      validSelection(record.selected) !== null);
}

export default function DemoJourneyPanel({
  onOpenWorkspace,
}: DemoJourneyPanelProps) {
  const [selected, setSelected] = useState<number | null>(
    null,
  );

  const [reviewed, setReviewed] = useState<boolean[]>(
    () => lessons.map(() => false),
  );

  const [progressKey, setProgressKey] =
    useState<string | null>(null);

  const [sessionChecked, setSessionChecked] =
    useState(false);

  useEffect(() => {
    let cancelled = false;

    async function loadProgress() {
      try {
        const response = await fetch("/api/auth/session", {
          method: "GET",
          credentials: "include",
          cache: "no-store",
        });

        if (!response.ok) {
          return;
        }

        const payload: unknown = await response.json();

        if (
          typeof payload !== "object" ||
          payload === null ||
          !("authenticated" in payload) ||
          payload.authenticated !== true ||
          !("user_id" in payload) ||
          typeof payload.user_id !== "string" ||
          !payload.user_id.trim()
        ) {
          return;
        }

        const key =
          `${progressVersion}:${encodeURIComponent(payload.user_id)}`;

        if (cancelled) {
          return;
        }

        let saved: unknown = null;

        try {
          const value = window.sessionStorage.getItem(key);
          if (value !== null) {
            saved = JSON.parse(value) as unknown;
          }
        } catch {
          saved = null;
        }

        if (cancelled) {
          return;
        }

        if (validProgress(saved)) {
          setReviewed(saved.reviewed);
          setSelected(saved.selected);
        }

        setProgressKey(key);
      } catch {
        // Continue without persistence when session verification fails.
      } finally {
        if (!cancelled) {
          setSessionChecked(true);
        }
      }
    }

    void loadProgress();

    return () => {
      cancelled = true;
    };
  }, []);

  const saveProgress = (
    nextReviewed: boolean[],
    nextSelected: number | null,
  ) => {
    if (!progressKey) {
      return;
    }

    try {
      window.sessionStorage.setItem(
        progressKey,
        JSON.stringify({
          reviewed: nextReviewed,
          selected: nextSelected,
        } satisfies SavedProgress),
      );
    } catch {
      // Storage may be disabled; the guide still works in memory.
    }
  };

  const selectLesson = (index: number | null) => {
    setSelected(index);
    saveProgress(reviewed, index);
  };

  const lesson =
    selected === null ? null : lessons[selected];

  const reviewedCount =
    reviewed.filter(Boolean).length;

  const openLesson = (index: number) => {
    selectLesson(index);
  };

  const markReviewed = (index: number) => {
    const nextReviewed = reviewed.map((value, position) =>
      position === index ? true : value,
    );

    setReviewed(nextReviewed);
    saveProgress(nextReviewed, selected);
  };

  const goToWorkspace = (
    workspace: DemoWorkspace,
  ) => {
    if (selected !== null) {
      markReviewed(selected);
    }
    onOpenWorkspace(workspace);
  };

  return (
    <section
      data-testid="demo-journey-panel"
      aria-label="First five minutes onboarding guide"
      className="mb-6 overflow-hidden rounded-3xl border border-cyan-300/20 bg-[radial-gradient(circle_at_top_right,rgba(34,211,238,0.12),transparent_35%),linear-gradient(135deg,rgba(8,18,35,0.96),rgba(5,11,22,0.98))] shadow-[0_24px_70px_rgba(0,0,0,0.24)]"
    >
      <div className="border-b border-white/[0.08] px-5 py-5 sm:px-6">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="nv-eyebrow">
              First five minutes
            </p>

            <h2 className="mt-2 text-xl font-black text-white">
              Get started with NeuroVest
            </h2>

            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
              Explore each feature at your own pace and find
              the tools you need.
              Brokerage connections are optional and read-only.
              All trading actions remain in paper simulation.
            </p>
          </div>

          <span className="rounded-full border border-emerald-300/20 bg-emerald-300/[0.06] px-3 py-1.5 text-[9px] font-black uppercase tracking-[0.13em] text-emerald-200">
            No live execution
          </span>
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-3">
          <span
            className="text-xs font-semibold text-cyan-200"
            aria-live="polite"
          >
            {reviewedCount} of {lessons.length} lessons reviewed
            {!sessionChecked ? " · Checking progress…" : ""}
          </span>

          <span className="text-xs text-slate-500">
            Go in order or choose any lesson.
          </span>
        </div>
      </div>

      <div className="grid gap-3 p-4 sm:grid-cols-2 sm:p-5 xl:grid-cols-3 2xl:grid-cols-5">
        {lessons.map((item, index) => (
          <button
            key={item.title}
            type="button"
            aria-expanded={selected === index}
            aria-controls="neurovest-onboarding-lesson"
            onClick={() => openLesson(index)}
            className={[
              cardClass,
              selected === index
                ? "border-cyan-300/50 bg-cyan-300/[0.08]"
                : "border-white/[0.08] bg-white/[0.025] hover:border-cyan-300/35 hover:bg-cyan-300/[0.04]",
            ].join(" ")}
          >
            <p className="text-[10px] font-black uppercase tracking-[0.14em] text-cyan-300">
              {index + 1} · {item.label}
            </p>

            <p className="mt-2 text-sm font-black text-white">
              {item.title}
            </p>

            <p className="mt-2 text-xs leading-5 text-slate-500">
              {item.description}
            </p>

            <p className="mt-3 text-[10px] font-bold text-cyan-200">
              {reviewed[index]
                ? "Reviewed · Open lesson"
                : "Open lesson →"}
            </p>
          </button>
        ))}
      </div>

      {lesson !== null && selected !== null && (
        <div
          id="neurovest-onboarding-lesson"
          data-testid="demo-journey-lesson"
          className="border-t border-white/[0.08] bg-[#071323]/75 px-5 py-6 sm:px-6"
        >
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p className="nv-eyebrow">
                Lesson {selected + 1} of {lessons.length}
                {lesson.optional ? " · Optional" : ""}
              </p>

              <h3 className="mt-2 text-lg font-black text-white">
                {lesson.title}
              </h3>
            </div>

            <button
              type="button"
              onClick={() => selectLesson(null)}
              className="rounded-lg border border-white/[0.12] px-3 py-2 text-xs font-semibold text-slate-300 hover:text-white"
            >
              Close lesson
            </button>
          </div>

          <p className="mt-4 max-w-3xl text-sm leading-6 text-slate-300">
            {lesson.purpose}
          </p>

          <h4 className="mt-5 text-xs font-black uppercase tracking-[0.12em] text-cyan-200">
            How to explore this feature
          </h4>

          <ol className="mt-3 space-y-3">
            {lesson.instructions.map((instruction, index) => (
              <li
                key={`${selected}-${index}`}
                className="flex items-start gap-3 text-sm leading-6 text-slate-300"
              >
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-cyan-300/20 bg-cyan-300/[0.06] text-xs font-black text-cyan-200">
                  {index + 1}
                </span>
                <span>{instruction}</span>
              </li>
            ))}
          </ol>

          <div className="mt-5 rounded-xl border border-cyan-300/15 bg-cyan-300/[0.035] p-4">
            <p className="text-xs font-black uppercase tracking-[0.1em] text-cyan-200">
              What to remember
            </p>

            <p className="mt-2 text-sm leading-6 text-slate-300">
              {lesson.takeaway}
            </p>
          </div>

          <div className="mt-5 flex flex-wrap items-center gap-3">
            {lesson.href ? (
              <a
                href={lesson.href}
                onClick={() => markReviewed(selected)}
                className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl border border-cyan-200/30 bg-cyan-300 px-5 py-3 text-center text-sm font-bold text-slate-950 shadow-[0_8px_24px_rgba(34,211,238,0.16)] transition-all duration-200 hover:bg-cyan-200 hover:shadow-[0_10px_30px_rgba(34,211,238,0.25)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-200"
              >
                {lesson.action} →
              </a>
            ) : lesson.workspace ? (
              <button
                type="button"
                onClick={() =>
                  goToWorkspace(lesson.workspace!)
                }
                className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl border border-cyan-200/30 bg-cyan-300 px-5 py-3 text-center text-sm font-bold text-slate-950 shadow-[0_8px_24px_rgba(34,211,238,0.16)] transition-all duration-200 hover:bg-cyan-200 hover:shadow-[0_10px_30px_rgba(34,211,238,0.25)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-200"
              >
                {lesson.action} →
              </button>
            ) : null}

            <button
              type="button"
              onClick={() => {
                const nextReviewed = reviewed.map(
                  (value, position) =>
                    position === selected ? true : value,
                );
                const nextSelected =
                  selected < lessons.length - 1
                    ? selected + 1
                    : null;

                setReviewed(nextReviewed);
                setSelected(nextSelected);
                saveProgress(nextReviewed, nextSelected);
              }}
              className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl border border-white/20 bg-white/[0.07] px-5 py-3 text-center text-sm font-semibold text-slate-100 transition-all duration-200 hover:border-cyan-300/40 hover:bg-cyan-300/[0.10] hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-200"
            >
              {selected === lessons.length - 1
                ? "Finish guide"
                : "Mark reviewed & next"}
            </button>

            {selected > 0 && (
              <button
                type="button"
                onClick={() => selectLesson(selected - 1)}
                className="rounded-lg px-3 py-2 text-xs font-semibold text-slate-400 hover:text-white"
              >
                ← Previous lesson
              </button>
            )}

            {lesson.optional && (
              <button
                type="button"
                onClick={() => selectLesson(1)}
                className="rounded-lg px-3 py-2 text-xs font-semibold text-slate-400 hover:text-white"
              >
                Skip brokerage connection
              </button>
            )}
          </div>
        </div>
      )}
    </section>
  );
}
