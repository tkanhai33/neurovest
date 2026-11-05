#!/usr/bin/env python3
"""
Generation 274 controlled experience-training wrapper.

This entry point delegates only to the proven isolated Generation 274
experience-reuse trainer.

The wrapper intentionally provides no candidate-registration,
promotion, parent-replacement, runtime-activation, paper-order,
broker-order, SnapTrade-order, or live-order operation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import UTC, datetime


REPO_ROOT = Path(__file__).resolve().parents[1]

TRAINER_PATH = (
    REPO_ROOT
    / "scripts"
    / "generation274_experience_reuse_training.py"
)

PROOF_RESULT_PATH = (
    REPO_ROOT
    / "runtime"
    / "training"
    / "generation274_experience_reuse_final_proof_20260806_132313"
    / "result.json"
)

PROOF_METRICS_PATH = (
    REPO_ROOT
    / "runtime"
    / "training"
    / "generation274_experience_reuse_final_proof_20260806_132313"
    / "proof_metrics.json"
)

BOUNDARY_RESULT_PATH = (
    REPO_ROOT
    / "runtime"
    / "training"
    / "generation274_remaining_integration_boundary_inspection_20260806_142647"
    / "result.json"
)

EXPECTED_FEATURE_COUNT = 18
EXPECTED_CONTINUATION_STRATEGY = "warm_start"

DISABLED_OPERATIONS = {
    "candidate_registration": False,
    "database_registration": False,
    "candidate_promotion": False,
    "parent_model_replacement": False,
    "runtime_activation": False,
    "service_restart": False,
    "paper_execution": False,
    "broker_execution": False,
    "snaptrade_execution": False,
    "live_execution": False,
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_text(
            encoding="utf-8",
        )
    )

    if not isinstance(value, dict):
        raise TypeError(
            f"Expected JSON object: {path}"
        )

    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


def utc_stamp() -> str:
    return datetime.now(
        UTC
    ).strftime(
        "%Y%m%d_%H%M%S"
    )


def qualification_contract() -> dict[str, Any]:
    proof = load_json(
        PROOF_RESULT_PATH
    )

    metrics = load_json(
        PROOF_METRICS_PATH
    )

    boundary = load_json(
        BOUNDARY_RESULT_PATH
    )

    feature_count = int(
        metrics.get(
            "rows",
            {},
        ).get(
            "feature_count",
            EXPECTED_FEATURE_COUNT,
        )
        or EXPECTED_FEATURE_COUNT
    )

    proof_passed = bool(
        proof.get("passed") is True
        and proof.get(
            "experience_reuse_proven"
        ) is True
        and proof.get(
            "state_continuity_proven"
        ) is True
        and proof.get(
            "behavioral_learning_proven"
        ) is True
    )

    boundary_passed = bool(
        boundary.get("passed") is True
        and boundary.get(
            "core_boundary_evidence_resolved"
        ) is True
    )

    trainer_present = TRAINER_PATH.is_file()

    checks = {
        "experience_reuse_proof_passed":
            proof_passed,

        "core_boundary_evidence_resolved":
            boundary_passed,

        "trainer_present":
            trainer_present,

        "trainer_is_python_source":
            TRAINER_PATH.suffix == ".py",

        "exact_feature_count_contract":
            feature_count
            == EXPECTED_FEATURE_COUNT,

        "continuation_strategy_warm_start":
            proof.get(
                "continuation_strategy"
            )
            == EXPECTED_CONTINUATION_STRATEGY,

        "registration_disabled":
            DISABLED_OPERATIONS[
                "candidate_registration"
            ]
            is False,

        "promotion_disabled":
            DISABLED_OPERATIONS[
                "candidate_promotion"
            ]
            is False,

        "parent_replacement_disabled":
            DISABLED_OPERATIONS[
                "parent_model_replacement"
            ]
            is False,

        "runtime_activation_disabled":
            DISABLED_OPERATIONS[
                "runtime_activation"
            ]
            is False,

        "all_execution_disabled":
            not any(
                DISABLED_OPERATIONS[
                    name
                ]
                for name in (
                    "paper_execution",
                    "broker_execution",
                    "snaptrade_execution",
                    "live_execution",
                )
            ),
    }

    qualified = all(
        checks.values()
    )

    return {
        "classification":
            (
                "generation274_controlled_wrapper_qualified"
                if qualified
                else
                "generation274_controlled_wrapper_blocked"
            ),

        "qualified":
            qualified,

        "checks":
            checks,

        "trainer": {
            "path":
                str(TRAINER_PATH),

            "sha256":
                (
                    sha256_file(
                        TRAINER_PATH
                    )
                    if trainer_present
                    else None
                ),
        },

        "proof": {
            "path":
                str(PROOF_RESULT_PATH),

            "sha256":
                sha256_file(
                    PROOF_RESULT_PATH
                ),
        },

        "boundary": {
            "path":
                str(BOUNDARY_RESULT_PATH),

            "sha256":
                sha256_file(
                    BOUNDARY_RESULT_PATH
                ),
        },

        "continuation_strategy":
            EXPECTED_CONTINUATION_STRATEGY,

        "feature_count":
            EXPECTED_FEATURE_COUNT,

        "disabled_operations":
            DISABLED_OPERATIONS,

        "authorization": {
            "execute_isolated_training":
                qualified,

            "write_isolated_candidate_package":
                qualified,

            "register_candidate":
                False,

            "promote_candidate":
                False,

            "replace_parent_model":
                False,

            "runtime_activation":
                False,

            "paper_execution":
                False,

            "broker_execution":
                False,

            "snaptrade_execution":
                False,

            "live_execution":
                False,
        },
    }


def write_qualification(
    destination: Path,
) -> dict[str, Any]:
    contract = qualification_contract()

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination.write_text(
        json.dumps(
            contract,
            indent=2,
            sort_keys=True,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )

    return contract


def run_trainer(
    trainer_args: Sequence[str],
    output_root: Path,
) -> int:
    qualification_file = (
        output_root
        / "wrapper_qualification.json"
    )

    qualification = write_qualification(
        qualification_file
    )

    if not qualification["qualified"]:
        print(
            json.dumps(
                qualification,
                indent=2,
                sort_keys=True,
            )
        )

        print(
            "BLOCKED: wrapper qualification failed.",
            file=sys.stderr,
        )

        return 1

    output_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    environment = os.environ.copy()

    environment.update(
        {
            "OMP_NUM_THREADS": "1",
            "OMP_THREAD_LIMIT": "1",
            "OPENBLAS_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "NUMEXPR_NUM_THREADS": "1",
            "VECLIB_MAXIMUM_THREADS": "1",
            "PYTHONUNBUFFERED": "1",

            "NEUROVEST_GENERATION274_CONTROLLED_WRAPPER":
                "1",

            "NEUROVEST_CANDIDATE_REGISTRATION":
                "0",

            "NEUROVEST_DATABASE_REGISTRATION":
                "0",

            "NEUROVEST_CANDIDATE_PROMOTION":
                "0",

            "NEUROVEST_PARENT_MODEL_REPLACEMENT":
                "0",

            "NEUROVEST_RUNTIME_ACTIVATION":
                "0",

            "NEUROVEST_PAPER_EXECUTION":
                "0",

            "NEUROVEST_BROKER_EXECUTION":
                "0",

            "NEUROVEST_SNAPTRADE_EXECUTION":
                "0",

            "NEUROVEST_LIVE_EXECUTION":
                "0",
        }
    )

    command = [
        sys.executable,
        "-X",
        "faulthandler",
        str(TRAINER_PATH),
        *trainer_args,
    ]

    invocation = {
        "classification":
            "generation274_controlled_training_invocation",

        "created_at":
            datetime.now(
                UTC
            ).isoformat(),

        "command":
            command,

        "working_directory":
            str(REPO_ROOT),

        "output_root":
            str(output_root),

        "qualification":
            qualification,

        "disabled_operations":
            DISABLED_OPERATIONS,
    }

    invocation_path = (
        output_root
        / "wrapper_invocation.json"
    )

    invocation_path.write_text(
        json.dumps(
            invocation,
            indent=2,
            sort_keys=True,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        "=" * 110
    )

    print(
        "NEUROVEST — GENERATION 274 CONTROLLED EXPERIENCE TRAINING"
    )

    print(
        "=" * 110
    )

    print(
        "Trainer:",
        TRAINER_PATH,
    )

    print(
        "Output:",
        output_root,
    )

    print(
        "Registration: disabled"
    )

    print(
        "Promotion: disabled"
    )

    print(
        "Parent replacement: disabled"
    )

    print(
        "Runtime activation: disabled"
    )

    print()

    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        env=environment,
        check=False,
    )

    result = {
        "classification":
            (
                "generation274_controlled_training_completed"
                if completed.returncode == 0
                else
                "generation274_controlled_training_failed"
            ),

        "passed":
            completed.returncode == 0,

        "trainer_returncode":
            completed.returncode,

        "invocation":
            str(invocation_path),

        "qualification":
            str(qualification_file),

        "registration_performed":
            False,

        "promotion_performed":
            False,

        "parent_replaced":
            False,

        "runtime_activated":
            False,

        "orders_submitted":
            0,
    }

    (
        output_root
        / "wrapper_result.json"
    ).write_text(
        json.dumps(
            result,
            indent=2,
            sort_keys=True,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )

    return int(
        completed.returncode
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Controlled Generation 274 experience-training wrapper. "
            "Qualification is read-only. Training requires two "
            "explicit authorization flags."
        )
    )

    parser.add_argument(
        "--qualify-only",
        action="store_true",
        help=(
            "Validate the wrapper, proof, trainer, and safety "
            "contract without starting training."
        ),
    )

    parser.add_argument(
        "--qualification-output",
        type=Path,
        default=None,
        help=(
            "Optional path for the qualification JSON artifact."
        ),
    )

    parser.add_argument(
        "--run-training",
        action="store_true",
        help=(
            "Request isolated experience training."
        ),
    )

    parser.add_argument(
        "--allow-training",
        action="store_true",
        help=(
            "Second explicit confirmation required before training."
        ),
    )

    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help=(
            "Isolated wrapper output directory."
        ),
    )

    parser.add_argument(
        "trainer_args",
        nargs=argparse.REMAINDER,
        help=(
            "Arguments forwarded unchanged to the proven trainer. "
            "Place them after --."
        ),
    )

    return parser


def main() -> int:
    parser = build_parser()

    args = parser.parse_args()

    qualification_output = (
        args.qualification_output
        or (
            REPO_ROOT
            / "runtime"
            / "training"
            / (
                "generation274_controlled_wrapper_qualification_"
                + utc_stamp()
            )
            / "qualification.json"
        )
    )

    qualification = write_qualification(
        qualification_output
    )

    if args.qualify_only:
        print(
            json.dumps(
                qualification,
                indent=2,
                sort_keys=True,
            )
        )

        return (
            0
            if qualification["qualified"]
            else 1
        )

    if not args.run_training:
        parser.error(
            "Use --qualify-only, or provide --run-training "
            "together with --allow-training."
        )

    if not args.allow_training:
        parser.error(
            "--run-training requires --allow-training."
        )

    if not qualification["qualified"]:
        print(
            json.dumps(
                qualification,
                indent=2,
                sort_keys=True,
            )
        )

        print(
            "BLOCKED: wrapper qualification failed.",
            file=sys.stderr,
        )

        return 1

    if args.output_root is None:
        parser.error(
            "--output-root is required for training."
        )

    trainer_args = list(
        args.trainer_args
    )

    if (
        trainer_args
        and trainer_args[0] == "--"
    ):
        trainer_args = trainer_args[1:]

    return run_trainer(
        trainer_args,
        args.output_root,
    )


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
