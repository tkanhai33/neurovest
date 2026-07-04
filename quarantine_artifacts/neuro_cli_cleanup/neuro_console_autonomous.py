from __future__ import annotations

import os
import time

from spine.L5_api.repo_autonomous_orchestrator import chat
from spine.L5_api.repo_executor import execute_action
from spine.L4_runtime.compiler.contract_diff_engine import compute_contract_diff


class AutonomousConsole:
    def __init__(self):
        self.memory = []

    def render(self, msg, result, exec_result=None):
        print("\n🧠 NEURO LOOP")
        print("-" * 50)
        print("YOU:", msg)
        print("NEXT:", result.get("next_action"))
        if exec_result:
            print("EXEC:", exec_result)
        print("-" * 50)

    def run(self):
        print("🧠 NEURO AUTONOMOUS MODE ONLINE")
        print("Type 'exit' to stop\n")

        while True:
            msg = input("you > ")

            if msg.strip().lower() == "exit":
                break

            # 1. reasoning + planning
            result = chat(msg)

            exec_result = None

            # 2. EXECUTE ACTION AUTOMATICALLY
            action = result.get("next_action")

            if action:
                exec_result = execute_action(action)

            # 3. VERIFY SYSTEM STATE AFTER EXECUTION
            diff = compute_contract_diff(limit=200)

            # 4. update memory
            self.memory.append({
                "msg": msg,
                "action": action,
                "exec": exec_result,
                "diff": diff
            })

            # 5. render
            self.render(msg, result, exec_result)


if __name__ == "__main__":
    AutonomousConsole().run()
