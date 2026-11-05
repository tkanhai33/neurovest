"use client";

import { useState } from "react";

type StrategyAdaptiveTrainingActionProps = {
  strategyName: string;
};

type AdaptiveTrainingResponse = {
  controller_id?: string | number | null;
  detail?: unknown;
};

export default function StrategyAdaptiveTrainingAction({
  strategyName,
}: StrategyAdaptiveTrainingActionProps) {
  const [submitting, setSubmitting] = useState(false);

  const handleAdaptiveTraining = async () => {
    const normalizedStrategyName = strategyName.trim();

    if (!normalizedStrategyName || submitting) {
      return;
    }

    const confirmed = window.confirm(
      `Start adaptive training for ${normalizedStrategyName}?`,
    );

    if (!confirmed) {
      return;
    }

    setSubmitting(true);

    try {
      const response = await fetch(
        "/api/v1/training/adaptive",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            strategy_name: normalizedStrategyName,
          }),
        },
      );

      const payload =
        (await response
          .json()
          .catch(() => null)) as AdaptiveTrainingResponse | null;

      if (!response.ok) {
        const detail =
          payload?.detail !== undefined
            ? String(payload.detail)
            : `HTTP ${response.status}`;

        window.alert(
          `Adaptive training could not start: ${detail}`,
        );

        return;
      }

      const controllerId =
        payload?.controller_id !== undefined &&
        payload.controller_id !== null
          ? String(payload.controller_id)
          : "queued";

      window.alert(
        `Adaptive training started for ${normalizedStrategyName}. Controller: ${controllerId}`,
      );
    } catch (error) {
      const detail =
        error instanceof Error
          ? error.message
          : "Unknown request error";

      window.alert(
        `Adaptive training request failed: ${detail}`,
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <button
      type="button"
      className="nv-user-strategy-adaptive-action"
      disabled={submitting}
      onClick={handleAdaptiveTraining}
    >
      {submitting
        ? "Starting…"
        : "Adaptive train"}
    </button>
  );
}
