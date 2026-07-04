import subprocess
import sys
import time


TEST_QUESTIONS = [
    "How do we structure a fintech AI day trading system using SnapTrade?",
    "What are the biggest architectural risks in this repo?",
    "What should be built first for a trading engine?",
]


def run_cli():
    """
    Launch CLI as subprocess (interactive mode simulation)
    """
    return subprocess.Popen(
        ["python3", "spine/L5_api/neuro_cli_stateful.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )


def send_and_read(proc, msg):
    proc.stdin.write(msg + "\n")
    proc.stdin.flush()
    time.sleep(2)  # allow model to respond

    output = ""
    while proc.stdout.readable():
        line = proc.stdout.readline()
        if not line:
            break
        output += line
        if len(output) > 3000:
            break

    return output


def validate_output(output):
    """
    Basic structural validation
    """

    checks = {
        "has_fact_section": "FACT" in output,
        "has_hotspot_section": "HOTSPOT" in output,
        "has_next_step": "NEXT STEP" in output,
        "not_empty": len(output.strip()) > 50,
    }

    return checks


def main():
    print("\n🧪 NEURO CLI TEST SUITE STARTING\n")

    proc = run_cli()

    time.sleep(3)  # let CLI boot

    results = []

    for q in TEST_QUESTIONS:
        print(f"\n▶ TEST QUESTION: {q}")

        proc.stdin.write(q + "\n")
        proc.stdin.flush()

        time.sleep(4)

        output = ""
        try:
            output = proc.stdout.readline()
        except Exception:
            pass

        checks = validate_output(output)

        results.append((q, checks))

        print("RESULT CHECK:")
        for k, v in checks.items():
            print(f"  {k}: {v}")

    proc.kill()

    print("\n🧪 FINAL TEST SUMMARY\n")

    passed = sum(all(c.values()) for _, c in results)
    total = len(results)

    print(f"PASSED: {passed}/{total}")

    if passed == total:
        print("✔ SYSTEM IS STABLE AND STRUCTURED")
    else:
        print("⚠ SYSTEM NEEDS REFINEMENT")


if __name__ == "__main__":
    main()
