import requests # type: ignore

from devlens.config.settings import (
    LLM_API_KEY,
    LLM_API_URL,
    LLM_MODEL,
    MAX_TOKENS,
    TEMPERATURE,
    get_headers,
)
from devlens.llm.exception import LLMClientError


def build_payload(system_msg: str, prompt_msg: str) -> dict:
    return {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt_msg},
        ],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
    }


def send_request(payload: dict) -> dict:
    """Send payload to the LLM API and return parsed JSON response."""
    if not LLM_API_KEY:
        raise LLMClientError(
            "LLM_API_KEY is not set. "
            "Set LLM_API_KEY (or GROQ_API_KEY) in your environment or .env file."
        )
    try:
        response = requests.post(LLM_API_URL, headers=get_headers(), json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise LLMClientError(f"Request failed: {e}") from e
    except ValueError:
        raise LLMClientError("Invalid JSON response from API") from None
