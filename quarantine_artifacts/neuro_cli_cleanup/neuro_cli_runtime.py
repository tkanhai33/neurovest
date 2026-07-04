from spine.L4_runtime.compiler.contract_diff_engine import compute_contract_diff
from spine.L4_runtime.compiler.contract_patch_engine import generate_contract_patch_plan
from spine.L4_runtime.compiler.execution_gate import validate_stage


class NeuroCLI:

    def __init__(self):
        self.last_plan = []

    def build_plan(self):
        diff = compute_contract_diff(limit=200)
        plan = generate_contract_patch_plan(limit=200)

        self.last_plan = plan["patch_plan"]

        print("\n🧠 NEURO PLAN GENERATED")
        print("----------------------")
        print(f"Missing stacks: {len(diff['missing'])}")
        print(f"Extra stacks: {len(diff['extra'])}")

        for i, p in enumerate(self.last_plan[:5]):
            print(f"{i+1}. {p['file']} -> {p['reason']}")

        print("\nType 'approve' to execute, or 'exit' to quit")

    def execute(self):
        if not self.last_plan:
            print("No plan available.")
            return

        print("\n🚀 EXECUTING PLAN...")
        results = []

        for p in self.last_plan:
            r = validate_stage({
                "stack": p.get("stack", "unknown"),
                "files": [p["file"]]
            })

            results.append((p, r))

        print("\n🧠 EXECUTION COMPLETE")
        print("----------------------")

        for p, r in results[:5]:
            print(f"{p['file']} -> {'APPROVED' if r['approved'] else 'REJECTED'}")

    def run(self):

        print("\n🧠 NEURO SYSTEM ONLINE")
        print("======================")

        while True:
            cmd = input("\nneuro > ").strip().lower()

            if cmd == "exit":
                break

            if cmd in ["what should i build next", "plan", "next", "build"]:
                self.build_plan()

            elif cmd == "approve":
                self.execute()

            else:
                print("Command not recognized. Try: build / approve / exit")


if __name__ == "__main__":
    NeuroCLI().run()
