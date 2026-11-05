from backend.app.stacks.chat_public.math_tools.live_math import evaluate_live_math


def check(message, operation, expected):
    bundle = evaluate_live_math(message, requested=True)
    assert bundle.grounded
    assert bundle.operation == operation
    assert bundle.result["values"]["result"] == expected


def test_symbolic_math_operations():
    check("Differentiate x^3 + sin(x) with respect to x", "derivative", "3*x**2 + cos(x)")
    check("Integrate x^2 from 0 to 1 with respect to x", "definite_integral", "1/3")
    check("Find the limit of sin(x)/x as x approaches 0", "limit", "1")
    check("Solve x^2 - 5*x + 6 = 0 for x", "equation_solve", "[2, 3]")
    check("Find the determinant of [[1,2],[3,4]]", "matrix_determinant", "-2")
    check(
        "Evaluate the integral from zero to infinity of x cubed divided by e to the x minus one.",
        "improper_integral",
        "pi**4/15",
    )


def test_unsafe_expression_is_rejected():
    bundle = evaluate_live_math(
        "Differentiate __import__('os') with respect to x",
        requested=True,
    )
    assert not bundle.grounded
    assert bundle.error is not None
