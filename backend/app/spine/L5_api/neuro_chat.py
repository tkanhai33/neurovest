
from spine.L3_facade.repo_intelligence_facade import get_repo_intelligence
from spine.L5_api.ollama_reasoner import reason_about_repo

def run():
    print("NEURO + OLLAMA CLI ONLINE")
    print("type exit to quit")

    while True:
        u = input("\nyou > ").strip().lower()

        if u in {"exit", "quit"}:
            break

        snapshot = get_repo_intelligence(limit=50)
        intent = reason_about_repo(snapshot)

        it = intent.get("intent", "unknown")

        if it in ["status", "report"]:
            print(snapshot)

        elif it in ["analyze"]:
            print(intent)

        elif it in ["plan"]:
            print(intent)

        else:
            print({"echo": u, "intent": intent})


if __name__ == "__main__":
    run()
