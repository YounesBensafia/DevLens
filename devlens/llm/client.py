import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests
from config.settings import GROQ_API_URL, HEADERS
from config.settings import MODEL_NAME, TEMPERATURE
from llm.exception import LLMClientError

def build_payload(system_msg: str, prompt_msg: str) -> dict:
    return {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt_msg}
        ],
        "temperature": TEMPERATURE,
    }

def send_request(payload: dict) -> dict:
    """Send payload to the LLM API and return parsed JSON response."""
    try:
        response = requests.post(
            GROQ_API_URL,
            headers=HEADERS,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise LLMClientError(f"Request failed: {e}")
    except ValueError:
        raise LLMClientError("Invalid JSON response from API")