"use client";

import { useEffect, useState } from "react";

import {
  getSnapTradeStatus,
  resolveSnapTradeState,
} from "../../../services/snaptradeService";

import { StatusBadge } from "../../../components/ui";

type ConnectionStatus =
  | "loading"
  | "connected"
  | "registered"
  | "not_connected"
  | "unavailable";

export default function BrokerageConnectionBadge() {
  const [status, setStatus] =
    useState<ConnectionStatus>("loading");

  useEffect(() => {
    let active = true;

    async function loadStatus() {
      try {
        const payload = await getSnapTradeStatus();
        const state = resolveSnapTradeState(payload);

        if (!active) return;

        if (
          state?.connected === true ||
          state?.connection_status === "connected"
        ) {
          setStatus("connected");
        } else if (
          state?.registered === true ||
          state?.connection_status === "registered"
        ) {
          setStatus("registered");
        } else {
          setStatus("not_connected");
        }
      } catch {
        if (active) {
          setStatus("unavailable");
        }
      }
    }

    void loadStatus();

    return () => {
      active = false;
    };
  }, []);

  const presentation = {
    loading: {
      label: "Checking connection",
      tone: "info",
    },
    connected: {
      label: "Connected",
      tone: "success",
    },
    registered: {
      label: "Registered",
      tone: "info",
    },
    not_connected: {
      label: "Not connected",
      tone: "warning",
    },
    unavailable: {
      label: "Status unavailable",
      tone: "warning",
    },
  } as const;

  const current = presentation[status];

  return (
    <StatusBadge
      tone={current.tone}
    >
      {current.label}
    </StatusBadge>
  );
}
