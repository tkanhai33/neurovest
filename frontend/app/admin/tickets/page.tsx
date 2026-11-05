"use client";

import {
  FormEvent,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import PageHeader from "../../../components/app-shell/PageHeader";

import {
  Button,
  Panel,
  StatusBadge,
  StatusMessage,
} from "../../../components/ui";

import {
  csrfHeaders,
} from "../../../lib/clientCsrf";


type TicketStatus =
  | "OPEN"
  | "WAITING_FOR_USER"
  | "WAITING_FOR_ADMINISTRATOR"
  | "RESOLVED"
  | "CLOSED";


type TicketPriority =
  | "LOW"
  | "NORMAL"
  | "HIGH"
  | "URGENT";


type SupportMessage = {
  id: string;
  ticket_id: string;
  author_user_id: string;
  author_role: "USER" | "ADMINISTRATOR";
  message: string;
  created_at: string;
};


type SupportTicket = {
  id: string;
  owner_user_id: string;
  subject: string;
  status: TicketStatus;
  priority: TicketPriority;
  created_at: string;
  updated_at: string;
  resolved_at?: string | null;
  closed_at?: string | null;
  messages?: SupportMessage[];
};


async function parseJson<T>(
  response: Response,
): Promise<T> {
  const body = await response.json();

  if (!response.ok) {
    const detail =
      typeof body?.detail === "string"
        ? body.detail
        : "Administrative support request failed.";

    throw new Error(detail);
  }

  return body as T;
}


function statusTone(
  status: TicketStatus,
):
  | "success"
  | "warning"
  | "danger"
  | "info"
  | "violet" {
  switch (status) {
    case "OPEN":
      return "info";

    case "WAITING_FOR_USER":
      return "warning";

    case "WAITING_FOR_ADMINISTRATOR":
      return "violet";

    case "RESOLVED":
      return "success";

    case "CLOSED":
      return "danger";
  }
}


export default function AdminTicketsPage() {
  const [
    tickets,
    setTickets,
  ] = useState<SupportTicket[]>([]);

  const [
    selected,
    setSelected,
  ] = useState<SupportTicket | null>(
    null,
  );

  const [
    message,
    setMessage,
  ] = useState("");

  const [
    selectedStatus,
    setSelectedStatus,
  ] = useState<TicketStatus>("OPEN");

  const [
    selectedPriority,
    setSelectedPriority,
  ] = useState<TicketPriority>(
    "NORMAL",
  );

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    mutating,
    setMutating,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState<string | null>(
    null,
  );


  const loadTickets = useCallback(
    async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(
          "/api/v1/admin/support/tickets",
          {
            cache: "no-store",
          },
        );

        if (
          response.status === 401
        ) {
          window.location.assign(
            "/login?next=/admin/tickets",
          );
          return;
        }

        const payload =
          await parseJson<
            SupportTicket[]
          >(response);

        setTickets(payload);
      } catch (caught) {
        setError(
          caught instanceof Error
            ? caught.message
            : "Unable to load administrative support tickets.",
        );
      } finally {
        setLoading(false);
      }
    },
    [],
  );


  const loadTicket = useCallback(
    async (
      ticketId: string,
    ) => {
      setError(null);

      try {
        const response = await fetch(
          `/api/v1/admin/support/tickets/${encodeURIComponent(
            ticketId,
          )}`,
          {
            cache: "no-store",
          },
        );

        const payload =
          await parseJson<
            SupportTicket
          >(response);

        setSelected(payload);
        setSelectedStatus(
          payload.status,
        );
        setSelectedPriority(
          payload.priority,
        );
      } catch (caught) {
        setError(
          caught instanceof Error
            ? caught.message
            : "Unable to load administrative support ticket.",
        );
      }
    },
    [],
  );


  useEffect(() => {
    queueMicrotask(() => { void loadTickets(); });
  }, [loadTickets]);


  const needsAdministrator =
    useMemo(
      () =>
        tickets.filter(
          (ticket) =>
            ticket.status ===
              "OPEN" ||
            ticket.status ===
              "WAITING_FOR_ADMINISTRATOR",
        ).length,
      [tickets],
    );


  async function sendMessage(
    event: FormEvent,
  ) {
    event.preventDefault();

    if (
      !selected ||
      !message.trim()
    ) {
      return;
    }

    setMutating(true);
    setError(null);

    try {
      const response = await fetch(
        `/api/v1/admin/support/tickets/${encodeURIComponent(
          selected.id,
        )}/messages`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
            ...csrfHeaders(),
          },
          body: JSON.stringify({
            message:
              message.trim(),
          }),
        },
      );

      const updated =
        await parseJson<
          SupportTicket
        >(response);

      setMessage("");
      setSelected(updated);
      setSelectedStatus(
        updated.status,
      );
      setSelectedPriority(
        updated.priority,
      );

      await loadTickets();
    } catch (caught) {
      setError(
        caught instanceof Error
          ? caught.message
          : "Unable to send administrator support response.",
      );
    } finally {
      setMutating(false);
    }
  }


  async function updateTicket() {
    if (!selected) {
      return;
    }

    setMutating(true);
    setError(null);

    try {
      const response = await fetch(
        `/api/v1/admin/support/tickets/${encodeURIComponent(
          selected.id,
        )}`,
        {
          method: "PATCH",
          headers: {
            "Content-Type":
              "application/json",
            ...csrfHeaders(),
          },
          body: JSON.stringify({
            status:
              selectedStatus,
            priority:
              selectedPriority,
          }),
        },
      );

      const updated =
        await parseJson<
          SupportTicket
        >(response);

      setSelected(updated);
      setSelectedStatus(
        updated.status,
      );
      setSelectedPriority(
        updated.priority,
      );

      await loadTickets();
    } catch (caught) {
      setError(
        caught instanceof Error
          ? caught.message
          : "Unable to update support ticket.",
      );
    } finally {
      setMutating(false);
    }
  }


  return (
    <div
      className="space-y-6"
      data-testid="admin-support-tickets"
    >
      <PageHeader
        eyebrow="NeuroVest Administration"
        title="Support tickets."
        description="Review real user support conversations, respond as the authenticated administrator, and manage ticket state without impersonating the user."
        badge={
          <StatusBadge tone="violet">
            Administrative
          </StatusBadge>
        }
      />

      {error ? (
        <StatusMessage tone="danger">
          {error}
        </StatusMessage>
      ) : null}

      <div className="grid gap-4 md:grid-cols-3">
        <Panel variant="elevated">
          <p className="nv-stat-label">
            Total tickets
          </p>

          <p className="mt-3 text-3xl font-black text-white">
            {tickets.length}
          </p>
        </Panel>

        <Panel variant="elevated">
          <p className="nv-stat-label">
            Needs administrator
          </p>

          <p className="mt-3 text-3xl font-black text-amber-200">
            {needsAdministrator}
          </p>
        </Panel>

        <Panel variant="elevated">
          <p className="nv-stat-label">
            Boundary
          </p>

          <p className="mt-3 text-sm font-bold text-cyan-200">
            Authenticated administrator
          </p>
        </Panel>
      </div>

      <div className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <Panel
          variant="elevated"
          className="space-y-4"
        >
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="nv-stat-label">
                Ticket queue
              </p>

              <p className="mt-2 text-sm text-slate-400">
                Server-authoritative support records.
              </p>
            </div>

            <Button
              type="button"
              onClick={() => {
                void loadTickets();
              }}
              disabled={loading}
            >
              Refresh
            </Button>
          </div>

          {loading ? (
            <StatusMessage tone="info">
              Loading support queue...
            </StatusMessage>
          ) : tickets.length === 0 ? (
            <StatusMessage tone="info">
              No support tickets are currently open.
            </StatusMessage>
          ) : (
            <div className="space-y-3">
              {tickets.map(
                (ticket) => (
                  <button
                    type="button"
                    key={ticket.id}
                    onClick={() => {
                      void loadTicket(
                        ticket.id,
                      );
                    }}
                    className="w-full rounded-xl border border-white/10 bg-white/[0.03] p-4 text-left transition hover:border-violet-300/30 hover:bg-violet-300/[0.04]"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="font-bold text-white">
                          {ticket.subject}
                        </p>

                        <p className="mt-1 text-xs text-slate-500">
                          Owner {ticket.owner_user_id}
                        </p>
                      </div>

                      <StatusBadge
                        tone={statusTone(
                          ticket.status,
                        )}
                      >
                        {ticket.status}
                      </StatusBadge>
                    </div>

                    <p className="mt-3 text-xs uppercase tracking-[0.15em] text-slate-500">
                      Priority {ticket.priority}
                    </p>
                  </button>
                ),
              )}
            </div>
          )}
        </Panel>

        <Panel
          variant="elevated"
          className="space-y-5"
        >
          {!selected ? (
            <StatusMessage tone="info">
              Select a support ticket to review the authenticated conversation.
            </StatusMessage>
          ) : (
            <>
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p className="nv-stat-label">
                    Ticket workspace
                  </p>

                  <h2 className="mt-2 text-xl font-black text-white">
                    {selected.subject}
                  </h2>

                  <p className="mt-2 text-xs text-slate-500">
                    {selected.id}
                  </p>
                </div>

                <StatusBadge
                  tone={statusTone(
                    selected.status,
                  )}
                >
                  {selected.status}
                </StatusBadge>
              </div>

              <div className="grid gap-3 sm:grid-cols-2">
                <label className="space-y-2">
                  <span className="nv-stat-label">
                    Status
                  </span>

                  <select
                    value={selectedStatus}
                    onChange={(event) => {
                      setSelectedStatus(
                        event.target.value as TicketStatus,
                      );
                    }}
                    className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-slate-100"
                  >
                    <option value="OPEN">
                      Open
                    </option>

                    <option value="WAITING_FOR_USER">
                      Waiting for user
                    </option>

                    <option value="WAITING_FOR_ADMINISTRATOR">
                      Waiting for administrator
                    </option>

                    <option value="RESOLVED">
                      Resolved
                    </option>

                    <option value="CLOSED">
                      Closed
                    </option>
                  </select>
                </label>

                <label className="space-y-2">
                  <span className="nv-stat-label">
                    Priority
                  </span>

                  <select
                    value={selectedPriority}
                    onChange={(event) => {
                      setSelectedPriority(
                        event.target.value as TicketPriority,
                      );
                    }}
                    className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-slate-100"
                  >
                    <option value="LOW">
                      Low
                    </option>

                    <option value="NORMAL">
                      Normal
                    </option>

                    <option value="HIGH">
                      High
                    </option>

                    <option value="URGENT">
                      Urgent
                    </option>
                  </select>
                </label>
              </div>

              <Button
                type="button"
                onClick={() => {
                  void updateTicket();
                }}
                disabled={mutating}
              >
                Apply ticket update
              </Button>

              <div className="space-y-3">
                {(selected.messages ?? []).map(
                  (item) => (
                    <div
                      key={item.id}
                      className="rounded-xl border border-white/10 bg-slate-950/40 p-4"
                    >
                      <div className="flex items-center justify-between gap-4">
                        <p className="text-xs font-black uppercase tracking-[0.16em] text-violet-300">
                          {item.author_role}
                        </p>

                        <p className="text-xs text-slate-600">
                          {new Date(
                            item.created_at,
                          ).toLocaleString()}
                        </p>
                      </div>

                      <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-200">
                        {item.message}
                      </p>
                    </div>
                  ),
                )}
              </div>

              {selected.status ===
              "CLOSED" ? (
                <StatusMessage tone="warning">
                  Closed tickets cannot receive additional messages.
                </StatusMessage>
              ) : (
                <form
                  onSubmit={sendMessage}
                  className="space-y-3"
                >
                  <textarea
                    value={message}
                    onChange={(event) => {
                      setMessage(
                        event.target.value,
                      );
                    }}
                    rows={4}
                    placeholder="Administrator response"
                    aria-label="Administrator support response"
                    className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-slate-100"
                  />

                  <Button
                    type="submit"
                    disabled={
                      mutating ||
                      !message.trim()
                    }
                  >
                    Send administrator reply
                  </Button>
                </form>
              )}
            </>
          )}
        </Panel>
      </div>
    </div>
  );
}
