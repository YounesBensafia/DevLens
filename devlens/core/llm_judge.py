"""
LLM layer — qualitative judgment via binary questions only.
Binary answers = low variance, reproducible across runs.
"""

import json
import re
from dataclasses import dataclass


@dataclass
class LLMJudgment:
    function_names_clear: bool
    undocumented_side_effects: bool
    junior_friendly: bool
    single_responsibility: bool
    magic_values: bool
    llm_score: float
    explanation: str


SYSTEM_PROMPT = """You are a senior software engineer reviewing code for comprehensibility.
You answer ONLY in the exact JSON format requested. No markdown, no preamble.
Be strict and honest — if you are unsure, answer false."""


def build_llm_prompt(source: str, file_path: str) -> str:
    snippet = source[:2000]
    return f"""Analyze this Python file for comprehensibility: {file_path}

```python
{snippet}
```

Respond ONLY with this JSON (no markdown, no extra text):
{{
  "function_names_clear": true/false,
  "undocumented_side_effects": true/false,
  "junior_friendly": true/false,
  "single_responsibility": true/false,
  "magic_values": true/false,
  "explanation": "one sentence: the main comprehensibility issue, or 'No major issues' if clean"
}}"""


def parse_llm_response(response_text: str) -> LLMJudgment:
    clean = re.sub(r"```json|```", "", response_text).strip()
    try:
        data = json.loads(clean)
    except json.JSONDecodeError:
        return LLMJudgment(
            function_names_clear=True,
            undocumented_side_effects=False,
            junior_friendly=True,
            single_responsibility=True,
            magic_values=False,
            llm_score=50.0,
            explanation="Could not parse LLM response.",
        )

    good = sum(
        [
            data.get("function_names_clear", True),
            data.get("junior_friendly", True),
            data.get("single_responsibility", True),
        ]
    )
    bad = sum(
        [
            data.get("undocumented_side_effects", False),
            data.get("magic_values", False),
        ]
    )
    llm_score = (good / 3) * 70 + ((2 - bad) / 2) * 30

    return LLMJudgment(
        function_names_clear=data.get("function_names_clear", True),
        undocumented_side_effects=data.get("undocumented_side_effects", False),
        junior_friendly=data.get("junior_friendly", True),
        single_responsibility=data.get("single_responsibility", True),
        magic_values=data.get("magic_values", False),
        llm_score=round(llm_score, 1),
        explanation=data.get("explanation", ""),
    )
