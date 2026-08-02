"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import PageHeader from "../../../components/app-shell/PageHeader";

import {
  Button,
  EmptyState,
  Input,
  Panel,
  StatCard,
  StatusBadge,
  StatusMessage,
} from "../../../components/ui";

type AdminUser = {
  user_id: string;
  email: string;
  role: string;
  status: string;
  is_active: boolean;
  must_change_password: boolean;
  created_at: string | null;
  updated_at: string | null;
};

type AdminUserDetail = AdminUser & {
  active_session_count: number;
  total_session_count: number;
};

type UserListResponse = {
  items: AdminUser[];
  offset: number;
  limit: number;
  returned: number;
  total: number;
};

type ActionKind =
  | "require-password-reset"
  | "temporary-password"
  | "disable"
  | "enable"
  | "delete";

type PendingAction = {
  kind: ActionKind;
  user: AdminUser;
};

type UnknownRecord =
  Record<string, unknown>;

function isRecord(
  value: unknown,
): value is UnknownRecord {
  return (
    typeof value === "object" &&
    value !== null &&
    !Array.isArray(value)
  );
}

function errorDetail(
  payload: unknown,
  fallback: string,
): string {
  if (!isRecord(payload)) {
    return fallback;
  }

  for (const key of [
    "detail",
    "message",
    "error",
  ]) {
    const value = payload[key];

    if (
      typeof value === "string" &&
      value.trim()
    ) {
      return value;
    }
  }

  return fallback;
}

function mutationHeaders():
  HeadersInit {
  if (
    typeof document ===
    "undefined"
  ) {
    return {};
  }

  const csrf =
    document.cookie
      .split(";")
      .map((item) =>
        item.trim(),
      )
      .find((item) =>
        item.startsWith(
          "neurovest_csrf=",
        ),
      )
      ?.slice(
        "neurovest_csrf="
          .length,
      );

  if (!csrf) {
    return {};
  }

  return {
    "Content-Type":
      "application/json",
    "x-neurovest-csrf":
      decodeURIComponent(csrf),
  };
}

function displayDate(
  value: string | null,
): string {
  if (!value) {
    return "—";
  }

  const parsed = new Date(value);

  if (
    Number.isNaN(
      parsed.getTime(),
    )
  ) {
    return value;
  }

  return parsed.toLocaleString();
}

function shortId(
  value: string,
): string {
  if (value.length <= 16) {
    return value;
  }

  return (
    `${value.slice(0, 8)}…` +
    value.slice(-6)
  );
}

function protectedRole(
  role: string,
): boolean {
  return [
    "owner",
    "developer",
    "dev",
  ].includes(
    role
      .trim()
      .toLowerCase(),
  );
}

function actionTitle(
  action: PendingAction,
): string {
  switch (action.kind) {
    case "require-password-reset":
      return "Require password change";
    case "temporary-password":
      return "Issue temporary password";
    case "disable":
      return "Disable account";
    case "enable":
      return "Enable account";
    case "delete":
      return "Permanently close account";
  }
}

function actionDescription(
  action: PendingAction,
): string {
  switch (action.kind) {
    case "require-password-reset":
      return (
        "The user will be required to " +
        "choose a new password. Existing " +
        "refresh sessions will be revoked."
      );

    case "temporary-password":
      return (
        "A temporary password will replace " +
        "the current credential. It will be " +
        "displayed once and existing refresh " +
        "sessions will be revoked."
      );

    case "disable":
      return (
        "Authentication will be disabled " +
        "and existing refresh sessions " +
        "will be revoked."
      );

    case "enable":
      return (
        "The account will be restored to " +
        "active authentication status."
      );

    case "delete":
      return (
        "The identity record, refresh " +
        "sessions, and related access-token " +
        "revocation records will be " +
        "permanently deleted."
      );
  }
}

function roleTone(
  role: string,
):
  | "info"
  | "warning"
  | "violet" {
  const normalized =
    role
      .trim()
      .toLowerCase();

  if (
    normalized === "owner" ||
    normalized === "developer" ||
    normalized === "dev"
  ) {
    return "violet";
  }

  if (
    normalized === "admin" ||
    normalized ===
      "administrator"
  ) {
    return "warning";
  }

  return "info";
}

