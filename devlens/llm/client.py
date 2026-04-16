import requests
from devlens.config.settings import GROQ_API_URL, GROQ_API_KEY, get_headers
from devlens.config.settings import MODEL_NAME, TEMPERATURE, MAX_TOKENS
from devlens.llm.exception import LLMClientError

def build_payload(system_msg: str, prompt_msg: str) -> dict:
    return {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt_msg}
        ],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
    }

def send_request(payload: dict) -> dict:
    """Send payload to the LLM API and return parsed JSON response."""
    if not GROQ_API_KEY:
        raise LLMClientError(
            "GROQ_API_KEY is not set. "
            "Get a free key at https://console.groq.com/keys and run:\n"
            "  export GROQ_API_KEY=your_key_here"
        )
    try:
        response = requests.post(
            GROQ_API_URL,
            headers=get_headers(),
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise LLMClientError(f"Request failed: {e}")
    except ValueError:
        raise LLMClientError("Invalid JSON response from API")