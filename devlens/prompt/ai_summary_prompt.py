def generate_ai_summary_prompt(file_content: str) -> str:
    return f"""Summarize this file.

    - Language: detect it from the content
    - What it does: explain its purpose clearly

    --- File Content ---
    {file_content}
    """

def system_message() -> str:
    return "You are a code analysis assistant. " \
    "Provide only a concise, direct summary of what the any file does. " \
    "Do not show your thinking process or reasoning steps. " \
    "Just give the final summary in 1-3 sentences."
