"use client";

import Link from "next/link";
import {
  useEffect,
  useState,
} from "react";
import {
  useRouter,
} from "next/navigation";

import FloatingChatWidget from "../../components/chat/FloatingChatWidget";
import PageHeader from "../../components/app-shell/PageHeader";
import { Panel, StatCard, StatusMessage } from "../../components/ui";

type SessionPayload = {
  authenticated?: boolean;
  role?: string;
  subscription_tier?: string;
};

type AnalyticsPayload = {
  total_trades_logged?: number;
  buy_signals_count?: number;
  sell_signals_count?: number;
  risk_blocked_percentage?: number;
  execution_success_percentage?: number;
};

type PortfolioPayload = {
  positions?: unknown[];
  active_exposure_count?: number;
};

type MarketPayload = Record<
  string,
  unknown
>;

function displayValue(
  value: unknown,
): string {
  if (
    typeof value === "number" ||
    typeof value === "string"
  ) {
    return String(value);
  }

  return "—";
}

export default function UserDashboardPage() {
  const router = useRouter();

  const [session, setSession] =
    useState<SessionPayload | null>(null);

  const [analytics, setAnalytics] =
    useState<AnalyticsPayload>({});

  const [portfolio, setPortfolio] =
    useState<PortfolioPayload>({});

  const [market, setMarket] =
    useState<MarketPayload>({});

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function load(): Promise<void> {
      try {
        const sessionResponse =
          await fetch(
            "/api/auth/session",
            {
              method: "GET",
              credentials: "include",
              cache: "no-store",
            },
          );

        if (
          sessionResponse.status === 401
        ) {
          router.replace(
            "/login?next=/user/dashboard",
          );
          return;
        }

        if (!sessionResponse.ok) {
          throw new Error(
            "Your account session could not be loaded.",
          );
        }

        const sessionPayload =
          (await sessionResponse.json()) as
            SessionPayload;

        const [
          analyticsResponse,
          portfolioResponse,
          marketResponse,
        ] = await Promise.all([
          fetch("/api/v1/analytics", {
            cache: "no-store",
          }),
          fetch(
            "/api/v1/portfolio/positions",
            {
              cache: "no-store",
            },
          ),
          fetch(
            "/api/v1/market/live-price/AAPL",
            {
              cache: "no-store",
            },
          ),
        ]);

        if (
          !analyticsResponse.ok ||
          !portfolioResponse.ok ||
          !marketResponse.ok
        ) {
          throw new Error(
            "Some dashboard information is temporarily unavailable.",
          );
        }

        const analyticsPayload =
          (await analyticsResponse.json()) as
            AnalyticsPayload;

        const portfolioPayload =
          (await portfolioResponse.json()) as
            PortfolioPayload;

        const marketPayload =
          (await marketResponse.json()) as
            MarketPayload;

        if (!active) {
          return;
        }

        setSession(sessionPayload);
        setAnalytics(analyticsPayload);
        setPortfolio(portfolioPayload);
        setMarket(marketPayload);
      } catch (caught) {
        if (!active) {
          return;
        }

        setError(
          caught instanceof Error
            ? caught.message
            : "The dashboard could not be loaded.",
        );
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    void load();

    return () => {
      active = false;
    };
  }, [router]);

  const positionCount =
    Array.isArray(portfolio.positions)
      ? portfolio.positions.length
      : portfolio.active_exposure_count ??
        0;

  const marketPrice =
    market.price ??
    market.last_price ??
    market.current_price ??
    market.close;

  return (
    <main className="min-h-screen bg-[#030712] px-5 py-8 text-white sm:px-8 lg:px-12">
      <div className="mx-auto max-w-[1500px]">
        <PageHeader
          eyebrow="NeuroVest Account"
          title="Your market workspace."
          description="Review your paper portfolio, market intelligence, risk information, and conversations with Neuro."
          badge={
            <StatusMessage tone="success">
              Authenticated
            </StatusMessage>
          }
        />

        {error && (
          <Panel variant="default" className="mt-6 p-5">
            <StatusMessage tone="danger">
              {error}
            </StatusMessage>
          </Panel>
        )}

        <section className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard
            label="Logged decisions"
            value={
              loading ? "…" : displayValue(
                analytics.total_trades_logged,
              )
            }
            detail="Total decisions logged"
            accent="cyan"
          />

          <StatCard
            label="Paper positions"
            value={
              loading ? "…" : displayValue(positionCount)
            }
            detail="Active exposures"
            accent="emerald"
          />

          <StatCard
            label="Buy signals"
            value={
              loading ? "…" : displayValue(
                analytics.buy_signals_count,
              )
            }
            detail="Accumulation signals"
            accent="amber"
          />

          <StatCard
            label="Execution health"
            value={
              loading || 
              analytics.execution_success_percentage === undefined
                ? "…"
                : `${analytics.execution_success_percentage}%`
            }
            detail="Success rate"
            accent="violet"
          />
        </section>

        <section className="mt-6 grid gap-6 xl:grid-cols-[1.25fr_0.75fr]">
          <Panel variant="default" className="p-7">
            <p className="text-xs font-black uppercase tracking-[0.28em] text-cyan-300">
              Personal overview
            </p>

            <h2 className="mt-4 text-3xl font-black">
              Start with what matters today.
            </h2>

            <div className="mt-7 grid gap-4 md:grid-cols-3">
              <Link
                href="/user/chat"
                className="rounded-2xl border border-fuchsia-300/20 bg-fuchsia-400/5 p-5 transition hover:border-fuchsia-300/40"
              >
                <p className="text-sm font-black text-fuchsia-200">
                  Talk with Neuro
                </p>
                <p className="mt-2 text-sm leading-6 text-slate-500">
                  Ask questions and review your simulated activity.
                </p>
              </Link>

              <div className="rounded-2xl border border-cyan-300/15 bg-cyan-400/5 p-5">
                <p className="text-sm font-black text-cyan-200">
                  AAPL snapshot
                </p>
                <p className="mt-2 text-2xl font-black">
                  {loading
                    ? "…"
                    : displayValue(
                        marketPrice,
                      )}
                </p>
                <p className="mt-1 text-xs text-slate-500">
                  Current approved market observation
                </p>
              </div>

              <div className="rounded-2xl border border-emerald-300/15 bg-emerald-400/5 p-5">
                <p className="text-sm font-black text-emerald-200">
                  Safety status
                </p>
                <p className="mt-2 text-lg font-black">
                  Simulation only
                </p>
                <p className="mt-1 text-xs text-slate-500">
                  Live broker execution remains disabled
                </p>
              </div>
            </div>
          </Panel>

          <Panel variant="default" className="p-7">
            <p className="text-xs font-black uppercase tracking-[0.28em] text-amber-300">
              Account access
            </p>

            <h2 className="mt-4 text-2xl font-black">
              Your workspace boundaries
            </h2>

            <div className="mt-6 space-y-3">
              {[
                "Personal portfolio access",
                "Paper broker access",
                "Neuro chat access",
                "Profile and journal access",
              ].map((item) => (
                <div
                  key={item}
                  className="flex items-center gap-3 rounded-xl border border-white/5 bg-white/[0.025] px-4 py-3 text-sm text-slate-300"
                >
                  <span className="h-2 w-2 rounded-full bg-emerald-300" />
                  {item}
                </div>
              ))}
            </div>
          </Panel>
        </section>
      </div>

      <FloatingChatWidget />
    </main>
  );
}
