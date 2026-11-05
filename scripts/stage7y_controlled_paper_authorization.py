#!/usr/bin/env python3

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import argparse
import csv
import hashlib
import json
import sys


PAPER_MODE = "CONTROLLED_DRY_RUN"
MAXIMUM_GROSS_EXPOSURE = 0.25
MAXIMUM_SYMBOL_EXPOSURE = 0.02
EXPECTED_ACCOUNT_VALUE = 100000.0
MAXIMUM_AUTHORIZED_GROSS_VALUE = (
    EXPECTED_ACCOUNT_VALUE
    * MAXIMUM_GROSS_EXPOSURE
)


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def deterministic_id(*parts: str) -> str:
    payload = "|".join(parts)

    return hashlib.sha256(
        payload.encode("utf-8")
    ).hexdigest()


def discover_paper_boundaries(
    repository: Path,
) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []

    roots = [
        repository / "backend",
        repository / "scripts",
    ]

    excluded = {
        ".git",
        ".venv",
        "__pycache__",
        "node_modules",
        ".next",
        "runtime",
    }

    keywords = (
        "paper_trading",
        "paper trading",
        "paper order",
        "paper_order",
        "order intent",
        "order_intent",
        "execution boundary",
        "execution_boundary",
        "broker execution",
        "broker_execution",
    )

    for root in roots:
        if not root.exists():
            continue

        for path in root.rglob("*"):
            if not path.is_file():
                continue

            if any(
                part in excluded
                for part in path.parts
            ):
                continue

            if path.suffix.lower() not in {
                ".py",
                ".md",
                ".txt",
                ".json",
                ".yaml",
                ".yml",
            }:
                continue

            try:
                text = path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
            except Exception:
                continue

            lowered = text.lower()

            found = sorted(
                {
                    keyword
                    for keyword in keywords
                    if keyword in lowered
                }
            )

            if found:
                matches.append(
                    {
                        "path":
                            str(
                                path.relative_to(
                                    repository
                                )
                            ),

                        "keywords":
                            found,

                        "sha256":
                            sha256_file(path),
                    }
                )

    return sorted(
        matches,
        key=lambda item: item["path"],
    )


