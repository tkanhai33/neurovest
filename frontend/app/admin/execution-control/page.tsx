"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import PageHeader from "../../../components/app-shell/PageHeader";

import {
  Panel,
  StatusBadge,
  StatusMessage,
} from "../../../components/ui";

import {
  SELECTABLE_EXECUTION_MODES,
  activateExecutionEmergencyStop,
  loadExecutionControl,
  transitionExecutionControl,
  type ExecutionControlSnapshot,
  type ExecutionOperatingMode,
} from "../../../services/executionControlService";


type SelectableMode = Exclude<
  ExecutionOperatingMode,
  "EMERGENCY_STOP"
>;


const MODE_DESCRIPTIONS: Record<
  ExecutionOperatingMode,
  string
> = {
  SAFE:
    "Read-only operation. Paper and live execution are blocked.",

  SIMULATION:
    "Controlled paper execution is permitted. Live broker execution remains blocked.",

  LOCKED:
    "Administrative lockout. All execution remains blocked.",

  EMERGENCY_STOP:
    "Immediate persistent execution denial. Recovery must pass through LOCKED.",
};


const MODE_TONES: Record<
  ExecutionOperatingMode,
  "success" | "info" | "warning" | "danger"
> = {
  SAFE: "success",
  SIMULATION: "info",
  LOCKED: "warning",
  EMERGENCY_STOP: "danger",
};


const TRANSITION_REASONS: Record<
  SelectableMode,
  string
> = {
  SAFE:
    "Administrative transition to SAFE read-only operation",

  SIMULATION:
    "Administrative authorization for controlled paper simulation",

  LOCKED:
    "Administrative execution lock activated",
};


function formatTimestamp(
  value: string
): string {
  const timestamp = new Date(
    value
  );

  if (
    Number.isNaN(
      timestamp.getTime()
    )
  ) {
    return value || "Unavailable";
  }

  return timestamp.toLocaleString();
}


function modeButtonLabel(
  mode: SelectableMode
): string {
  if (mode === "SAFE") {
    return "Enter SAFE";
  }

  if (mode === "SIMULATION") {
    return "Enable simulation";
  }

  return "Lock execution";
}


