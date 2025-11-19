import requests
from requests.exceptions import RequestException, Timeout

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = "gemma3:1b"
DEFAULT_TIMEOUT = 30  # note: seconds

def ollama_call(prompt: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    """
    Send prompt to Ollama and return the text response.
    Raises RuntimeError on failures with a clear message.
    """
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,  
        "options": {
            "temperature": 0.3
        }
    }

    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
        resp.raise_for_status()
    except Timeout as e:
        raise RuntimeError(f"Ollama request timed out after {timeout}s") from e
    except RequestException as e:
        body = None
        try:
            body = resp.text
        except Exception:
            body = "<no body>"
        raise RuntimeError(f"Ollama request failed: {e}; response_body={body}") from e

    try:
        data = resp.json()
    except ValueError as e:
        raise RuntimeError(f"Ollama returned non-JSON response: {resp.text[:500]}") from e

    reply = data.get("response") or data.get("text") or ""
    if not reply:
        raise RuntimeError(f"Ollama returned empty response: {data}")

    return str(reply).strip()