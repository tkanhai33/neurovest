from __future__ import annotations

import time
from spine.L5_api.repo_autonomous_orchestrator import chat


def run_loop():
    print("🧠 Neuro Autonomous Agent ONLINE")
    print("Type: 'exit' to stop\n")

    while True:
        user = input("you > ")

        if user.strip().lower() == "exit":
            break

        result = chat(user)

        print("\nneuro >")
        print(result["reasoning"])
        print("NEXT ACTION:", result["next_action"])
        print("STATUS:", result["mode"])
        print("-" * 40)


if __name__ == "__main__":
    run_loop()
