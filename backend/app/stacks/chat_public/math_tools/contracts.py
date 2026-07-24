"""
Contracts for NeuroVest deterministic calculations.

All calculation inputs are explicit and bounded.
No expression evaluation, code execution, network access,
database mutation, broker access, or live trading is permitted.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass(
    frozen=True,
    slots=True,
)
class MathToolRequest:
    operation: str
    arguments: dict[str, Any]


@dataclass(
    frozen=True,
    slots=True,
)
class MathToolResult:
    operation: str
    status: str
    values: dict[str, Decimal | int | str | bool | None]
    formula: str
    precision: int
    error: str | None = None

    @property
    def succeeded(
        self,
    ) -> bool:
        return (
            self.status
            == "success"
            and self.error is None
        )

    def as_serializable(
        self,
    ) -> dict[str, Any]:
        serialized: dict[str, Any] = {}

        for key, value in self.values.items():
            if isinstance(
                value,
                Decimal,
            ):
                serialized[key] = format(
                    value,
                    "f",
                )
            else:
                serialized[key] = value

        return {
            "operation":
                self.operation,
            "status":
                self.status,
            "values":
                serialized,
            "formula":
                self.formula,
            "precision":
                self.precision,
            "error":
                self.error,
            "deterministic":
                True,
            "read_only":
                True,
        }


__all__ = [
    "MathToolRequest",
    "MathToolResult",
]
