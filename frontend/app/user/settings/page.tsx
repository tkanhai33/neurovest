"use client";

import AccountSecurityPanel from "./AccountSecurityPanel";


import {
  getSnapTradeStatus,
  resolveSnapTradeState,
  type SnapTradeState,
} from "../../../services/snaptradeService";

import {
  applyNotificationAction,
  fetchNotifications,
  type NotificationListResponse,
  type NotificationRecord,
} from "../../../services/notificationService";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import Link from "next/link";

import PageHeader from "../../../components/app-shell/PageHeader";

import {
  Button,
  Panel,
  StatusBadge,
  StatusMessage,
} from "../../../components/ui";

function brokerageStatusLabel(
  state: SnapTradeState | null
): string {
  if (
    state?.connected
    || state?.connection_status
      === "connected"
  ) {
    return "Connected";
  }

  if (
    state?.registered
    || state?.connection_status
      === "registered"
  ) {
    return "Registered";
  }

  return "Not connected";
}





function formatTimestamp(
  value: string | null
): string {
  if (!value) {
    return "Not recorded";
  }

  const date = new Date(
    value
  );

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return value;
  }

  return date.toLocaleString();
}

function badgeTone(
  severity: string
):
  | "info"
  | "success"
  | "warning"
  | "danger"
  | "violet" {
  const normalized =
    severity.toLowerCase();

  if (
    normalized === "critical" ||
    normalized === "error" ||
    normalized === "danger"
  ) {
    return "danger";
  }

  if (
    normalized === "warning" ||
    normalized === "warn"
  ) {
    return "warning";
  }

  if (
    normalized === "success"
  ) {
    return "success";
  }

  if (
    normalized === "system"
  ) {
    return "violet";
  }

  return "info";
}