export default function AdminUsersPage() {
  const [
    users,
    setUsers,
  ] = useState<AdminUser[]>([]);

  const [
    selected,
    setSelected,
  ] =
    useState<AdminUserDetail | null>(
      null,
    );

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    refreshing,
    setRefreshing,
  ] = useState(false);

  const [
    detailLoading,
    setDetailLoading,
  ] = useState(false);

  const [
    search,
    setSearch,
  ] = useState("");

  const [
    roleFilter,
    setRoleFilter,
  ] = useState("all");

  const [
    statusFilter,
    setStatusFilter,
  ] = useState("all");

  const [
    failure,
    setFailure,
  ] = useState("");

  const [
    notice,
    setNotice,
  ] = useState("");

  const [
    pendingAction,
    setPendingAction,
  ] =
    useState<PendingAction | null>(
      null,
    );

  const [
    actionRunning,
    setActionRunning,
  ] = useState(false);

  const [
    deleteConfirmation,
    setDeleteConfirmation,
  ] = useState("");

  const [
    temporaryPassword,
    setTemporaryPassword,
  ] = useState("");

  const [
    temporaryPasswordUser,
    setTemporaryPasswordUser,
  ] = useState("");

  const loadUsers =
    useCallback(
      async (
        mode:
          | "initial"
          | "refresh" =
          "initial",
      ) => {
        if (mode === "initial") {
          setLoading(true);
        } else {
          setRefreshing(true);
        }

        setFailure("");

        try {
          const response =
            await fetch(
              "/api/admin/users?offset=0&limit=500",
              {
                method: "GET",
                credentials:
                  "same-origin",
                cache: "no-store",
              },
            );

          const payload:
            unknown =
            await response
              .json()
              .catch(() => null);

          if (!response.ok) {
            throw new Error(
              errorDetail(
                payload,
                "Unable to load " +
                  "user accounts.",
              ),
            );
          }

          const list =
            isRecord(payload) &&
            Array.isArray(
              payload.items,
            )
              ? (
                  payload as
                    unknown as
                    UserListResponse
                ).items
              : [];

          setUsers(list);

          setSelected(
            (current) => {
              if (!current) {
                return null;
              }

              const updated =
                list.find(
                  (user) =>
                    user.user_id ===
                    current.user_id,
                );

              return updated
                ? {
                    ...current,
                    ...updated,
                  }
                : null;
            },
          );
        } catch (error) {
          setFailure(
            error instanceof Error
              ? error.message
              : "Unable to load users.",
          );
        } finally {
          setLoading(false);
          setRefreshing(false);
        }
      },
      [],
    );

  useEffect(() => {
    const timer =
      window.setTimeout(
        () => {
          void loadUsers(
            "initial",
          );
        },
        0,
      );

    return () => {
      window.clearTimeout(
        timer,
      );
    };
  }, [loadUsers]);

  async function openUser(
    user: AdminUser,
  ) {
    setDetailLoading(true);
    setFailure("");
    setSelected({
      ...user,
      active_session_count: 0,
      total_session_count: 0,
    });

    try {
      const response =
        await fetch(
          `/api/admin/users/${
            encodeURIComponent(
              user.user_id,
            )
          }`,
          {
            method: "GET",
            credentials:
              "same-origin",
            cache: "no-store",
          },
        );

      const payload:
        unknown =
        await response
          .json()
          .catch(() => null);

      if (!response.ok) {
        throw new Error(
          errorDetail(
            payload,
            "Unable to load " +
              "account details.",
          ),
        );
      }

      setSelected(
        payload as
          AdminUserDetail,
      );
    } catch (error) {
      setFailure(
        error instanceof Error
          ? error.message
          : "Unable to load details.",
      );
    } finally {
      setDetailLoading(false);
    }
  }

  const roleOptions =
    useMemo(
      () => [
        "all",
        ...Array.from(
          new Set(
            users.map(
              (user) =>
                user.role,
            ),
          ),
        ).sort(),
      ],
      [users],
    );

  const filteredUsers =
    useMemo(() => {
      const query =
        search
          .trim()
          .toLowerCase();

      return users.filter(
        (user) => {
          if (
            roleFilter !== "all" &&
            user.role !== roleFilter
          ) {
            return false;
          }

          if (
            statusFilter ===
              "active" &&
            !user.is_active
          ) {
            return false;
          }

          if (
            statusFilter ===
              "disabled" &&
            user.is_active
          ) {
            return false;
          }

          if (
            statusFilter ===
              "reset" &&
            !user
              .must_change_password
          ) {
            return false;
          }

          if (!query) {
            return true;
          }

          return [
            user.email,
            user.user_id,
            user.role,
            user.status,
          ]
            .join(" ")
            .toLowerCase()
            .includes(query);
        },
      );
    }, [
      roleFilter,
      search,
      statusFilter,
      users,
    ]);

  const activeCount =
    users.filter(
      (user) =>
        user.is_active,
    ).length;

  const disabledCount =
    users.length -
    activeCount;

  const administrativeCount =
    users.filter((user) =>
      [
        "owner",
        "developer",
        "dev",
        "admin",
        "administrator",
      ].includes(
        user.role.toLowerCase(),
      ),
    ).length;

  const resetCount =
    users.filter(
      (user) =>
        user
          .must_change_password,
    ).length;

  function requestAction(
    kind: ActionKind,
    user: AdminUser,
  ) {
    if (
      protectedRole(user.role)
    ) {
      setFailure(
        "Protected developer and " +
          "owner accounts cannot be " +
          "mutated.",
      );
      return;
    }

    setFailure("");
    setNotice("");
    setDeleteConfirmation("");
    setPendingAction({
      kind,
      user,
    });
  }

  async function executeAction() {
    if (!pendingAction) {
      return;
    }

    if (
      pendingAction.kind ===
        "delete" &&
      deleteConfirmation !==
        pendingAction.user.email
    ) {
      setFailure(
        "Enter the account email " +
          "exactly before permanent " +
          "closure.",
      );
      return;
    }

    const action =
      pendingAction;

    const userId =
      encodeURIComponent(
        action.user.user_id,
      );

    let method:
      | "POST"
      | "DELETE" = "POST";

    let path =
      `/api/admin/users/${userId}`;

    switch (action.kind) {
      case "require-password-reset":
        path +=
          "/require-password-reset";
        break;
      case "temporary-password":
        path +=
          "/temporary-password";
        break;
      case "disable":
        path += "/disable";
        break;
      case "enable":
        path += "/enable";
        break;
      case "delete":
        method = "DELETE";
        break;
    }

    setActionRunning(true);
    setFailure("");
    setNotice("");

    try {
      const response =
        await fetch(path, {
          method,
          credentials:
            "same-origin",
          cache: "no-store",
          headers:
            mutationHeaders(),
          body:
            method === "POST"
              ? "{}"
              : undefined,
        });

      const payload:
        unknown =
        await response
          .json()
          .catch(() => null);

      if (!response.ok) {
        throw new Error(
          errorDetail(
            payload,
            `${actionTitle(
              action,
            )} failed.`,
          ),
        );
      }

      if (
        action.kind ===
        "temporary-password"
      ) {
        const password =
          isRecord(payload) &&
          typeof payload
            .temporary_password ===
            "string"
            ? payload
                .temporary_password
            : "";

        if (!password) {
          throw new Error(
            "The password was changed, " +
              "but the temporary value " +
              "was not returned.",
          );
        }

        setTemporaryPassword(
          password,
        );
        setTemporaryPasswordUser(
          action.user.email,
        );
      }

      setNotice(
        `${actionTitle(action)} ` +
          `completed for ` +
          `${action.user.email}.`,
      );

      if (
        action.kind ===
        "delete"
      ) {
        setSelected(null);
      }

      setPendingAction(null);
      setDeleteConfirmation("");

      await loadUsers("refresh");

      if (
        action.kind !==
          "delete" &&
        selected?.user_id ===
          action.user.user_id
      ) {
        await openUser(
          action.user,
        );
      }
    } catch (error) {
      setFailure(
        error instanceof Error
          ? error.message
          : `${actionTitle(
              action,
            )} failed.`,
      );
    } finally {
      setActionRunning(false);
    }
  }

  async function copyPassword() {
    try {
      await navigator.clipboard
        .writeText(
          temporaryPassword,
        );

      setNotice(
        "Temporary password copied.",
      );
    } catch {
      setFailure(
        "Clipboard access was " +
          "unavailable. Copy the " +
          "password manually.",
      );
    }
  }

  return (
    <main className="space-y-6">
      <PageHeader
        eyebrow="NeuroVest Administration"
        title="User operations center."
        description="Live canonical identity records with server-authoritative account controls, session protection, and explicit confirmation for sensitive actions."
        badge={
          <StatusBadge tone="success">
            Database connected
          </StatusBadge>
        }
        actions={
          <Button
            variant="primary"
            size="lg"
            disabled={
              loading ||
              refreshing
            }
            onClick={() => {
              void loadUsers(
                "refresh",
              );
            }}
          >
            {refreshing
              ? "Refreshing…"
              : "Refresh database"}
          </Button>
        }
      />

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <StatCard
          label="Database accounts"
          value={
            loading
              ? "…"
              : users.length
          }
          detail="Canonical identities"
          accent="cyan"
        />

        <StatCard
          label="Active"
          value={
            loading
              ? "…"
              : activeCount
          }
          detail="Authentication enabled"
          accent="emerald"
        />

        <StatCard
          label="Disabled"
          value={
            loading
              ? "…"
              : disabledCount
          }
          detail="Authentication blocked"
          accent="red"
        />

        <StatCard
          label="Password reset"
          value={
            loading
              ? "…"
              : resetCount
          }
          detail="Change required"
          accent="amber"
        />

        <StatCard
          label="Administrative"
          value={
            loading
              ? "…"
              : administrativeCount
          }
          detail="Elevated identities"
          accent="violet"
        />
      </section>

      {failure && (
        <StatusMessage tone="danger">
          {failure}
        </StatusMessage>
      )}

      {notice && (
        <StatusMessage tone="success">
          {notice}
        </StatusMessage>
      )}

      <Panel
        variant="elevated"
        className="overflow-hidden"
      >
        <div className="grid gap-4 border-b border-white/10 p-5 lg:grid-cols-[minmax(0,1fr)_auto_auto]">
          <label>
            <span className="sr-only">
              Search accounts
            </span>

            <Input
              type="search"
              value={search}
              onChange={(event) => {
                setSearch(
                  event.target.value,
                );
              }}
              placeholder="Search email, user ID, role or status"
            />
          </label>

          <select
            value={roleFilter}
            onChange={(event) => {
              setRoleFilter(
                event.target.value,
              );
            }}
            aria-label="Filter accounts by role"
            className="nv-input min-w-[170px]"
          >
            {roleOptions.map(
              (role) => (
                <option
                  key={role}
                  value={role}
                >
                  {role === "all"
                    ? "All roles"
                    : role}
                </option>
              ),
            )}
          </select>

          <select
            value={statusFilter}
            onChange={(event) => {
              setStatusFilter(
                event.target.value,
              );
            }}
            aria-label="Filter accounts by status"
            className="nv-input min-w-[180px]"
          >
            <option value="all">
              All states
            </option>

            <option value="active">
              Active
            </option>

            <option value="disabled">
              Disabled
            </option>

            <option value="reset">
              Reset required
            </option>
          </select>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/[0.06] px-5 py-3">
          <p className="text-xs text-slate-500">
            Showing{" "}
            <strong className="text-slate-300">
              {filteredUsers.length}
            </strong>{" "}
            of{" "}
            <strong className="text-slate-300">
              {users.length}
            </strong>{" "}
            canonical identity records
          </p>

          <StatusBadge tone="neutral">
            Server-authoritative
          </StatusBadge>
        </div>

        {loading ? (
          <div
            className="flex min-h-[300px] items-center justify-center p-12 text-center"
            role="status"
          >
            <div>
              <div
                className="mx-auto h-9 w-9 animate-spin rounded-full border-2 border-slate-700 border-t-cyan-300"
                aria-hidden="true"
              />

              <p className="mt-5 text-sm text-slate-400">
                Loading canonical identity database…
              </p>
            </div>
          </div>
        ) : filteredUsers.length === 0 ? (
          <EmptyState
            title="No accounts found"
            description="No canonical identity records match the current search and filter combination."
            action={
              <Button
                variant="secondary"
                onClick={() => {
                  setSearch("");
                  setRoleFilter("all");
                  setStatusFilter("all");
                }}
              >
                Clear filters
              </Button>
            }
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[1200px] text-left">
              <thead className="bg-white/[0.025]">
                <tr className="border-b border-white/10">
                  {[
                    "Account",
                    "Role",
                    "State",
                    "Password",
                    "Created",
                    "Updated",
                    "Quick actions",
                  ].map(
                    (heading) => (
                      <th
                        key={heading}
                        className="px-5 py-4 text-[10px] font-black uppercase tracking-[0.2em] text-slate-500"
                      >
                        {heading}
                      </th>
                    ),
                  )}
                </tr>
              </thead>

              <tbody className="divide-y divide-white/[0.06]">
                {filteredUsers.map(
                  (user) => {
                    const protectedAccount =
                      protectedRole(
                        user.role,
                      );

                    return (
                      <tr
                        key={user.user_id}
                        className="transition hover:bg-white/[0.025]"
                      >
                        <td className="px-5 py-5">
                          <button
                            type="button"
                            onClick={() => {
                              void openUser(
                                user,
                              );
                            }}
                            className="text-left"
                          >
                            <p className="font-black text-white transition hover:text-cyan-200">
                              {user.email}
                            </p>

                            <p
                              title={
                                user.user_id
                              }
                              className="mt-2 font-mono text-[11px] text-slate-600"
                            >
                              {shortId(
                                user.user_id,
                              )}
                            </p>
                          </button>
                        </td>

                        <td className="px-5 py-5">
                          <StatusBadge
                            tone={
                              roleTone(
                                user.role,
                              )
                            }
                          >
                            {user.role}
                          </StatusBadge>

                          {protectedAccount && (
                            <p className="mt-2 text-[10px] font-black uppercase tracking-[0.14em] text-fuchsia-400">
                              Protected
                            </p>
                          )}
                        </td>

                        <td className="px-5 py-5">
                          <StatusBadge
                            tone={
                              user.is_active
                                ? "success"
                                : "danger"
                            }
                          >
                            {user.status}
                          </StatusBadge>
                        </td>

                        <td className="px-5 py-5">
                          {user.must_change_password ? (
                            <StatusBadge tone="warning">
                              Change required
                            </StatusBadge>
                          ) : (
                            <span className="text-sm text-slate-500">
                              Current
                            </span>
                          )}
                        </td>

                        <td className="px-5 py-5 text-sm text-slate-400">
                          {displayDate(
                            user.created_at,
                          )}
                        </td>

                        <td className="px-5 py-5 text-sm text-slate-400">
                          {displayDate(
                            user.updated_at,
                          )}
                        </td>

                        <td className="px-5 py-5">
                          <div className="flex flex-wrap gap-2">
                            <Button
                              variant="secondary"
                              size="sm"
                              onClick={() => {
                                void openUser(
                                  user,
                                );
                              }}
                            >
                              Inspect
                            </Button>

                            <Button
                              variant="secondary"
                              size="sm"
                              disabled={
                                protectedAccount
                              }
                              onClick={() => {
                                requestAction(
                                  user.is_active
                                    ? "disable"
                                    : "enable",
                                  user,
                                );
                              }}
                            >
                              {user.is_active
                                ? "Disable"
                                : "Enable"}
                            </Button>

                            <Button
                              variant="ghost"
                              size="sm"
                              disabled={
                                protectedAccount
                              }
                              onClick={() => {
                                requestAction(
                                  "require-password-reset",
                                  user,
                                );
                              }}
                            >
                              Reset
                            </Button>
                          </div>
                        </td>
                      </tr>
                    );
                  },
                )}
              </tbody>
            </table>
          </div>
        )}
      </Panel>

      {selected && (
        <div className="fixed inset-0 z-40 flex justify-end bg-black/70 backdrop-blur-sm">
          <button
            type="button"
            aria-label="Close account panel"
            className="flex-1"
            onClick={() => {
              setSelected(null);
            }}
          />

          <aside className="h-full w-full max-w-xl overflow-y-auto border-l border-white/10 bg-[#050816] p-6 shadow-2xl shadow-black sm:p-8">
            <div className="flex items-start justify-between gap-5">
              <div className="min-w-0">
                <p className="nv-eyebrow">
                  Canonical identity
                </p>

                <h2 className="mt-3 break-all text-2xl font-black text-white">
                  {selected.email}
                </h2>
              </div>

              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setSelected(null);
                }}
              >
                Close
              </Button>
            </div>

            {detailLoading ? (
              <div
                className="mt-10 text-sm text-slate-400"
                role="status"
              >
                Loading account details…
              </div>
            ) : (
              <>
                <div className="mt-7 grid gap-3 sm:grid-cols-2">
                  {[
                    [
                      "Role",
                      selected.role,
                    ],
                    [
                      "Status",
                      selected.status,
                    ],
                    [
                      "Active sessions",
                      selected.active_session_count,
                    ],
                    [
                      "Total sessions",
                      selected.total_session_count,
                    ],
                    [
                      "Created",
                      displayDate(
                        selected.created_at,
                      ),
                    ],
                    [
                      "Updated",
                      displayDate(
                        selected.updated_at,
                      ),
                    ],
                  ].map(
                    ([label, value]) => (
                      <Panel
                        key={label}
                        variant="muted"
                        className="p-4"
                      >
                        <p className="nv-stat-label">
                          {label}
                        </p>

                        <p className="mt-2 break-all text-sm font-bold text-slate-200">
                          {value}
                        </p>
                      </Panel>
                    ),
                  )}
                </div>

                <Panel
                  variant="muted"
                  className="mt-5 p-5"
                >
                  <p className="nv-stat-label">
                    User ID
                  </p>

                  <code className="mt-3 block break-all text-xs text-cyan-200">
                    {selected.user_id}
                  </code>
                </Panel>

                <section className="mt-7">
                  <p className="nv-eyebrow">
                    Account controls
                  </p>

                  {protectedRole(
                    selected.role,
                  ) ? (
                    <div className="mt-4">
                      <StatusMessage tone="warning">
                        This is a protected developer or owner identity. Backend policy prohibits administrative mutation.
                      </StatusMessage>
                    </div>
                  ) : (
                    <div className="mt-4 grid gap-3 sm:grid-cols-2">
                      <Button
                        variant="secondary"
                        className="min-h-[4.5rem] justify-start text-left"
                        onClick={() => {
                          requestAction(
                            "require-password-reset",
                            selected,
                          );
                        }}
                      >
                        Require password change
                      </Button>

                      <Button
                        variant="secondary"
                        className="min-h-[4.5rem] justify-start text-left"
                        onClick={() => {
                          requestAction(
                            "temporary-password",
                            selected,
                          );
                        }}
                      >
                        Issue temporary password
                      </Button>

                      <Button
                        variant="secondary"
                        className="min-h-[4.5rem] justify-start text-left"
                        onClick={() => {
                          requestAction(
                            selected.is_active
                              ? "disable"
                              : "enable",
                            selected,
                          );
                        }}
                      >
                        {selected.is_active
                          ? "Disable account"
                          : "Enable account"}
                      </Button>
                    </div>
                  )}
                </section>

                {!protectedRole(
                  selected.role,
                ) && (
                  <section className="mt-8 border-t border-red-300/15 pt-7">
                    <p className="text-xs font-black uppercase tracking-[0.24em] text-red-300">
                      Danger zone
                    </p>

                    <Button
                      variant="danger"
                      size="lg"
                      className="mt-4 w-full justify-start"
                      onClick={() => {
                        requestAction(
                          "delete",
                          selected,
                        );
                      }}
                    >
                      Permanently close account
                    </Button>
                  </section>
                )}
              </>
            )}
          </aside>
        </div>
      )}

      {pendingAction && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-5 backdrop-blur-sm">
          <Panel
            variant="elevated"
            role="dialog"
            aria-modal="true"
            aria-labelledby="admin-action-title"
            className="w-full max-w-lg p-7"
          >
            <p className="text-xs font-black uppercase tracking-[0.24em] text-amber-300">
              Explicit confirmation
            </p>

            <h2
              id="admin-action-title"
              className="mt-4 text-2xl font-black text-white"
            >
              {actionTitle(
                pendingAction,
              )}
            </h2>

            <p className="mt-3 break-all text-sm font-bold text-cyan-200">
              {pendingAction.user.email}
            </p>

            <p className="mt-5 text-sm leading-7 text-slate-400">
              {actionDescription(
                pendingAction,
              )}
            </p>

            {pendingAction.kind ===
              "delete" && (
              <div className="mt-5">
                <label
                  htmlFor="delete-account-confirmation"
                  className="text-xs font-black uppercase tracking-[0.18em] text-red-300"
                >
                  Enter the account email
                </label>

                <Input
                  id="delete-account-confirmation"
                  value={
                    deleteConfirmation
                  }
                  onChange={(event) => {
                    setDeleteConfirmation(
                      event.target.value,
                    );
                  }}
                  placeholder={
                    pendingAction.user
                      .email
                  }
                  className="mt-3"
                />
              </div>
            )}

            <div className="mt-7 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
              <Button
                variant="ghost"
                disabled={
                  actionRunning
                }
                onClick={() => {
                  setPendingAction(
                    null,
                  );
                  setDeleteConfirmation(
                    "",
                  );
                }}
              >
                Cancel
              </Button>

              <Button
                variant={
                  pendingAction.kind ===
                  "delete"
                    ? "danger"
                    : "primary"
                }
                disabled={
                  actionRunning ||
                  (
                    pendingAction.kind ===
                      "delete" &&
                    deleteConfirmation !==
                      pendingAction.user
                        .email
                  )
                }
                onClick={() => {
                  void executeAction();
                }}
              >
                {actionRunning
                  ? "Processing…"
                  : actionTitle(
                      pendingAction,
                    )}
              </Button>
            </div>
          </Panel>
        </div>
      )}

      {temporaryPassword && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/85 p-5 backdrop-blur-sm">
          <Panel
            variant="elevated"
            role="dialog"
            aria-modal="true"
            aria-labelledby="temporary-password-title"
            className="w-full max-w-xl p-7"
          >
            <p className="nv-eyebrow">
              One-time credential display
            </p>

            <h2
              id="temporary-password-title"
              className="mt-4 text-2xl font-black text-white"
            >
              Temporary password generated
            </h2>

            <p className="mt-3 break-all text-sm text-slate-400">
              Account:{" "}
              {temporaryPasswordUser}
            </p>

            <code className="mt-6 block break-all rounded-xl border border-cyan-300/15 bg-black/40 p-5 text-lg font-black tracking-wider text-cyan-100">
              {temporaryPassword}
            </code>

            <div className="mt-4">
              <StatusMessage tone="warning">
                Copy this value now. It will be removed from page memory when dismissed.
              </StatusMessage>
            </div>

            <div className="mt-7 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
              <Button
                variant="ghost"
                onClick={() => {
                  setTemporaryPassword(
                    "",
                  );
                  setTemporaryPasswordUser(
                    "",
                  );
                }}
              >
                Dismiss permanently
              </Button>

              <Button
                variant="primary"
                onClick={() => {
                  void copyPassword();
                }}
              >
                Copy password
              </Button>
            </div>
          </Panel>
        </div>
      )}
    </main>
  );
}
