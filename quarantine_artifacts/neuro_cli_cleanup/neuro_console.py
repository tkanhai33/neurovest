from __future__ import annotations

import os
import sys
import time
import threading

from spine.L5_api.repo_autonomous_orchestrator import chat


class NeuroConsole:
    def __init__(self):
        self.running = True
        self.buffer = []

    def clear(self):
        os.system("clear")

    def render(self, user_input=None, response=None):
        self.clear()

        print("🧠 NEURO CONSOLE MODE")
        print("=" * 50)

        print("\n💬 Conversation\n")

        for i, item in enumerate(self.buffer[-10:]):
            print(f"you: {item['user']}")
            print(f"neuro: {item['response']['next_action']}")
            print("-" * 50)

        if user_input:
            print(f"\nyou: {user_input}")
            print(f"neuro: {response['next_action']}")
            print("-" * 50)

        print("\nType 'exit' to quit")
        print("Type anything to continue system reasoning...\n")

    def run(self):
        self.render()

        while self.running:
            user_input = input("you > ")

            if user_input.strip().lower() == "exit":
                break

            response = chat(user_input)

            self.buffer.append({
                "user": user_input,
                "response": response
            })

            self.render(user_input, response)


if __name__ == "__main__":
    console = NeuroConsole()
    console.run()
