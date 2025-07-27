import os
import requests
from devlens.config import GROQ_API_KEY  # Replace with your Groq key storage



GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json",
}

def summarize_code(path: str, max_files=1):
    summaries = []

    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".py") and len(summaries) < max_files:
                with open(os.path.join(root, file), "r", errors="ignore") as f:
                    content = f.read()[:3000]  # Limit input size
                    prompt = f"Summarize what this Python file does:\n\n{content}"
                    print(prompt)
                    payload = {
                        "model": "deepseek-r1-distill-llama-70b",  # You can also try llama3-8b
                        "messages": [
                            {"role": "system", "content": "You are an assistant that summarizes Python code."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.2
                    }

                    try:
                        response = requests.post(GROQ_API_URL, headers=HEADERS, json=payload)
                        response.raise_for_status()
                        data = response.json()
                        summary = data["choices"][0]["message"]["content"].strip()
                        summaries.append((file, summary))
                    except Exception as e:
                        summaries.append((file, f"[ERROR] {e}"))

    return summaries
