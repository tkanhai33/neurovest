import subprocess
from backend.app.spine.L5_api.api import handle_request

def query_ollama(prompt: str):
    """
    Sends system structure + prompt to Ollama.
    """

    structure = handle_request({"type": "inspect"})

    full_prompt = f"""
You are a system observer.

Here is the current backend architecture:

{structure}

User question:
{prompt}

Respond ONLY based on structure.
"""

    result = subprocess.run(
        ["ollama", "run", "llama3.1"],
        input=full_prompt,
        text=True,
        capture_output=True
    )

    return result.stdout.strip()
