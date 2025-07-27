from openai import OpenAI
from devlens.config import OPENAI_API_KEY
import os

client = OpenAI(api_key=OPENAI_API_KEY)

def summarize_code(path: str, max_files=1):
    summaries = []

    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".py") and len(summaries) < max_files:
                with open(os.path.join(root, file), "r", errors="ignore") as f:
                    content = f.read()[:3000]
                    prompt = f"Summarize what this Python file does:\n\n{content}"
                    try:
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.2,
                        )
                        summary = response.choices[0].message.content.strip()
                        summaries.append((file, summary))
                    except Exception as e:
                        summaries.append((file, f"[ERROR] {e}"))
    return summaries
