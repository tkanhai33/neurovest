export type ExecutionOperatingMode =
  | "SAFE"
  | "SIMULATION"
  | "LOCKED"
  | "EMERGENCY_STOP";

export type ExecutionControlSnapshot = {
  mode: ExecutionOperatingMode;
  revision: number;
  updated_at: string;
  reason: string;
  actor: string;
  paper_execution_enabled: boolean;
  live_execution_enabled: boolean;
  emergency_stop_active: boolean;
};

export type ExecutionControlResponse = {
  status: string;
  control: ExecutionControlSnapshot;
  detail?: string;
};

export type ExecutionControlRequestResult = {
  ok: boolean;
  statusCode: number;
  payload: ExecutionControlResponse | null;
  error: string | null;
};

export const SELECTABLE_EXECUTION_MODES:
  readonly ExecutionOperatingMode[] = [
    "SAFE",
    "SIMULATION",
    "LOCKED",
  ] as const;

function isOperatingMode(
  value: unknown
): value is ExecutionOperatingMode {
  return (
    value === "SAFE" ||
    value === "SIMULATION" ||
    value === "LOCKED" ||
    value === "EMERGENCY_STOP"
  );
}

function isSnapshot(
  value: unknown
): value is ExecutionControlSnapshot {
  if (
    !value ||
    typeof value !== "object"
  ) {
    return false;
  }

  const record =
    value as Record<string, unknown>;

  return (
    isOperatingMode(record.mode) &&
    typeof record.revision === "number" &&
    typeof record.updated_at === "string" &&
    typeof record.reason === "string" &&
    typeof record.actor === "string" &&
    typeof record.paper_execution_enabled ===
      "boolean" &&
    typeof record.live_execution_enabled ===
      "boolean" &&
    typeof record.emergency_stop_active ===
      "boolean"
  );
}

function parseControlResponse(
  value: unknown
): ExecutionControlResponse | null {
  if (
    !value ||
    typeof value !== "object"
  ) {
    return null;
  }

  const record =
    value as Record<string, unknown>;

  if (
    typeof record.status !== "string" ||
    !isSnapshot(record.control)
  ) {
    return null;
  }

  return {
    status: record.status,
    control: record.control,
    detail:
      typeof record.detail === "string"
        ? record.detail
        : undefined,
  };
}

function responseError(
  value: unknown,
  fallback: string
): string {
  if (
    value &&
    typeof value === "object"
  ) {
    const detail =
      (value as Record<string, unknown>)
        .detail;

    if (
      typeof detail === "string" &&
      detail.trim()
    ) {
      return detail;
    }
  }

  return fallback;
}

async function executeRequest(
  url: string,
  init: RequestInit
): Promise<ExecutionControlRequestResult> {
  try {
    const response = await fetch(
      url,
      {
        ...init,
        credentials: "include",
        cache: "no-store",
        headers: {
          Accept: "application/json",
          ...(init.body
            ? {
                "Content-Type":
                  "application/json",
              }
            : {}),
          ...init.headers,
        },
      }
    );

    const body: unknown =
      await response.json().catch(
        () => null
      );

    const payload =
      parseControlResponse(body);

    if (!response.ok) {
      return {
        ok: false,
        statusCode: response.status,
        payload,
        error: responseError(
          body,
          `Execution-control request failed with status ${response.status}.`
        ),
      };
    }

    if (!payload) {
      return {
        ok: false,
        statusCode: response.status,
        payload: null,
        error:
          "Execution-control response did not match the required contract.",
      };
    }

    return {
      ok: true,
      statusCode: response.status,
      payload,
      error: null,
    };
  } catch (error) {
    return {
      ok: false,
      statusCode: 0,
      payload: null,
      error:
        error instanceof Error
          ? error.message
          : "Execution-control request failed.",
    };
  }
}

export async function loadExecutionControl():
  Promise<ExecutionControlRequestResult> {
  return executeRequest(
    "/api/v1/admin/execution-control",
    {
      method: "GET",
    }
  );
}

export async function transitionExecutionControl(
  mode: Exclude<
    ExecutionOperatingMode,
    "EMERGENCY_STOP"
  >,
  reason: string
): Promise<ExecutionControlRequestResult> {
  return executeRequest(
    "/api/v1/admin/execution-control/transition",
    {
      method: "POST",
      body: JSON.stringify({
        mode,
        reason,
      }),
    }
  );
}

export async function activateExecutionEmergencyStop(
  reason: string
): Promise<ExecutionControlRequestResult> {
  return executeRequest(
    "/api/v1/admin/execution-control/emergency-stop",
    {
      method: "POST",
      body: JSON.stringify({
        reason,
      }),
    }
  );
}
