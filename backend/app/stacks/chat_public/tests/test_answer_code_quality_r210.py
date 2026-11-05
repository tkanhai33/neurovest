import ast
import re

from backend.app.stacks.chat_public.answer_code_quality_13d_r90 import (
    inspect_python_answer,
)


def first_fence(answer):
    match = re.search(
        r"(?ms)^[ \t]{0,3}```([^\n]*)\n(.*?)^[ \t]{0,3}```",
        answer,
    )
    return match


def test_indented_standalone_python_fence_is_dedented():
    question = "In Python, explain an off-by-one error and show a loop."
    answer = "```python\n   for item in data:\n       print(item)\n```"

    candidate, report = inspect_python_answer(question, answer)
    fence = first_fence(candidate)

    assert fence is not None
    assert fence.group(1).strip() == "python"
    ast.parse(fence.group(2))
    assert report["r210_python_fence_dedents"] == 1


def test_invalid_pseudocode_is_labeled_as_pseudocode():
    question = "Explain HTTP idempotency with a concrete example or pseudocode."
    answer = (
        "```python\n"
        "def handle_payment(key, amount):\n"
        "    if key exists in db:\n"
        '        return "Already processed"\n'
        "```"
    )

    candidate, report = inspect_python_answer(question, answer)
    fence = first_fence(candidate)

    assert fence is not None
    assert fence.group(1).strip() == "pseudocode"
    assert "if key exists in db" in fence.group(2)
    assert report["r210_pseudocode_fence_relabels"] == 1


def test_sql_mislabeled_as_python_is_relabelled():
    question = "Explain PostgreSQL transaction handling."
    answer = (
        "```python\n"
        "BEGIN;\n"
        "UPDATE accounts SET balance = balance - 100;\n"
        "COMMIT;\n"
        "```"
    )

    candidate, report = inspect_python_answer(question, answer)
    fence = first_fence(candidate)

    assert fence is not None
    assert fence.group(1).strip() == "sql"
    assert report["r210_sql_fence_relabels"] == 1


def test_invalid_python_fence_is_withheld_even_outside_python_scope():
    question = "Explain this application workflow."
    answer = "```python\ndef broken(:\n    pass\n```"

    candidate, report = inspect_python_answer(question, answer)

    assert "Python example withheld" in candidate
    assert report["r210_invalid_python_fence_blocks"] == 1
    assert report["r210_invalid_python_fence_issues"]


def test_valid_python_fence_remains_python():
    question = "Explain this application workflow."
    answer = "```python\ndef allow(value):\n    return bool(value)\n```"

    candidate, report = inspect_python_answer(question, answer)
    fence = first_fence(candidate)

    assert fence is not None
    assert fence.group(1).strip() == "python"
    ast.parse(fence.group(2))
    assert report["r210_invalid_python_fence_blocks"] == 0

def test_valid_python_stays_python_when_prompt_allows_pseudocode():
    question = "Explain HTTP idempotency with a concrete example or pseudocode."
    answer = """```python
def remember(key, store):
    if key in store:
        return store[key]
    store[key] = "done"
    return store[key]
```"""

    candidate, report = inspect_python_answer(question, answer)
    fence = first_fence(candidate)

    assert fence is not None
    assert fence.group(1).strip() == "python"
    ast.parse(fence.group(2))
    assert report["r210_pseudocode_fence_relabels"] == 0

