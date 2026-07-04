from spine.L5_api.neuro_conversation_brain import chat as brain_chat

def main():
    print("🧠 NEURO UNIFIED RUNTIME ONLINE")
    print("Type 'exit' to quit")
    print("Type 'approve' to execute last action")
    print("-" * 50)

    while True:
        user = input("\nyou > ").strip()

        if user.lower() == "exit":
            break

        result = brain_chat(user)

        print("\nneuro >")
        print(result.get("response"))
        print("-" * 50)


if __name__ == "__main__":
    main()