export default function UserSettingsPage() {
  // F12-R2-NOTIFICATION-FILTERS
  const [notificationSearch, setNotificationSearch] = useState("");
  const [notificationView, setNotificationView] = useState("all");
  const [notificationSeverity, setNotificationSeverity] = useState("all");
  const [notificationPage, setNotificationPage] = useState(1);

  const [
    notifications,
    setNotifications,
  ] = useState<
    NotificationRecord[]
  >([]);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState<
    string | null
  >(null);

  const [
    activeNotification,
    setActiveNotification,
  ] = useState<
    string | null
  >(null);

  const [
    lastUpdated,
    setLastUpdated,
  ] = useState<
    string | null
  >(null);

  const [
    brokerageState,
    setBrokerageState,
  ] = useState<
    SnapTradeState | null
  >(null);

  const [
    brokerageLoading,
    setBrokerageLoading,
  ] = useState(
    true
  );

  const [
    brokerageError,
    setBrokerageError,
  ] = useState<
    string | null
  >(null);


  const unreadCount = useMemo(
    () =>
      notifications.filter(
        (record) =>
          !record.is_read
      ).length,
    [
      notifications,
    ]
  );

  const acknowledgedCount =
    useMemo(
      () =>
        notifications.filter(
          (record) =>
            Boolean(
              record.acknowledged_at
            )
        ).length,
      [
        notifications,
      ]
    );


  const filteredNotifications = useMemo(() => {
    const query = notificationSearch.trim().toLowerCase();

    return notifications.filter((record) => {
      const searchText = [
        record.title,
        record.message,
        record.severity,
        record.delivery_status,
      ].filter(Boolean).join(" ").toLowerCase();

      if (query && !searchText.includes(query)) {
        return false;
      }

      if (notificationSeverity !== "all") {
        if (record.severity.toLowerCase() !== notificationSeverity) {
          return false;
        }
      }

      if (notificationView === "unread" && record.is_read) {
        return false;
      }

      if (notificationView === "read" && !record.is_read) {
        return false;
      }

      if (
        notificationView === "acknowledged" &&
        !record.acknowledged_at
      ) {
        return false;
      }

      if (
        notificationView === "unacknowledged" &&
        Boolean(record.acknowledged_at)
      ) {
        return false;
      }

      return true;
    });
  }, [
    notifications,
    notificationSearch,
    notificationView,
    notificationSeverity,
  ]);

  const notificationPageCount = Math.max(
    1,
    Math.ceil(filteredNotifications.length / 20),
  );

  const currentNotificationPage = Math.min(
    notificationPage,
    notificationPageCount,
  );

  const visibleNotifications = filteredNotifications.slice(
    (currentNotificationPage - 1) * 20,
    currentNotificationPage * 20,
  );

  const notificationSeverities = Array.from(
    new Set(
      notifications
        .map(record => record.severity.toLowerCase())
        .filter(Boolean),
    ),
  ).sort();

  function clearNotificationFilters() {
    setNotificationSearch("");
    setNotificationView("all");
    setNotificationSeverity("all");
    setNotificationPage(1);
  }

  const loadBrokerageStatus =
    useCallback(
      async () => {
        setBrokerageLoading(
          true
        );

        setBrokerageError(
          null
        );

        try {
          const payload =
            await getSnapTradeStatus();

          setBrokerageState(
            resolveSnapTradeState(
              payload
            )
          );

        } catch (
          requestError
        ) {

          setBrokerageState(
            null
          );

          setBrokerageError(
            requestError instanceof Error
              ? requestError.message
              : "Unable to load brokerage status."
          );

        } finally {

          setBrokerageLoading(
            false
          );
        }
      },
      []
    );


  const loadNotifications =
    useCallback(
      async () => {
        setLoading(true);
        setError(null);

        try {
          const body =
            await fetchNotifications(
              {
                limit: 100,
              }
            );

          setNotifications(
            Array.isArray(
              body.records
            )
              ? body.records
              : []
          );

          setLastUpdated(
            new Date().toLocaleString()
          );

        } catch (
          requestError
        ) {

          setNotifications([]);

          setError(
            requestError instanceof Error
              ? requestError.message
              : "Unable to load notifications."
          );

        } finally {

          setLoading(false);
        }
      },
      []
    );

  useEffect(() => {
    queueMicrotask(() => { void loadNotifications(); });
  }, [
    loadNotifications,
  ]);


  useEffect(() => {
    queueMicrotask(() => { void loadBrokerageStatus(); });
  }, [
    loadBrokerageStatus,
  ]);

  async function applyAction(
    notificationId: string,
    action:
      | "read"
      | "acknowledge"
  ): Promise<void> {
    setActiveNotification(
      notificationId
    );

    setError(null);

    try {
      await applyNotificationAction(
        notificationId,
        action,
      );

      await loadNotifications();

    } catch (
      requestError
    ) {

      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to update notification."
      );

    } finally {

      setActiveNotification(
        null
      );
    }
  }

  const brokerageConnected =
    brokerageState?.connected === true
    || brokerageState?.connection_status
      === "connected";

  const brokerageRegistered =
    brokerageConnected
    || brokerageState?.registered === true
    || brokerageState?.connection_status
      === "registered";


  return (
    <main className="space-y-4 sm:space-y-5">
      <PageHeader
        eyebrow="Your account"
        title="Account settings"
        description="Review your brokerage connection and manage important account notifications."
        badge={
          <StatusBadge tone="info">
            Personal account
          </StatusBadge>
        }
        actions={
          <Button
            type="button"
            variant="secondary"
            disabled={loading}
            onClick={() => {
              void loadNotifications();
            }}
          >
            {loading
              ? "Loading…"
              : "Refresh notifications"}
          </Button>
        }
      />

      <nav
        aria-label="Account settings sections"
        className="flex flex-wrap items-center gap-2 rounded-2xl border border-white/[0.08] bg-slate-900/50 p-2 sm:p-3"
      >
        <a
          href="#profile-security"
          className="inline-flex min-h-10 items-center rounded-xl border border-cyan-300/20 bg-cyan-300/[0.07] px-4 py-2 text-sm font-semibold text-cyan-100 transition hover:bg-cyan-300/[0.14] focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-300"
        >
          Profile &amp; Security
        </a>
        <a
          href="#brokerage-settings"
          className="inline-flex min-h-10 items-center rounded-xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-200 transition hover:bg-white/[0.07] focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-300"
        >
          Brokerage connection
        </a>
        <a
          href="#notification-settings"
          className="inline-flex min-h-10 items-center rounded-xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-200 transition hover:bg-white/[0.07] focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-300"
        >
          Notifications
        </a>
        <a
          href="#billing-settings"
          className="inline-flex min-h-10 items-center rounded-xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-200 transition hover:bg-white/[0.07] focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-300"
        >
          Billing
        </a>
      </nav>

      {/* F12_ACCOUNT_SECURITY_INSIDE_SETTINGS */}
      <AccountSecurityPanel />

      <Panel
        variant="default"
        className="p-4 sm:p-5"
        data-testid="settings-brokerage-connection"
      >
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="min-w-0">
            <p className="nv-eyebrow">
              Brokerage connection
            </p>

            <h2
              id="brokerage-settings"
              className="nv-section-title scroll-mt-24"
            >
              Brokerage connection
            </h2>

            <p className="nv-section-description max-w-3xl">
              See whether your brokerage is connected and when your
              account information was last updated. Connection management
              remains in the dedicated Brokerage workspace.
            </p>
          </div>

          <StatusBadge
            tone={
              brokerageConnected
                ? "success"
                : brokerageRegistered
                  ? "info"
                  : "warning"
            }
          >
            {
              brokerageLoading
                ? "Loading"
                : brokerageStatusLabel(
                    brokerageState
                  )
            }
          </StatusBadge>
        </div>


        {brokerageError ? (
          <div className="mt-5">
            <StatusMessage tone="warning">
              {brokerageError}
            </StatusMessage>
          </div>
        ) : null}


        <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
            <p className="nv-stat-label">
              Connection
            </p>

            <p
              data-testid="settings-brokerage-status" aria-live="polite"
              className="mt-3 text-lg font-black text-white"
            >
              {
                brokerageLoading
                  ? "Loading"
                  : brokerageStatusLabel(
                      brokerageState
                    )
              }
            </p>
          </div>


          <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
            <p className="nv-stat-label">
              Access mode
            </p>

            <p
              data-testid="settings-brokerage-access-mode"
              className="mt-3 text-lg font-black text-white"
            >
              Read only
            </p>
          </div>


          <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
            <p className="nv-stat-label">
              Trading
            </p>

            <p
              data-testid="settings-brokerage-trading"
              className="mt-3 text-lg font-black text-white"
            >
              Disabled
            </p>
          </div>


          <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
            <p className="nv-stat-label">
              Last synchronization
            </p>

            <p
              data-testid="settings-brokerage-last-sync" aria-live="polite"
              className="mt-3 break-words text-sm font-bold text-white"
            >
              {
                brokerageLoading
                  ? "Loading"
                  : brokerageState?.last_synced_at
                    ? formatTimestamp(
                        brokerageState.last_synced_at
                      )
                    : "Not synchronized"
              }
            </p>
          </div>
        </div>


        <div className="mt-4 grid gap-3 border-t border-white/[0.07] pt-4 md:grid-cols-2">
          <div>
            <p className="nv-stat-label">
              Provider status
            </p>

            <p
              data-testid="settings-brokerage-provider-status" aria-live="polite"
              className="mt-2 text-sm text-slate-200"
            >
              {
                brokerageState?.connection_status
                || brokerageStatusLabel(
                  brokerageState
                )
              }
            </p>
          </div>


          <div>
            <p className="nv-stat-label">
              Synchronization status
            </p>

            <p
              data-testid="settings-brokerage-sync-status" aria-live="polite"
              className="mt-2 text-sm text-slate-200"
            >
              {
                brokerageState?.last_sync_status
                || "No synchronization result"
              }
            </p>
          </div>
        </div>


        <div className="mt-6 flex flex-wrap items-center justify-between gap-4 border-t border-white/[0.07] pt-5">
          <p className="max-w-2xl text-sm leading-6 text-slate-400">
            To connect or refresh a supported brokerage account,
            use the Brokerage page. NeuroVest does not place live
            brokerage trades.
          </p>

          <Link
            href="/user/brokerage"
            className="nv-button nv-button-secondary nv-button-sm"
            data-testid="settings-manage-brokerage"
          >
            Manage brokerage connection
          </Link>
        </div>
      </Panel>


      <section className="grid gap-4 md:grid-cols-3">
        <Panel
          variant="elevated"
          className="p-5"
        >
          <p className="nv-stat-label">
            Delivered
          </p>

          <p
            data-testid="notification-count"
            className="nv-section-title"
          >
            {notifications.length}
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            Messages delivered to your account.
          </p>
        </Panel>

        <Panel
          variant="elevated"
          className="p-5"
        >
          <p className="nv-stat-label">
            Unread
          </p>

          <p
            data-testid="notification-unread-count"
            className="nv-section-title"
          >
            {unreadCount}
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            Notifications awaiting review.
          </p>
        </Panel>

        <Panel
          variant="elevated"
          className="p-5"
        >
          <p className="nv-stat-label">
            Acknowledged
          </p>

          <p
            data-testid="notification-acknowledged-count"
            className="nv-section-title"
          >
            {acknowledgedCount}
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            Notifications you have acknowledged.
          </p>
        </Panel>
      </section>

      {error ? (
        <StatusMessage tone="danger">
          {error}
        </StatusMessage>
      ) : null}

      <Panel
        variant="default"
        className="p-4 sm:p-5"
      >
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="nv-eyebrow">
              Notifications
            </p>

            <h2
              id="notification-settings"
              className="nv-section-title scroll-mt-24"
            >
              Notifications and alerts
            </h2>

            <p className="nv-section-description max-w-3xl">
              Review important account updates, mark messages as read,
              and acknowledge notifications that need your attention.
            </p>
          </div>

          <StatusBadge tone="info">
            Account notifications
          </StatusBadge>
        </div>

        <p className="mt-4 text-xs text-slate-500">
          {lastUpdated
            ? `Last refreshed ${lastUpdated}.`
            : "Waiting for the qualified notification source."}
        </p>


        <div
          data-testid="f12-notification-filters"
          className="mt-5 rounded-2xl border border-white/[0.08] bg-white/[0.025] p-4"
        >
          <div className="grid gap-3 md:grid-cols-3">
            <label className="block text-xs font-semibold text-slate-400">
              Search notifications
              <input
                type="search"
                data-testid="f12-notification-search"
                className="nv-input mt-2 w-full"
                value={notificationSearch}
                onChange={(event) => {
                  setNotificationSearch(event.target.value);
                  setNotificationPage(1);
                }}
                placeholder="Title, message, severity..."
              />
            </label>

            <label className="block text-xs font-semibold text-slate-400">
              Review status
              <select
                data-testid="f12-notification-status"
                className="nv-input mt-2 w-full"
                value={notificationView}
                onChange={(event) => {
                  setNotificationView(event.target.value);
                  setNotificationPage(1);
                }}
              >
                <option value="all">All notifications</option>
                <option value="unread">Unread only</option>
                <option value="read">Read only</option>
                <option value="unacknowledged">
                  Not acknowledged
                </option>
                <option value="acknowledged">
                  Acknowledged
                </option>
              </select>
            </label>

            <label className="block text-xs font-semibold text-slate-400">
              Severity
              <select
                data-testid="f12-notification-severity"
                className="nv-input mt-2 w-full"
                value={notificationSeverity}
                onChange={(event) => {
                  setNotificationSeverity(event.target.value);
                  setNotificationPage(1);
                }}
              >
                <option value="all">All severities</option>
                {notificationSeverities.map(severity => (
                  <option key={severity} value={severity}>
                    {severity}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
            <p
              data-testid="f12-notification-match-count"
              className="text-sm text-slate-400"
            >
              {loading
                ? "Loading notifications..."
                : error
                  ? "Notification results unavailable"
                  : `${filteredNotifications.length} matching of ${notifications.length} loaded records`}
            </p>

            <button
              type="button"
              onClick={clearNotificationFilters}
              className="rounded-xl border border-white/15 px-4 py-2 text-sm text-slate-200 hover:bg-white/[0.05]"
            >
              Clear filters
            </button>
          </div>

          <p className="mt-3 text-xs leading-5 text-slate-500">
            Filters and pages operate on up to 100 notifications
            returned by the current account API request.
            They do not search older server records.
          </p>
        </div>

        <div className="mt-6">
          {loading ? (
            <StatusMessage tone="info">
              Loading notifications…
            </StatusMessage>
          ) : error ? (
            <StatusMessage tone="danger">
              Notifications could not be loaded. Use Refresh notifications to retry.
            </StatusMessage>
          ) : notifications.length === 0 ? (
            <StatusMessage tone="info">
              No notifications are currently available for this account.
            </StatusMessage>
          ) : filteredNotifications.length === 0 ? (
            <StatusMessage tone="info">
              No notifications match the selected filters.
            </StatusMessage>
          ) : (
            <div
              data-testid="notification-records"
              className="space-y-3"
            >
              {visibleNotifications.map(
                (
                  notification
                ) => {
                  const busy =
                    activeNotification ===
                    notification.id;

                  return (
                    <article
                      key={
                        notification.id
                      }
                      className="rounded-2xl border border-white/[0.08] bg-white/[0.035] p-4 shadow-sm sm:p-5"
                    >
                      <div className="flex flex-wrap items-start justify-between gap-4">
                        <div className="min-w-0">
                          <div className="flex flex-wrap items-center gap-2">
                            <StatusBadge
                              tone={badgeTone(
                                notification.severity
                              )}
                            >
                              {
                                notification.severity
                              }
                            </StatusBadge>

                            <StatusBadge
                              tone={
                                notification.is_read
                                  ? "success"
                                  : "warning"
                              }
                            >
                              {notification.is_read
                                ? "Read"
                                : "Unread"}
                            </StatusBadge>

                            <StatusBadge tone="info">
                              {
                                notification.delivery_status
                              }
                            </StatusBadge>
                          </div>

                          <h3 className="nv-card-title mt-4">
                            {
                              notification.title
                            }
                          </h3>

                          <p className="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-300">
                            {
                              notification.message
                            }
                          </p>
                        </div>

                        <div className="flex flex-wrap gap-2">
                          {!notification.is_read ? (
                            <Button
                              type="button"
                              variant="secondary"
                              disabled={busy}
                              onClick={() => {
                                void applyAction(
                                  notification.id,
                                  "read"
                                );
                              }}
                            >
                              Mark read
                            </Button>
                          ) : null}

                          {!notification.acknowledged_at ? (
                            <Button
                              type="button"
                              variant="primary"
                              disabled={busy}
                              onClick={() => {
                                void applyAction(
                                  notification.id,
                                  "acknowledge"
                                );
                              }}
                            >
                              Acknowledge
                            </Button>
                          ) : (
                            <StatusBadge tone="success">
                              Acknowledged
                            </StatusBadge>
                          )}
                        </div>
                      </div>

                      <dl className="mt-5 grid gap-3 text-sm md:grid-cols-3">
                        <div className="rounded-xl border border-white/[0.06] bg-black/20 p-3">
                          <dt className="nv-stat-label">
                            Delivered
                          </dt>

                          <dd className="mt-2 text-slate-200">
                            {formatTimestamp(
                              notification.delivered_at
                            )}
                          </dd>
                        </div>

                        <div className="rounded-xl border border-white/[0.06] bg-black/20 p-3">
                          <dt className="nv-stat-label">
                            Read
                          </dt>

                          <dd className="mt-2 text-slate-200">
                            {formatTimestamp(
                              notification.read_at
                            )}
                          </dd>
                        </div>

                        <div className="rounded-xl border border-white/[0.06] bg-black/20 p-3">
                          <dt className="nv-stat-label">
                            Acknowledged
                          </dt>

                          <dd className="mt-2 text-slate-200">
                            {formatTimestamp(
                              notification.acknowledged_at
                            )}
                          </dd>
                        </div>
                      </dl>
                    </article>
                  );
                }
              )}
            </div>
          )}

        {!loading && !error && filteredNotifications.length > 0 && (
          <div className="mt-5 flex flex-wrap items-center justify-between gap-3">
            <p className="text-sm text-slate-400">
              Page {currentNotificationPage} of {notificationPageCount}
              {" · "}
              Showing {visibleNotifications.length} notifications
            </p>
            <div className="flex gap-2">
              <button
                type="button"
                data-testid="f12-notification-previous"
                disabled={currentNotificationPage <= 1}
                onClick={() => setNotificationPage(currentNotificationPage - 1)}
                className="rounded-xl border border-white/15 px-4 py-2 text-sm text-white disabled:opacity-35"
              >
                Previous
              </button>
              <button
                type="button"
                data-testid="f12-notification-next"
                disabled={currentNotificationPage >= notificationPageCount}
                onClick={() => setNotificationPage(currentNotificationPage + 1)}
                className="rounded-xl border border-white/15 px-4 py-2 text-sm text-white disabled:opacity-35"
              >
                Next
              </button>
            </div>
          </div>
        )}
        </div>
      </Panel>
          
    
      <Panel
        variant="default"
        className="p-4 sm:p-5"
        data-testid="settings-billing-coming-soon"
      >
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="nv-eyebrow">Membership</p>
            <h2 id="billing-settings" className="nv-section-title scroll-mt-24">
              Billing
            </h2>
            <p className="nv-section-description max-w-3xl">
              Subscription and payment controls are coming soon. Checkout
              cannot be started from Settings yet.
            </p>
          </div>
          <StatusBadge tone="info">Coming soon</StatusBadge>
        </div>
        <Link
          href="/#pricing"
          className="mt-5 inline-flex rounded-xl border border-white/15 px-4 py-2 text-sm font-semibold text-slate-200 transition hover:bg-white/[0.07] focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-300"
        >
          View plans
        </Link>
      </Panel>
    </main>
  );
}



