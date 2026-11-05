from backend.app.stacks.chat_public.answer_code_quality_13d_r90 import (
    inspect_python_answer,
)


def test_blocks_wrong_fastapi_request_validation_import():
    question = "Explain FastAPI validation."
    answer = "from fastapi import FastAPI, RequestValidationError"
    candidate, report = inspect_python_answer(question, answer)

    assert "withholding this answer" in candidate
    assert report["r215_known_technical_blocks"] == 1


def test_blocks_journalmaxuse_claim():
    question = "Explain systemd service failures."
    answer = "Without JournalMaxUse= settings, diagnostics may be lost."
    candidate, report = inspect_python_answer(question, answer)

    assert "withholding this answer" in candidate
    assert report["r215_known_technical_blocks"] == 1


def test_blocks_false_cast_runtime_claim():
    question = "Explain Python type checking and typing.cast."
    answer = "typing.cast(str, value) crashes at runtime if value is an integer."
    candidate, report = inspect_python_answer(question, answer)

    assert "withholding this answer" in candidate
    assert report["r215_known_technical_blocks"] == 1


def test_keeps_correct_cast_explanation():
    question = "Explain Python type checking and typing.cast."
    answer = (
        "typing.cast returns its input unchanged and does not validate "
        "the value at runtime."
    )
    candidate, report = inspect_python_answer(question, answer)

    assert report["r215_known_technical_blocks"] == 0
    assert "withholding this answer" not in candidate

def test_blocks_postgresql_automatic_rollback_to_begin_claim():
    question = "Explain PostgreSQL transactions."
    answer = (
        "If an error occurs, PostgreSQL rolls back to the last BEGIN "
        "or SAVEPOINT."
    )
    candidate, report = inspect_python_answer(question, answer)

    assert "withholding this answer" in candidate
    assert report["r215_known_technical_blocks"] == 1


def test_blocks_unsupported_systemd_journald_directive():
    question = "Explain systemd service failures."
    answer = "Set JournalMaxFileSize= to keep logs from being lost."
    candidate, report = inspect_python_answer(question, answer)

    assert "withholding this answer" in candidate
    assert report["r215_known_technical_blocks"] == 1


def test_blocks_unbounded_systemd_restart_claim():
    question = "Explain systemd restart behavior."
    answer = "Restart=always restarts the service indefinitely."
    candidate, report = inspect_python_answer(question, answer)

    assert "withholding this answer" in candidate
    assert report["r215_known_technical_blocks"] == 1


def test_blocks_non_atomic_http_idempotency_example():
    question = "Explain HTTP idempotency."
    answer = "\n".join((
        "if idempotency_key in processed_requests:",
        "    return 'Already processed'",
        "process(data)",
        "processed_requests[idempotency_key] = True",
    ))
    candidate, report = inspect_python_answer(question, answer)

    assert "withholding this answer" in candidate
    assert report["r215_known_technical_blocks"] == 1


def test_r216_final_guard_is_before_response_sync():
    from pathlib import Path

    runtime_path = Path(__file__).parents[1] / "chat_runtime.py"
    source = runtime_path.read_text(encoding="utf-8")
    marker = "NEUROVEST_R216_FINAL_POST_MUTATION_TECHNICAL_GUARD"
    sync = "# Synchronize the guarded response for persistence"

    assert marker in source
    assert source.index(marker) < source.index(sync)

def test_r217_blocks_postgres_automatic_rollback_claim():
    question = "Explain PostgreSQL transactions."
    answer = (
        "If an error occurs during a transaction, it typically triggers "
        "an automatic rollback. If the UPDATE fails, PostgreSQL rolls back "
        "the INSERT."
    )
    candidate, report = inspect_python_answer(question, answer)

    assert "withholding this answer" in candidate
    assert any(
        "PostgreSQL explicit-transaction rollback" in issue
        for issue in report["r215_known_technical_issues"]
    )


def test_r217_allows_correct_postgres_aborted_transaction_explanation():
    question = "Explain PostgreSQL transactions."
    answer = (
        "In an explicit transaction, a statement error leaves the transaction "
        "aborted until ROLLBACK or ROLLBACK TO SAVEPOINT is issued. Earlier "
        "uncommitted statements are discarded when that rollback is issued."
    )
    candidate, report = inspect_python_answer(question, answer)

    assert report["r215_known_technical_blocks"] == 0
    assert "withholding this answer" not in candidate


def test_r217_blocks_non_atomic_idempotency_check_process_store():
    question = "Explain HTTP idempotency."
    answer = """Pseudocode:
```python
if key_exists_in_cache:
    return 200
else:
    process_request()
    store_key_in_cache()
```"""
    candidate, report = inspect_python_answer(question, answer)

    assert "withholding this answer" in candidate
    assert any(
        "non-atomic idempotency" in issue
        for issue in report["r215_known_technical_issues"]
    )


def test_r217_allows_idempotency_with_atomic_claim():
    question = "Explain HTTP idempotency."
    answer = """Use an atomic key claim:
```python
with transaction:
    if key_exists_in_cache:
        return existing_result
    claim_idempotency_key(key)  # unique constraint
    process_request()
```"""
    candidate, report = inspect_python_answer(question, answer)

    assert report["r215_known_technical_blocks"] == 0
    assert "withholding this answer" not in candidate

