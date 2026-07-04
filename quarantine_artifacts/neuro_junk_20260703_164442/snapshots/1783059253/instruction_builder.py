def build_instructions(results: list):

    output = "\n🧠 EXECUTION PLAN RESULTS\n"
    output += "=" * 40 + "\n\n"

    for i, r in enumerate(results):

        output += f"Step {i+1}:\n"
        output += f"{r}\n\n"

    output += "\n📌 NEXT ACTION SUGGESTION:\n"

    if len(results) > 0:
        output += "Review results above and confirm next execution step."

    return output
