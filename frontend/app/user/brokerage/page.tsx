"use client";

import {
  createSnapTradeConnectionPortal,
  getSnapTradeStatus,
  registerSnapTradeUser,
  resolveConnectionPortalUrl,
  resolveSnapTradeState,
  synchronizeSnapTrade,
  type SnapTradeState,
} from "../../../services/snaptradeService";

import {
  useCallback,
  useEffect,
  useState,
} from "react";

import PageHeader from "../../../components/app-shell/PageHeader";

import {
  Button,
  Panel,
  StatusBadge,
  StatusMessage,
} from "../../../components/ui";

function statusLabel(
  state: SnapTradeState | null
): string {
  if (
    state?.connected ||
    state?.connection_status ===
      "connected"
  ) {
    return "Connected";
  }

  if (
    state?.registered ||
    state?.connection_status ===
      "registered"
  ) {
    return "Registered";
  }

  return "Not connected";
}

export default function BrokeragePage() {
  const [
    state,
    setState,
  ] = useState<SnapTradeState | null>(
    null
  );

  const [
    loading,
    setLoading,
  ] = useState(
    true
  );

  const [
    working,
    setWorking,
  ] = useState(
    false
  );

  const [
    error,
    setError,
  ] = useState<string | null>(
    null
  );

  const [
    message,
    setMessage,
  ] = useState<string | null>(
    null
  );

  const loadStatus = useCallback(
    async () => {
      setLoading(
        true
      );

      setError(
        null
      );

      try {
        const payload =
          await getSnapTradeStatus();

        setState(
          resolveSnapTradeState(
            payload
          )
        );

      } catch (
        requestError
      ) {

        setError(
          requestError instanceof Error
            ? requestError.message
            : "Unable to load SnapTrade status."
        );

      } finally {

        setLoading(
          false
        );
      }
    },
    []
  );


  useEffect(() => {
    queueMicrotask(() => { void loadStatus(); });
  }, [loadStatus]);



  async function registerIdentity() {
    setWorking(
      true
    );

    setError(
      null
    );

    setMessage(
      null
    );

    try {
      const payload =
        await registerSnapTradeUser();

      setState(
        resolveSnapTradeState(
          payload
        )
      );

      setMessage(
        "The authenticated NeuroVest account is registered with the read-only brokerage boundary."
      );

      await loadStatus();
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "SnapTrade registration failed."
      );
    } finally {
      setWorking(
        false
      );
    }
  }

  async function openConnectionPortal() {
    const portalWindow =
      window.open(
        "",
        "_blank"
      );

    setWorking(
      true
    );

    setError(
      null
    );

    setMessage(
      null
    );

    try {
      const payload =
        await createSnapTradeConnectionPortal();

      const portalUrl =
        resolveConnectionPortalUrl(
          payload
        );

      if (!portalUrl) {
        throw new Error(
          "The backend did not return a connection-portal URL."
        );
      }

      if (
        portalWindow
        && !portalWindow.closed
      ) {
        portalWindow.opener =
          null;

        portalWindow.location.replace(
          portalUrl
        );

      } else {

        window.location.assign(
          portalUrl
        );
      }

      setMessage(
        "The read-only SnapTrade connection portal was opened."
      );
    } catch (requestError) {
      if (
        portalWindow
        && !portalWindow.closed
      ) {
        portalWindow.close();
      }

      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to open the SnapTrade connection portal."
      );
    } finally {
      setWorking(
        false
      );
    }
  }

  async function synchronizeConnection() {
    setWorking(
      true
    );

    setError(
      null
    );

    setMessage(
      null
    );

    try {
      const payload =
        await synchronizeSnapTrade();

      setState(
        resolveSnapTradeState(
          payload
        )
      );

      setMessage(
        "Read-only brokerage synchronization completed."
      );

      await loadStatus();
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "SnapTrade synchronization failed."
      );
    } finally {
      setWorking(
        false
      );
    }
  }

  const connected =
    state?.connected === true ||
    state?.connection_status ===
      "connected";

  const registered =
    connected ||
    state?.registered === true ||
    state?.connection_status ===
      "registered";

  return (
    <main className="space-y-6">
      <PageHeader
        eyebrow="NeuroVest Brokerage"
        title="Read-only brokerage connection."
        description="Connect and synchronize brokerage account information through SnapTrade. Trading and broker-order execution remain disabled."
        badge={
          <StatusBadge
            tone={
              connected
                ? "success"
                : registered
                  ? "info"
                  : "warning"
            }
          >
            {loading
              ? "Loading"
              : statusLabel(
                  state
                )}
          </StatusBadge>
        }
        actions={
          <Button
            type="button"
            variant="secondary"
            disabled={
              loading ||
              working
            }
            onClick={() => {
              void loadStatus();
            }}
          >
            Refresh status
          </Button>
        }
      />

      {error ? (
        <StatusMessage tone="danger">
          {error}
        </StatusMessage>
      ) : null}

      {message ? (
        <StatusMessage tone="success">
          {message}
        </StatusMessage>
      ) : null}

      <section className="grid gap-4 md:grid-cols-4">
        <Panel
          variant="elevated"
          className="p-5"
        >
          <p className="nv-stat-label">
            Connection
          </p>

          <p
            data-testid="snaptrade-connection-status"
            className="mt-3 text-xl font-black text-white"
          >
            {loading
              ? "Loading"
              : statusLabel(
                  state
                )}
          </p>
        </Panel>

        <Panel
          variant="elevated"
          className="p-5"
        >
          <p className="nv-stat-label">
            Access mode
          </p>

          <p className="mt-3 text-xl font-black text-white">
            Read only
          </p>
        </Panel>

        <Panel
          variant="elevated"
          className="p-5"
        >
          <p className="nv-stat-label">
            Trading
          </p>

          <p className="mt-3 text-xl font-black text-white">
            Disabled
          </p>
        </Panel>

        <Panel
          variant="elevated"
          className="p-5"
        >
          <p className="nv-stat-label">
            Last synchronization
          </p>

          <p className="mt-3 break-words text-sm font-bold text-white">
            {state?.last_synced_at ||
              "Not synchronized"}
          </p>
        </Panel>
      </section>

      <Panel
        variant="default"
        className="p-6"
      >
        <p className="nv-eyebrow">
          Brokerage lifecycle
        </p>

        <h2 className="nv-section-title">
          Register, connect, and synchronize
        </h2>

        <p className="nv-section-description max-w-3xl">
          Registration creates an encrypted, owner-scoped SnapTrade identity.
          The connection portal is forced to read-only mode. Synchronization
          imports brokerage account information without enabling trading.
        </p>

        <div className="mt-6 flex flex-wrap gap-3">
          <Button
            data-testid="snaptrade-register"
            type="button"
            variant="secondary"
            disabled={
              working ||
              loading ||
              registered
            }
            onClick={() => {
              void registerIdentity();
            }}
          >
            {registered
              ? "Identity registered"
              : "Register identity"}
          </Button>

          <Button
            data-testid="snaptrade-connect"
            type="button"
            variant="primary"
            disabled={
              working ||
              loading ||
              !registered
            }
            onClick={() => {
              void openConnectionPortal();
            }}
          >
            Open read-only portal
          </Button>

          <Button
            data-testid="snaptrade-synchronize"
            type="button"
            variant="secondary"
            disabled={
              working ||
              loading ||
              !registered
            }
            onClick={() => {
              void synchronizeConnection();
            }}
          >
            Synchronize accounts
          </Button>
        </div>
      </Panel>

      <Panel
        variant="elevated"
        className="p-6"
      >
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="nv-eyebrow">
              Safety boundary
            </p>

            <h2 className="nv-section-title">
              Brokerage execution remains unavailable
            </h2>
          </div>

          <StatusBadge tone="success">
            Read only
          </StatusBadge>
        </div>

        <div className="mt-5 grid gap-4 md:grid-cols-2">
          <div>
            <p className="nv-stat-label">
              Connection status
            </p>

            <p className="mt-2 text-sm text-slate-200">
              {state?.connection_status ||
                statusLabel(
                  state
                )}
            </p>
          </div>

          <div>
            <p className="nv-stat-label">
              Synchronization status
            </p>

            <p className="mt-2 text-sm text-slate-200">
              {state?.last_sync_status ||
                "No synchronization result"}
            </p>
          </div>

          <div>
            <p className="nv-stat-label">
              Provider identity
            </p>

            <p className="mt-2 break-all text-sm text-slate-200">
              {state?.snaptrade_user_id ||
                "Not available"}
            </p>
          </div>

          <div>
            <p className="nv-stat-label">
              Live broker orders
            </p>

            <p className="mt-2 text-sm text-slate-200">
              Blocked
            </p>
          </div>
        </div>
      </Panel>
    </main>
  );
}
