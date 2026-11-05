"use client";

import {
  FormEvent,
  useCallback,
  useEffect,
  useState,
} from "react";

import PageHeader from "../../../components/app-shell/PageHeader";

import {
  Button,
  Input,
  Panel,
  StatusBadge,
  StatusMessage,
} from "../../../components/ui";

import {
  csrfHeaders,
} from "../../../lib/clientCsrf";


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
  status:
    | "OPEN"
    | "WAITING_FOR_USER"
    | "WAITING_FOR_ADMINISTRATOR"
    | "RESOLVED"
    | "CLOSED";
  priority:
    | "LOW"
    | "NORMAL"
    | "HIGH"
    | "URGENT";
  created_at: string;
  updated_at: string;
  resolved_at?: string | null;
  closed_at?: string | null;
  messages?: SupportMessage[];
};


function statusTone(
  status: SupportTicket["status"],
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


async function parseJson<T>(
  response: Response,
): Promise<T> {
  const body = await response.json();

  if (!response.ok) {
    const detail =
      typeof body?.detail === "string"
        ? body.detail
        : "Support request failed.";

    throw new Error(detail);
  }

  return body as T;
}


export default function UserSupportPage() {
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
    subject,
    setSubject,
  ] = useState("");

  const [
    priority,
    setPriority,
  ] = useState<
    SupportTicket["priority"]
  >("NORMAL");

  const [
    initialMessage,
    setInitialMessage,
  ] = useState("");

  const [
    reply,
    setReply,
  ] = useState("");

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
          "/api/v1/support/tickets",
          {
            cache: "no-store",
          },
        );

        if (
          response.status === 401
        ) {
          window.location.assign(
            "/login?next=/user/support",
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
            : "Unable to load support tickets.",
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
          `/api/v1/support/tickets/${encodeURIComponent(
            ticketId,
          )}`,
          {
            cache: "no-store",
          },
        );

        if (
          response.status === 401
        ) {
          window.location.assign(
            "/login?next=/user/support",
          );
          return;
        }

        const payload =
          await parseJson<
            SupportTicket
          >(response);

        setSelected(payload);
      } catch (caught) {
        setError(
          caught instanceof Error
            ? caught.message
            : "Unable to load the support ticket.",
        );
      }
    },
    [],
  );


  useEffect(() => {
    queueMicrotask(() => { void loadTickets(); });
  }, [loadTickets]);


  async function createTicket(
    event: FormEvent,
  ) {
    event.preventDefault();

    if (
      !subject.trim() ||
      !initialMessage.trim()
    ) {
      setError(
        "Subject and message are required.",
      );
      return;
    }

    setMutating(true);
    setError(null);

    try {
      const response = await fetch(
        "/api/v1/support/tickets",
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
            ...csrfHeaders(),
          },
          body: JSON.stringify({
            subject:
              subject.trim(),
            message:
              initialMessage.trim(),
            priority,
          }),
        },
      );

      const created =
        await parseJson<
          SupportTicket
        >(response);

      setSubject("");
      setInitialMessage("");
      setPriority("NORMAL");

      await loadTickets();

      await loadTicket(
        created.id,
      );
    } catch (caught) {
      setError(
        caught instanceof Error
          ? caught.message
          : "Unable to create support ticket.",
      );
    } finally {
      setMutating(false);
    }
  }


  async function sendReply(
    event: FormEvent,
  ) {
    event.preventDefault();

    if (
      !selected ||
      !reply.trim()
    ) {
      return;
    }

    setMutating(true);
    setError(null);

    try {
      const response = await fetch(
        `/api/v1/support/tickets/${encodeURIComponent(
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
              reply.trim(),
          }),
        },
      );

      const updated =
        await parseJson<
          SupportTicket
        >(response);

      setReply("");
      setSelected(updated);

      await loadTickets();
    } catch (caught) {
      setError(
        caught instanceof Error
          ? caught.message
          : "Unable to send support message.",
      );
    } finally {
      setMutating(false);
    }
  }


  return (
    <div
      className="space-y-6"
      data-testid="user-support-page"
    >
      <PageHeader
        eyebrow="NeuroVest Support"
        title="Support tickets."
        description="Create a support request, review your own ticket history, and continue conversations with NeuroVest support."
        badge={
          <StatusBadge tone="info">
            Owner scoped
          </StatusBadge>
        }
      />

      {error ? (
        <StatusMessage tone="danger">
          {error}
        </StatusMessage>
      ) : null}

      <Panel
        variant="elevated"
        className="space-y-5"
      >
        <div>
          <p className="nv-stat-label">
            New support request
          </p>

          <h2 className="mt-2 text-xl font-black text-white">
            Contact support
          </h2>
        </div>

        <form
          onSubmit={createTicket}
          className="space-y-4"
        >
          <Input
            value={subject}
            onChange={(event) => {
              setSubject(
                event.target.value,
              );
            }}
            placeholder="Subject"
            aria-label="Support subject"
          />

          <select
            value={priority}
            onChange={(event) => {
              setPriority(
                event.target.value as SupportTicket["priority"],
              );
            }}
            className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-slate-100 outline-none"
            aria-label="Support priority"
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

          <textarea
            value={initialMessage}
            onChange={(event) => {
              setInitialMessage(
                event.target.value,
              );
            }}
            placeholder="Describe the issue"
            aria-label="Support message"
            rows={5}
            className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-slate-100 outline-none"
          />

          <Button
            type="submit"
            disabled={mutating}
          >
            {mutating
              ? "Submitting..."
              : "Create ticket"}
          </Button>
        </form>
      </Panel>

      <div className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <Panel
          variant="elevated"
          className="space-y-4"
        >
          <div>
            <p className="nv-stat-label">
              Your tickets
            </p>

            <p className="mt-2 text-sm text-slate-400">
              Only tickets owned by your authenticated identity are shown.
            </p>
          </div>

          {loading ? (
            <StatusMessage tone="info">
              Loading support tickets...
            </StatusMessage>
          ) : tickets.length === 0 ? (
            <StatusMessage tone="info">
              You do not have any support tickets yet.
            </StatusMessage>
          ) : (
            <div className="space-y-3">
              {tickets.map(
                (ticket) => (
                  <button
                    key={ticket.id}
                    type="button"
                    onClick={() => {
                      void loadTicket(
                        ticket.id,
                      );
                    }}
                    className="w-full rounded-xl border border-white/10 bg-white/[0.03] p-4 text-left transition hover:border-cyan-300/30 hover:bg-cyan-300/[0.04]"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="font-bold text-white">
                          {ticket.subject}
                        </p>

                        <p className="mt-1 text-xs text-slate-500">
                          {ticket.id}
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
              Select a support ticket to review its conversation.
            </StatusMessage>
          ) : (
            <>
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p className="nv-stat-label">
                    Ticket detail
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

              <div className="space-y-3">
                {(selected.messages ?? []).map(
                  (message) => (
                    <div
                      key={message.id}
                      className="rounded-xl border border-white/10 bg-slate-950/40 p-4"
                    >
                      <div className="flex items-center justify-between gap-4">
                        <p className="text-xs font-black uppercase tracking-[0.16em] text-cyan-300">
                          {message.author_role}
                        </p>

                        <p className="text-xs text-slate-600">
                          {new Date(
                            message.created_at,
                          ).toLocaleString()}
                        </p>
                      </div>

                      <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-200">
                        {message.message}
                      </p>
                    </div>
                  ),
                )}
              </div>

              {selected.status ===
              "CLOSED" ? (
                <StatusMessage tone="warning">
                  This ticket is closed and cannot receive additional messages.
                </StatusMessage>
              ) : (
                <form
                  onSubmit={sendReply}
                  className="space-y-3"
                >
                  <textarea
                    value={reply}
                    onChange={(event) => {
                      setReply(
                        event.target.value,
                      );
                    }}
                    rows={4}
                    placeholder="Add a reply"
                    aria-label="Support reply"
                    className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-slate-100 outline-none"
                  />

                  <Button
                    type="submit"
                    disabled={
                      mutating ||
                      !reply.trim()
                    }
                  >
                    Send reply
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
