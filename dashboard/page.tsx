"use client";

import {
  useEffect,
  useState,
} from "react";

import LogoutButton from "../components/auth/LogoutButton";
import FloatingChatWidget from "../components/chat/FloatingChatWidget";
import {
  DashboardHeader,
  DashboardStats,
  Sidebar,
  type DashboardTab,
} from "../components/layout/DashboardShell";
import WorkspaceRouter from "../components/layout/WorkspaceRouter";
import MarketTickerBanner from "../components/ticker/MarketTickerBanner";
import { useDashboardData } from "../hooks/useDashboardData";

import {
  loadSafeUiPreferences,
  saveSafeUiPreferences,
} from "../../lib/uiPreferences";

export default function DashboardPage() {
  const [activeTab, setActiveTab] =
    useState<DashboardTab>("overview");

  useEffect(() => {
    const restored =
      loadSafeUiPreferences()
        .activeWorkspace;

    if (!restored) {
      return;
    }

    const restoreWorkspace =
      window.setTimeout(
        () => {
          setActiveTab(
            restored as DashboardTab
          );
        },
        0,
      );

    return () => {
      window.clearTimeout(
        restoreWorkspace
      );
    };
  }, []);

  useEffect(() => {
    saveSafeUiPreferences({
      activeWorkspace: activeTab,
    });
  }, [activeTab]);

  const {
    hydrated,
    positions,
    analytics,
  } = useDashboardData();

  return (
    <main className="min-h-screen bg-[#050816] font-mono text-white">
      <LogoutButton />
      <div className="flex min-h-screen">
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
        />

        <section className="min-w-0 flex-1 px-5 py-5 lg:px-8">
          <MarketTickerBanner />

          <DashboardHeader
            activeTab={activeTab}
            hydrated={hydrated}
            setActiveTab={setActiveTab}
          />

          <DashboardStats analytics={analytics} />

          <WorkspaceRouter
            activeTab={activeTab}
            positions={positions}
          />

          <FloatingChatWidget />
        </section>
      </div>
    </main>
  );
}
