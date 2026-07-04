from spine.L4_runtime.signals.signal_generator import generate_signals
def test_signal_generation():
    s = generate_signals(limit=200)
    assert isinstance(s, list)
