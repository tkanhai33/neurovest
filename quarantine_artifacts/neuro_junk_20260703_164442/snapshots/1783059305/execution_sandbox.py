"""
L4 EXECUTION SANDBOX

NO BROKER ACCESS HERE
ONLY PASS-THROUGH BOUNDARY
"""

class ExecutionSandbox:

    def submit(self, order: dict):
        return {
            "status": "pending",
            "mode": "paper_only"
        }
