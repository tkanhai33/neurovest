"use client";

import {
  useCallback,
  useEffect,
  useState,
} from "react";

import PageHeader from "../../../components/app-shell/PageHeader";

import {
  Panel,
  StatusBadge,
  StatusMessage,
} from "../../../components/ui";

type AuditRecord = Record<
  string,
  unknown
>;

type AuditResponse = {
  status?: string;
  access_mode?: string;
  mutations_enabled?: boolean;
  count?: number;
  records?: AuditRecord[];
  detail?: string;
};

function displayValue(
  value: unknown
): string {
  if (
    value === null ||
    value === undefined
  ) {
    return "—";
  }

  if (typeof value === "string") {
    return value;
  }

  if (
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return String(value);
  }

  try {
    return JSON.stringify(
      value,
      null,
      2
    );
  } catch {
    return String(value);
  }
}

function recordIdentifier(
  record: AuditRecord,
  index: number
): string {
  const candidate =
    record.event_id ??
    record.id ??
    record.idempotency_key ??
    record.trace_id;

  return typeof candidate === "string"
    ? candidate
    : `audit-record-${index + 1}`;
}

export default function AdminAuditPage() {
  const [
    records,
    setRecords,
  ] = useState<AuditRecord[]>([]);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState<string | null>(null);

  const [
    lastUpdated,
    setLastUpdated,
  ] = useState<string | null>(null);

  const loadAuditRecords = useCallback(
    async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(
          "/api/v1/admin/audit?limit=100",
          {
            method: "GET",
            credentials: "include",
            cache: "no-store",
            headers: {
              Accept: "application/json",
            },
          }
        );

        const body =
          (await response.json()) as AuditResponse;

        if (!response.ok) {
          throw new Error(
            body.detail ||
              `Audit request failed with status ${response.status}.`
          );
        }

        setRecords(
          Array.isArray(body.records)
            ? body.records
            : []
        );

        setLastUpdated(
          new Date().toLocaleString()
        );
      } catch (requestError) {
        setRecords([]);

        setError(
          requestError instanceof Error
            ? requestError.message
            : "Unable to load audit records."
        );
      } finally {
        setLoading(false);
      }
    },
    []
  );

  useEffect(() => {
    queueMicrotask(() => { void loadAuditRecords(); });
  }, [loadAuditRecords]);

  return (
    <main className="space-y-6">
      <PageHeader
        eyebrow="NeuroVest Administration"
        title="Decision audit."
        description="Review server-authoritative decision records, administrative events, and immutable audit history."
        badge={
          <StatusBadge tone="info">
            Read only
          </StatusBadge>
        }
        actions={
          <button
            type="button"
            className="nv-button nv-button-secondary"
            disabled={loading}
            onClick={() => {
              void loadAuditRecords();
            }}
          >
            {loading
              ? "Loading…"
              : "Refresh records"}
          </button>
        }
      />

      <section className="grid gap-4 md:grid-cols-3">
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

          <p className="mt-3 text-sm leading-6 text-slate-400">
            Audit records cannot be changed from this workspace.
          </p>
        </Panel>

        <Panel
          variant="elevated"
          className="p-5"
        >
          <p className="nv-stat-label">
            Evidence source
          </p>

          <p className="mt-3 text-xl font-black text-white">
            Server authoritative
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            Local estimates and fabricated audit events are never displayed.
          </p>
        </Panel>

        <Panel
          variant="elevated"
          className="p-5"
        >
          <p className="nv-stat-label">
            Records returned
          </p>

          <p
            data-testid="admin-audit-count"
            className="mt-3 text-xl font-black text-white"
          >
            {records.length}
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            {lastUpdated
              ? `Last refreshed ${lastUpdated}.`
              : "Waiting for the qualified audit source."}
          </p>
        </Panel>
      </section>

      <Panel
        variant="default"
        className="p-6"
      >
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="nv-eyebrow">
              Audit record inventory
            </p>

            <h2 className="mt-3 text-2xl font-black text-white">
              Decision and administrative history
            </h2>

            <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-400">
              Records appear here only when returned through the authenticated,
              read-only decision-audit facade.
            </p>
          </div>

          <StatusBadge tone="success">
            Immutable boundary
          </StatusBadge>
        </div>

        <div className="mt-6">
          {loading ? (
            <StatusMessage tone="info">
              Loading qualified audit records…
            </StatusMessage>
          ) : error ? (
            <StatusMessage tone="danger">
              {error}
            </StatusMessage>
          ) : records.length === 0 ? (
            <StatusMessage tone="info">
              No qualified audit records are currently available.
            </StatusMessage>
          ) : (
            <div
              data-testid="admin-audit-records"
              className="space-y-4"
            >
              {records.map(
                (
                  record,
                  index
                ) => (
                  <article
                    key={recordIdentifier(
                      record,
                      index
                    )}
                    className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-5"
                  >
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div>
                        <p className="nv-stat-label">
                          Audit record
                        </p>

                        <p className="mt-2 break-all text-sm font-bold text-white">
                          {recordIdentifier(
                            record,
                            index
                          )}
                        </p>
                      </div>

                      <StatusBadge tone="violet">
                        Immutable
                      </StatusBadge>
                    </div>

                    <dl className="mt-5 grid gap-3 md:grid-cols-2">
                      {Object.entries(
                        record
                      ).map(
                        ([
                          key,
                          value,
                        ]) => (
                          <div
                            key={key}
                            className="rounded-xl border border-white/[0.06] bg-black/20 p-3"
                          >
                            <dt className="text-xs font-bold uppercase tracking-[0.16em] text-slate-500">
                              {key}
                            </dt>

                            <dd className="mt-2 whitespace-pre-wrap break-words text-sm text-slate-200">
                              {displayValue(
                                value
                              )}
                            </dd>
                          </div>
                        )
                      )}
                    </dl>
                  </article>
                )
              )}
            </div>
          )}
        </div>
      </Panel>
    </main>
  );
}
