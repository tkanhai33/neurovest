"use client";

import { useEffect, useState } from "react";

import {
  getPortfolioPositions,
  type PortfolioPosition,
} from "../../services/portfolioService";

const API = "/api/v1";

export type AnalyticsSummary = {
  total_trades_logged?: number;
  buy_signals_count?: number;
  sell_signals_count?: number;
  execution_success_percentage?: number;
};

export function useDashboardData() {
  const [hydrated, setHydrated] = useState(false);
  const [positions, setPositions] = useState<PortfolioPosition[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const [portfolioResult, analyticsResponse] = await Promise.all([
          getPortfolioPositions(),
          fetch(`${API}/analytics`, {
            cache: "no-store",
          }),
        ]);

        if (!analyticsResponse.ok) {
          throw new Error(
            `Analytics request failed: ${analyticsResponse.status}`
          );
        }

        const analyticsResult =
          (await analyticsResponse.json()) as AnalyticsSummary;

        if (cancelled) {
          return;
        }

        setPositions(portfolioResult.positions || []);
        setAnalytics(analyticsResult);
      } catch (error) {
        console.error("Dashboard data load failed:", error);
      }
    }

    const hydrationTimer = setTimeout(() => {
      if (!cancelled) {
        setHydrated(true);
      }
    }, 0);

    const firstLoad = setTimeout(() => {
      void load();
    }, 0);

    const pollingTimer = setInterval(() => {
      void load();
    }, 5000);

    return () => {
      cancelled = true;
      clearTimeout(hydrationTimer);
      clearTimeout(firstLoad);
      clearInterval(pollingTimer);
    };
  }, []);

  return {
    hydrated,
    positions,
    analytics,
  };
}
