import json
import urllib.request
import urllib.error


def call_ai_api(prompt: str) -> str:
    """Call the local Ollama/Gemma4 model for the given prompt."""
    return call_ollama_api(prompt)


def call_ollama_api(prompt: str) -> str:
    """Call the local Ollama API on localhost:11434."""
    system_prompt = (
        "You are a helpful offline assistant running locally with Ollama/Gemma4. "
        "Answer the user clearly and do not mention external Google services or API keys."
    )

    api_url = "http://localhost:11434/v1/chat/completions"
    model = "gemma4"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        api_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Ollama API HTTPError {e.code}: {body}") from e

    j = json.loads(raw)
    return j["choices"][0]["message"]["content"]
