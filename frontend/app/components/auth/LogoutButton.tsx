"use client";

import { useState } from "react";

import {
  csrfHeaders,
} from "../../../lib/clientCsrf";

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

export default function LogoutButton() {
  const [pending, setPending] =
    useState(false);

  async function logout() {
    setPending(true);

    try {
      await fetch(
        "/api/auth/logout",
        {
          method: "POST",
          headers: csrfHeaders(),
          cache: "no-store",
        }
      );
    } finally {
      clearPrivateBrowserCaches();
      window.location.replace("/login");
    }
  }

  return (
    <button
      type="button"
      onClick={logout}
      disabled={pending}
      className="inline-flex min-h-11 items-center justify-center rounded-xl border border-red-300/20 bg-slate-950/90 px-4 py-2 text-xs font-black uppercase tracking-[0.16em] text-red-200 backdrop-blur transition hover:border-red-300/40 disabled:opacity-50"
    >
      {pending ? "Signing out…" : "Sign out"}
    </button>
  );
}