def main() -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--repository",
        required=True,
    )

    parser.add_argument(
        "--stage7x-result",
        required=True,
    )

    parser.add_argument(
        "--stage7x-intents",
        required=True,
    )

    parser.add_argument(
        "--stage7x-package",
        required=True,
    )

    parser.add_argument(
        "--output",
        required=True,
    )

    args = parser.parse_args()

    repository = Path(
        args.repository
    ).resolve()

    root = Path(
        args.output
    )

    result_path = (
        root / "result.json"
    )

    authorized_path = (
        root
        / "authorized_paper_intents.csv"
    )

    ledger_path = (
        root
        / "dry_run_paper_ledger.jsonl"
    )

    reconciliation_path = (
        root
        / "reconciliation.json"
    )

    package_path = (
        root
        / "paper_only_authorization_package.json"
    )

    inventory_path = (
        root
        / "paper_boundary_inventory.json"
    )

    report_path = (
        root
        / "report.txt"
    )

    stage7x_result_path = Path(
        args.stage7x_result
    )

    stage7x_intents_path = Path(
        args.stage7x_intents
    )

    stage7x_package_path = Path(
        args.stage7x_package
    )

    stage7x = json.loads(
        stage7x_result_path.read_text(
            encoding="utf-8",
        )
    )

    stage7x_package = json.loads(
        stage7x_package_path.read_text(
            encoding="utf-8",
        )
    )

    source_intents: list[
        dict[str, Any]
    ] = []

    with stage7x_intents_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle)

        for row in reader:
            source_intents.append(
                dict(row)
            )

    boundary_matches = (
        discover_paper_boundaries(
            repository
        )
    )

    inventory = {
        "generated_at":
            utc_now(),

        "repository":
            str(repository),

        "match_count":
            len(boundary_matches),

        "matches":
            boundary_matches,

        "source_files_modified":
            False,

        "runtime_boundary_invoked":
            False,

        "broker_boundary_invoked":
            False,
    }

    inventory_path.write_text(
        json.dumps(
            inventory,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    continuity_checks = {
        "stage7x_passed":
            stage7x.get("passed")
            is True,

        "stage7x_classification_qualified":
            stage7x.get(
                "classification"
            )
            == (
                "stage7x_frozen_"
                "reproducibility_and_"
                "paper_readiness_qualified"
            ),

        "stage7x_paper_readiness_qualified":
            stage7x.get(
                "authorization",
                {},
            ).get(
                "paper_readiness_qualified"
            )
            is True,

        "stage7x_paper_execution_was_disabled":
            stage7x.get(
                "authorization",
                {},
            ).get(
                "paper_execution_authorized"
            )
            is False,

        "stage7x_broker_execution_disabled":
            stage7x.get(
                "authorization",
                {},
            ).get(
                "broker_execution"
            )
            is False,

        "stage7x_live_execution_disabled":
            stage7x.get(
                "authorization",
                {},
            ).get(
                "live_execution"
            )
            is False,

        "candidate_id_matches_package":
            str(
                stage7x.get(
                    "summary",
                    {},
                ).get(
                    "candidate_id"
                )
            )
            == str(
                stage7x_package.get(
                    "candidate_id"
                )
            ),

        "intent_count_matches_package":
            len(source_intents)
            == int(
                stage7x_package.get(
                    "paper_intent_count",
                    -1,
                )
            ),
    }

    if not all(
        bool(value)
        for value
        in continuity_checks.values()
    ):
        raise SystemExit(
            "BLOCKED: Stage 7X continuity "
            "qualification failed."
        )

    candidate_id = str(
        stage7x_package[
            "candidate_id"
        ]
    )

    source_gross_value = sum(
        abs(
            float(
                row[
                    "target_order_value"
                ]
            )
        )
        for row in source_intents
    )

    duplicate_source_ids = (
        len(
            {
                row["intent_id"]
                for row in source_intents
            }
        )
        != len(source_intents)
    )

    source_checks = {
        "source_intents_present":
            len(source_intents) > 0,

        "no_duplicate_source_intent_ids":
            not duplicate_source_ids,

        "all_candidate_ids_match":
            all(
                row.get(
                    "candidate_id"
                )
                == candidate_id
                for row in source_intents
            ),

        "all_source_intents_unsubmitted":
            all(
                str(
                    row.get(
                        "submitted",
                        "",
                    )
                ).lower()
                == "false"
                for row in source_intents
            ),

        "all_source_broker_flags_false":
            all(
                str(
                    row.get(
                        "broker_request_created",
                        "",
                    )
                ).lower()
                == "false"
                for row in source_intents
            ),

        "all_source_live_flags_false":
            all(
                str(
                    row.get(
                        "live_order_created",
                        "",
                    )
                ).lower()
                == "false"
                for row in source_intents
            ),

        "gross_value_within_cap":
            source_gross_value
            <= (
                MAXIMUM_AUTHORIZED_GROSS_VALUE
                + 1e-8
            ),

        "each_symbol_within_cap":
            all(
                float(
                    row[
                        "target_order_value"
                    ]
                )
                <= (
                    EXPECTED_ACCOUNT_VALUE
                    * MAXIMUM_SYMBOL_EXPOSURE
                    + 1e-8
                )
                for row in source_intents
            ),
    }

    if not all(
        bool(value)
        for value in source_checks.values()
    ):
        raise SystemExit(
            "BLOCKED: Stage 7X paper-intent "
            "boundary validation failed."
        )

    authorized_intents = []

    for source in source_intents:
        authorization_id = (
            "stage7y_authorization_"
            + deterministic_id(
                source["intent_id"],
                candidate_id,
                PAPER_MODE,
            )[:20]
        )

        authorized_intents.append(
            {
                "authorization_id":
                    authorization_id,

                "intent_id":
                    source[
                        "intent_id"
                    ],

                "candidate_id":
                    candidate_id,

                "timestamp":
                    source[
                        "timestamp"
                    ],

                "symbol":
                    source["symbol"],

                "side":
                    source["side"],

                "probability":
                    float(
                        source[
                            "probability"
                        ]
                    ),

                "threshold":
                    float(
                        source[
                            "threshold"
                        ]
                    ),

                "target_order_value":
                    float(
                        source[
                            "target_order_value"
                        ]
                    ),

                "authorization_scope":
                    "isolated_paper_dry_run",

                "paper_authorized":
                    True,

                "dry_run_only":
                    True,

                "runtime_submission_authorized":
                    False,

                "broker_submission_authorized":
                    False,

                "live_submission_authorized":
                    False,

                "submitted":
                    False,

                "broker_request_created":
                    False,

                "live_order_created":
                    False,
            }
        )

    fields = [
        "authorization_id",
        "intent_id",
        "candidate_id",
        "timestamp",
        "symbol",
        "side",
        "probability",
        "threshold",
        "target_order_value",
        "authorization_scope",
        "paper_authorized",
        "dry_run_only",
        "runtime_submission_authorized",
        "broker_submission_authorized",
        "live_submission_authorized",
        "submitted",
        "broker_request_created",
        "live_order_created",
    ]

    with authorized_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
        )

        writer.writeheader()
        writer.writerows(
            authorized_intents
        )

    ledger_records = []

    for intent in authorized_intents:
        ledger_id = (
            "stage7y_ledger_"
            + deterministic_id(
                intent[
                    "authorization_id"
                ],
                intent["intent_id"],
                "accepted",
            )[:20]
        )

        ledger_records.append(
            {
                "ledger_id":
                    ledger_id,

                "recorded_at":
                    utc_now(),

                "authorization_id":
                    intent[
                        "authorization_id"
                    ],

                "intent_id":
                    intent[
                        "intent_id"
                    ],

                "candidate_id":
                    candidate_id,

                "symbol":
                    intent["symbol"],

                "side":
                    intent["side"],

                "target_order_value":
                    intent[
                        "target_order_value"
                    ],

                "mode":
                    PAPER_MODE,

                "status":
                    "DRY_RUN_ACCEPTED",

                "simulated_fill_status":
                    "NOT_FILLED",

                "persisted_to_application_database":
                    False,

                "submitted_to_runtime":
                    False,

                "submitted_to_broker":
                    False,

                "submitted_live":
                    False,
            }
        )

    with ledger_path.open(
        "w",
        encoding="utf-8",
    ) as handle:
        for record in ledger_records:
            handle.write(
                json.dumps(
                    record,
                    sort_keys=True,
                )
                + "\n"
            )

    ledger_loaded = []

    with ledger_path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        for line in handle:
            line = line.strip()

            if line:
                ledger_loaded.append(
                    json.loads(line)
                )

    authorized_ids = {
        record["intent_id"]
        for record
        in authorized_intents
    }

    ledger_ids = {
        record["intent_id"]
        for record
        in ledger_loaded
    }

    reconciliation_checks = {
        "authorized_count_matches_source":
            len(authorized_intents)
            == len(source_intents),

        "ledger_count_matches_authorized":
            len(ledger_loaded)
            == len(authorized_intents),

        "intent_id_sets_match":
            authorized_ids
            == ledger_ids,

        "no_duplicate_authorization_ids":
            len(
                {
                    record[
                        "authorization_id"
                    ]
                    for record
                    in authorized_intents
                }
            )
            == len(
                authorized_intents
            ),

        "no_duplicate_ledger_ids":
            len(
                {
                    record[
                        "ledger_id"
                    ]
                    for record
                    in ledger_loaded
                }
            )
            == len(ledger_loaded),

        "all_ledger_records_dry_run":
            all(
                record["mode"]
                == PAPER_MODE
                for record
                in ledger_loaded
            ),

        "no_simulated_fills_created":
            all(
                record[
                    "simulated_fill_status"
                ]
                == "NOT_FILLED"
                for record
                in ledger_loaded
            ),

        "no_application_database_writes":
            all(
                record[
                    "persisted_to_application_database"
                ]
                is False
                for record
                in ledger_loaded
            ),

        "no_runtime_submissions":
            all(
                record[
                    "submitted_to_runtime"
                ]
                is False
                for record
                in ledger_loaded
            ),

        "no_broker_submissions":
            all(
                record[
                    "submitted_to_broker"
                ]
                is False
                for record
                in ledger_loaded
            ),

        "no_live_submissions":
            all(
                record[
                    "submitted_live"
                ]
                is False
                for record
                in ledger_loaded
            ),
    }

    reconciliation = {
        "generated_at":
            utc_now(),

        "candidate_id":
            candidate_id,

        "source_intent_count":
            len(source_intents),

        "authorized_intent_count":
            len(
                authorized_intents
            ),

        "ledger_record_count":
            len(ledger_loaded),

        "source_gross_value":
            source_gross_value,

        "authorized_gross_value":
            sum(
                abs(
                    record[
                        "target_order_value"
                    ]
                )
                for record
                in authorized_intents
            ),

        "checks":
            reconciliation_checks,

        "failed_checks":
            [
                name
                for name, passed
                in reconciliation_checks.items()
                if not bool(passed)
            ],

        "reconciled":
            all(
                bool(value)
                for value
                in reconciliation_checks.values()
            ),
    }

    reconciliation_path.write_text(
        json.dumps(
            reconciliation,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    authorization_checks = {
        **continuity_checks,
        **source_checks,

        "isolated_paper_authorization_created":
            all(
                record[
                    "paper_authorized"
                ]
                is True
                for record
                in authorized_intents
            ),

        "authorization_is_dry_run_only":
            all(
                record[
                    "dry_run_only"
                ]
                is True
                for record
                in authorized_intents
            ),

        "runtime_submission_not_authorized":
            all(
                record[
                    "runtime_submission_authorized"
                ]
                is False
                for record
                in authorized_intents
            ),

        "broker_submission_not_authorized":
            all(
                record[
                    "broker_submission_authorized"
                ]
                is False
                for record
                in authorized_intents
            ),

        "live_submission_not_authorized":
            all(
                record[
                    "live_submission_authorized"
                ]
                is False
                for record
                in authorized_intents
            ),

        "reconciliation_passed":
            reconciliation[
                "reconciled"
            ]
            is True,
    }

    failed_checks = [
        name
        for name, passed
        in authorization_checks.items()
        if not bool(passed)
    ]

    passed = not failed_checks

    classification = (
        "stage7y_controlled_paper_dry_run_qualified"
        if passed
        else "stage7y_paper_authorization_boundary_failure"
    )

    package = {
        "generated_at":
            utc_now(),

        "classification":
            classification,

        "candidate_id":
            candidate_id,

        "paper_mode":
            PAPER_MODE,

        "paper_account_value":
            EXPECTED_ACCOUNT_VALUE,

        "maximum_gross_exposure":
            MAXIMUM_GROSS_EXPOSURE,

        "maximum_symbol_exposure":
            MAXIMUM_SYMBOL_EXPOSURE,

        "authorized_intent_count":
            len(
                authorized_intents
            ),

        "authorized_gross_value":
            source_gross_value,

        "source_stage7x":
            str(
                stage7x_result_path
            ),

        "source_stage7x_sha256":
            sha256_file(
                stage7x_result_path
            ),

        "source_intents_sha256":
            sha256_file(
                stage7x_intents_path
            ),

        "authorized_intents_sha256":
            sha256_file(
                authorized_path
            ),

        "dry_run_ledger_sha256":
            sha256_file(
                ledger_path
            ),

        "reconciliation_sha256":
            sha256_file(
                reconciliation_path
            ),

        "authorization": {
            "isolated_paper_dry_run":
                passed,

            "application_runtime_submission":
                False,

            "application_database_persistence":
                False,

            "simulated_fill_creation":
                False,

            "broker_submission":
                False,

            "live_submission":
                False,

            "snaptrade_submission":
                False,
        },
    }

    package_path.write_text(
        json.dumps(
            package,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    summary = {
        "candidate_id":
            candidate_id,

        "source_intents":
            len(source_intents),

        "authorized_dry_run_intents":
            len(
                authorized_intents
            ),

        "authorized_gross_value":
            source_gross_value,

        "ledger_records":
            len(ledger_loaded),

        "reconciled":
            reconciliation[
                "reconciled"
            ],

        "paper_dry_run_authorized":
            passed,

        "runtime_submission_authorized":
            False,

        "broker_submission_authorized":
            False,

        "live_submission_authorized":
            False,
    }

    result = {
        "objective":
            (
                "Stage 7Y Controlled "
                "Paper-Only Authorization"
            ),

        "generated_at":
            utc_now(),

        "classification":
            classification,

        "passed":
            passed,

        "checks":
            authorization_checks,

        "failed_checks":
            failed_checks,

        "summary":
            summary,

        "reconciliation":
            reconciliation,

        "boundary_inventory":
            inventory,

        "artifacts": {
            "authorized_intents":
                str(authorized_path),

            "dry_run_ledger":
                str(ledger_path),

            "reconciliation":
                str(
                    reconciliation_path
                ),

            "authorization_package":
                str(package_path),

            "boundary_inventory":
                str(inventory_path),
        },

        "authorization": {
            "isolated_paper_dry_run":
                passed,

            "paper_runtime_submission":
                False,

            "paper_database_persistence":
                False,

            "paper_fill_simulation":
                False,

            "broker_execution":
                False,

            "live_execution":
                False,

            "snaptrade_execution":
                False,
        },

        "safety": {
            "source_files_modified":
                False,

            "model_retrained":
                False,

            "runtime_model_replaced":
                False,

            "application_database_written":
                False,

            "paper_order_submitted":
                False,

            "broker_request_created":
                False,

            "live_order_created":
                False,
        },
    }

    result_path.write_text(
        json.dumps(
            result,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    lines = [
        "=" * 100,
        (
            "NEUROVEST — STAGE 7Y "
            "CONTROLLED PAPER-ONLY AUTHORIZATION"
        ),
        "=" * 100,
        "",
        (
            "Qualification: "
            + (
                "PASS"
                if passed
                else "FAILED"
            )
        ),
        "",
        f"Classification: {classification}",
        "",
        "CHECKS:",
    ]

    for name, check_passed in (
        authorization_checks.items()
    ):
        lines.append(
            f"  {name:<72} {bool(check_passed)}"
        )

    lines.extend(
        [
            "",
            "SUMMARY:",
            json.dumps(
                summary,
                indent=2,
                sort_keys=True,
            ),
            "",
            (
                "The Stage 7X intents were "
                "authorized only for isolated dry-run use."
            ),
            (
                "The dry-run ledger exists only "
                "inside Stage 7Y evidence."
            ),
            (
                "No NeuroVest application database "
                "rows were written."
            ),
            "No simulated fills were created.",
            "No runtime order submission occurred.",
            "No SnapTrade request occurred.",
            "No broker request occurred.",
            "No live order occurred.",
            "Terminal remains open.",
        ]
    )

    report_path.write_text(
        "\n".join(lines)
        + "\n",
        encoding="utf-8",
    )

    print()
    print("=" * 100)
    print(
        "STAGE 7Y CONTROLLED PAPER-ONLY "
        "AUTHORIZATION COMPLETE"
    )
    print("=" * 100)
    print()
    print(
        json.dumps(
            {
                "passed":
                    passed,

                "classification":
                    classification,

                "failed_checks":
                    failed_checks,

                "summary":
                    summary,

                "result":
                    str(result_path),

                "report":
                    str(report_path),
            },
            indent=2,
            sort_keys=True,
        )
    )

    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
