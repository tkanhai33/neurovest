def request_approval(proposal: dict):

    print("\n🧠 NEURO EXECUTION PROPOSAL")
    print("=" * 40)

    print(f"ACTION: {proposal['proposal']['action']}")
    print(f"REASON: {proposal['proposal']['reason']}")
    print(f"CONFIDENCE: {proposal['proposal']['confidence']}")

    print("\nDO YOU APPROVE? (yes/no): ", end="")

    response = input().strip().lower()

    return response == "yes"
