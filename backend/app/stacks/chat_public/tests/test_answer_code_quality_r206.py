from backend.app.stacks.chat_public.answer_code_quality_13d_r90 import (
    inspect_python_answer,
)


QUESTION = "Write a Python unittest example with sequential and concurrent tests."


def test_module_level_self_is_withheld() -> None:
    answer = "\n".join([
        "```python",
        "import unittest",
        "class Limiter:",
        "    def allow(self): return True",
        "self.assertTrue(Limiter().allow())",
        "```",
    ])

    candidate, report = inspect_python_answer(QUESTION, answer)

    assert candidate != answer
    assert "withheld" in candidate
    assert report["invalid_unittest_structure_blocks"] == 1
    assert "uses self at module level" in report["unittest_structure_issues"]


def test_unittest_methods_without_assertions_are_withheld() -> None:
    answer = "\n".join([
        "```python",
        "import unittest",
        "class Tests(unittest.TestCase):",
        "    def test_sequential(self):",
        "        result = True",
        "    def test_concurrent(self):",
        "        result = False",
        "```",
    ])

    candidate, report = inspect_python_answer(QUESTION, answer)

    assert candidate != answer
    assert "withheld" in candidate
    assert report["invalid_unittest_structure_blocks"] == 1
    assert any(
        "has no assertion" in issue
        for issue in report["unittest_structure_issues"]
    )


def test_valid_two_test_unittest_example_is_retained() -> None:
    answer = "\n".join([
        "```python",
        "import unittest",
        "class Tests(unittest.TestCase):",
        "    def test_sequential(self):",
        "        self.assertTrue(True)",
        "    def test_concurrent(self):",
        "        self.assertFalse(False)",
        "```",
    ])

    candidate, report = inspect_python_answer(QUESTION, answer)

    assert candidate == answer
    assert report.get("invalid_unittest_structure_blocks", 0) == 0


def test_non_unittest_python_request_is_not_rewritten() -> None:
    question = "Write a Python function that adds two numbers."
    answer = "```python\ndef add(a, b):\n    return a + b\n```"

    candidate, report = inspect_python_answer(question, answer)

    assert candidate == answer
    assert report["scope"] == "python_programming"
    assert report.get("invalid_unittest_structure_blocks", 0) == 0
