from spine.L4_runtime.compiler.build_order_engine import compute_build_order
def test_build_order():
    r = compute_build_order(limit=200)
    assert "build_sequence" in r