export default function ExecutionControlPage() {
  const [
    control,
    setControl,
  ] = useState<ExecutionControlSnapshot | null>(
    null
  );

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    working,
    setWorking,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState<string | null>(
    null
  );

  const [
    notice,
    setNotice,
  ] = useState<string | null>(
    null
  );

  const [
    selectedMode,
    setSelectedMode,
  ] = useState<SelectableMode>(
    "SAFE"
  );

  const [
    transitionReason,
    setTransitionReason,
  ] = useState(
    TRANSITION_REASONS.SAFE
  );

  const [
    emergencyReason,
    setEmergencyReason,
  ] = useState(
    "Administrative emergency stop activated"
  );

  const [
    emergencyConfirmation,
    setEmergencyConfirmation,
  ] = useState("");


  const refreshControl = useCallback(
    async () => {
      setLoading(true);
      setError(null);

      const result =
        await loadExecutionControl();

      if (
        !result.ok ||
        !result.payload
      ) {
        setError(
          result.error ||
            "Unable to load execution-control status."
        );

        setLoading(false);
        return;
      }

      setControl(
        result.payload.control
      );

      const returnedMode =
        result.payload.control.mode;

      if (
        returnedMode !==
        "EMERGENCY_STOP"
      ) {
        setSelectedMode(
          returnedMode
        );

        setTransitionReason(
          TRANSITION_REASONS[
            returnedMode
          ]
        );
      }

      setLoading(false);
    },
    []
  );


  useEffect(() => {
    queueMicrotask(() => { void refreshControl(); });
  }, [refreshControl]);


  const selectableModes =
    useMemo(
      () =>
        SELECTABLE_EXECUTION_MODES.filter(
          (
            mode
          ): mode is SelectableMode =>
            mode !==
            "EMERGENCY_STOP"
        ),
      []
    );


  const emergencyConfirmed =
    emergencyConfirmation.trim().toUpperCase() ===
    "EMERGENCY STOP";


  const transitionAllowed =
    Boolean(control) &&
    !loading &&
    !working &&
    selectedMode !==
      control?.mode &&
    transitionReason.trim().length >=
      3;


  async function applyTransition() {
    if (!transitionAllowed) {
      return;
    }

    setWorking(true);
    setError(null);
    setNotice(null);

    const result =
      await transitionExecutionControl(
        selectedMode,
        transitionReason.trim()
      );

    if (
      !result.ok ||
      !result.payload
    ) {
      setError(
        result.error ||
          "The operating-mode transition was rejected."
      );

      setWorking(false);
      return;
    }

    setControl(
      result.payload.control
    );

    setNotice(
      `Execution mode transitioned to ${result.payload.control.mode}.`
    );

    setWorking(false);
  }


  async function activateEmergencyStop() {
    if (
      !emergencyConfirmed ||
      emergencyReason.trim().length <
        3 ||
      working
    ) {
      return;
    }

    setWorking(true);
    setError(null);
    setNotice(null);

    const result =
      await activateExecutionEmergencyStop(
        emergencyReason.trim()
      );

    if (
      !result.ok ||
      !result.payload
    ) {
      setError(
        result.error ||
          "The emergency stop could not be activated."
      );

      setWorking(false);
      return;
    }

    setControl(
      result.payload.control
    );

    setEmergencyConfirmation(
      ""
    );

    setNotice(
      "Persistent emergency stop activated. All execution is blocked."
    );

    setWorking(false);
  }


  return (
    <main
      className="space-y-6"
      data-testid="execution-control-page"
    >
      <PageHeader
        eyebrow="NeuroVest Administration"
        title="Execution control."
        description="Inspect and control the server-authoritative operating mode. Live broker execution remains unavailable in every mode."
        badge={
          control ? (
            <StatusBadge
              tone={
                MODE_TONES[
                  control.mode
                ]
              }
            >
              {control.mode}
            </StatusBadge>
          ) : (
            <StatusBadge tone="info">
              Loading
            </StatusBadge>
          )
        }
        actions={
          <button
            type="button"
            className="nv-button nv-button-secondary"
            disabled={
              loading ||
              working
            }
            onClick={() => {
              void refreshControl();
            }}
          >
            {loading
              ? "Loading…"
              : "Refresh status"}
          </button>
        }
      />


      {error ? (
        <StatusMessage tone="danger">
          {error}
        </StatusMessage>
      ) : null}


      {notice ? (
        <StatusMessage tone="success">
          {notice}
        </StatusMessage>
      ) : null}


      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Panel
          variant="elevated"
          className="p-5"
        >
          <p className="nv-stat-label">
            Current mode
          </p>

          <p
            data-testid="execution-control-current-mode"
            className="mt-3 text-2xl font-black text-white"
          >
            {control?.mode ||
              "Unavailable"}
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            {control
              ? MODE_DESCRIPTIONS[
                  control.mode
                ]
              : "Waiting for the server-authoritative control state."}
          </p>
        </Panel>


        <Panel
          variant="elevated"
          className="p-5"
        >
          <p className="nv-stat-label">
            Paper execution
          </p>

          <p className="mt-3 text-2xl font-black text-white">
            {control?.paper_execution_enabled
              ? "Enabled"
              : "Blocked"}
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            Paper execution is available only while the system is in SIMULATION.
          </p>
        </Panel>


        <Panel
          variant="elevated"
          className="p-5"
        >
          <p className="nv-stat-label">
            Live execution
          </p>

          <p className="mt-3 text-2xl font-black text-white">
            Blocked
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            Live broker execution is not enabled by this control system.
          </p>
        </Panel>


        <Panel
          variant="elevated"
          className="p-5"
        >
          <p className="nv-stat-label">
            Revision
          </p>

          <p className="mt-3 text-2xl font-black text-white">
            {control?.revision ??
              "—"}
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            {control
              ? `Updated ${formatTimestamp(
                  control.updated_at
                )}`
              : "No state has been loaded."}
          </p>
        </Panel>
      </section>


      <section className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <Panel
          variant="default"
          className="p-6"
        >
          <div>
            <p className="nv-eyebrow">
              Validated transition
            </p>

            <h2 className="mt-3 text-2xl font-black text-white">
              Change operating mode
            </h2>

            <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-400">
              Every transition is validated by the backend state machine and
              persisted before the new mode becomes active.
            </p>
          </div>


          <div className="mt-6 space-y-5">
            <div>
              <label
                htmlFor="execution-mode"
                className="text-sm font-bold text-slate-200"
              >
                Target mode
              </label>

              <select
                id="execution-mode"
                data-testid="execution-control-mode-select"
                className="nv-input mt-2 w-full"
                value={selectedMode}
                disabled={
                  loading ||
                  working
                }
                onChange={event => {
                  const mode =
                    event.target
                      .value as SelectableMode;

                  setSelectedMode(
                    mode
                  );

                  setTransitionReason(
                    TRANSITION_REASONS[
                      mode
                    ]
                  );
                }}
              >
                {selectableModes.map(
                  mode => (
                    <option
                      key={mode}
                      value={mode}
                    >
                      {mode}
                    </option>
                  )
                )}
              </select>

              <p className="mt-2 text-xs leading-5 text-slate-500">
                EMERGENCY_STOP cannot be selected here. It uses the dedicated
                emergency control below.
              </p>
            </div>


            <div>
              <label
                htmlFor="transition-reason"
                className="text-sm font-bold text-slate-200"
              >
                Administrative reason
              </label>

              <textarea
                id="transition-reason"
                data-testid="execution-control-transition-reason"
                className="nv-input mt-2 min-h-28 w-full resize-y"
                value={transitionReason}
                maxLength={500}
                disabled={
                  loading ||
                  working
                }
                onChange={event => {
                  setTransitionReason(
                    event.target.value
                  );
                }}
              />
            </div>


            <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-4">
              <p className="text-sm font-bold text-white">
                Selected behavior
              </p>

              <p className="mt-2 text-sm leading-6 text-slate-400">
                {MODE_DESCRIPTIONS[
                  selectedMode
                ]}
              </p>
            </div>


            <button
              type="button"
              data-testid="execution-control-transition-button"
              className="nv-button nv-button-primary"
              disabled={
                !transitionAllowed
              }
              onClick={() => {
                void applyTransition();
              }}
            >
              {working
                ? "Applying…"
                : modeButtonLabel(
                    selectedMode
                  )}
            </button>
          </div>
        </Panel>


        <Panel
          variant="elevated"
          className="border-red-500/25 p-6"
        >
          <div>
            <p className="text-xs font-black uppercase tracking-[0.18em] text-red-300">
              Emergency authority
            </p>

            <h2 className="mt-3 text-2xl font-black text-white">
              Emergency stop
            </h2>

            <p className="mt-3 text-sm leading-7 text-slate-400">
              Immediately persists EMERGENCY_STOP and blocks every execution
              path. Recovery must transition through LOCKED.
            </p>
          </div>


          <div className="mt-6 space-y-5">
            <div>
              <label
                htmlFor="emergency-reason"
                className="text-sm font-bold text-slate-200"
              >
                Emergency reason
              </label>

              <textarea
                id="emergency-reason"
                data-testid="execution-control-emergency-reason"
                className="nv-input mt-2 min-h-28 w-full resize-y"
                value={emergencyReason}
                maxLength={500}
                disabled={working}
                onChange={event => {
                  setEmergencyReason(
                    event.target.value
                  );
                }}
              />
            </div>


            <div>
              <label
                htmlFor="emergency-confirmation"
                className="text-sm font-bold text-slate-200"
              >
                Type EMERGENCY STOP to confirm
              </label>

              <input
                id="emergency-confirmation"
                data-testid="execution-control-emergency-confirmation"
                className="nv-input mt-2 w-full"
                value={emergencyConfirmation}
                autoComplete="off"
                disabled={working}
                onChange={event => {
                  setEmergencyConfirmation(
                    event.target.value
                  );
                }}
              />
            </div>


            <button
              type="button"
              data-testid="execution-control-emergency-button"
              className="nv-button w-full border border-red-400/30 bg-red-500/15 text-red-100 hover:bg-red-500/25"
              disabled={
                !emergencyConfirmed ||
                emergencyReason.trim()
                  .length < 3 ||
                working
              }
              onClick={() => {
                void activateEmergencyStop();
              }}
            >
              {working
                ? "Activating…"
                : "Activate emergency stop"}
            </button>
          </div>
        </Panel>
      </section>


      <Panel
        variant="default"
        className="p-6"
      >
        <p className="nv-eyebrow">
          Server-authoritative evidence
        </p>

        <h2 className="mt-3 text-2xl font-black text-white">
          Current control record
        </h2>

        {loading ? (
          <div className="mt-5">
            <StatusMessage tone="info">
              Loading execution-control state…
            </StatusMessage>
          </div>
        ) : control ? (
          <dl
            data-testid="execution-control-record"
            className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3"
          >
            <div className="rounded-xl border border-white/[0.06] bg-black/20 p-4">
              <dt className="nv-stat-label">
                Mode
              </dt>

              <dd className="mt-2 font-bold text-white">
                {control.mode}
              </dd>
            </div>

            <div className="rounded-xl border border-white/[0.06] bg-black/20 p-4">
              <dt className="nv-stat-label">
                Actor
              </dt>

              <dd className="mt-2 break-all font-bold text-white">
                {control.actor}
              </dd>
            </div>

            <div className="rounded-xl border border-white/[0.06] bg-black/20 p-4">
              <dt className="nv-stat-label">
                Reason
              </dt>

              <dd className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-200">
                {control.reason}
              </dd>
            </div>

            <div className="rounded-xl border border-white/[0.06] bg-black/20 p-4">
              <dt className="nv-stat-label">
                Updated
              </dt>

              <dd className="mt-2 text-sm text-slate-200">
                {formatTimestamp(
                  control.updated_at
                )}
              </dd>
            </div>

            <div className="rounded-xl border border-white/[0.06] bg-black/20 p-4">
              <dt className="nv-stat-label">
                Paper execution
              </dt>

              <dd className="mt-2 font-bold text-white">
                {control.paper_execution_enabled
                  ? "Enabled"
                  : "Blocked"}
              </dd>
            </div>

            <div className="rounded-xl border border-white/[0.06] bg-black/20 p-4">
              <dt className="nv-stat-label">
                Emergency stop
              </dt>

              <dd className="mt-2 font-bold text-white">
                {control.emergency_stop_active
                  ? "Active"
                  : "Inactive"}
              </dd>
            </div>
          </dl>
        ) : (
          <div className="mt-5">
            <StatusMessage tone="danger">
              No qualified execution-control record is available.
            </StatusMessage>
          </div>
        )}
      </Panel>
    </main>
  );
}
