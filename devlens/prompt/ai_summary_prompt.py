def generate_ai_summary_prompt(file_content: str, file_name: str) -> str:
    return f"""You are an expert code analyst. Analyze the following file and provide a structured summary.

    Instructions:
    1. Detect the programming language of the file based on its content.
    2. Summarize what the file does in 1 to 3 clear sentences. Focus on its purpose, not line-by-line details.
    3. If the file has no content, say: "be careful this file is empty".

    Format your response exactly as follows:
    - Language: <detected_language>
    - What it does: <file_purpose_or_warning>

    --- File Name ---
    {file_name}

    --- File Content ---
    {file_content}
    """



def system_message() -> str:
    return "You are a code analysis assistant. " \
    "Provide only a concise, direct summary of what the any file does. " \
    "Do not show your thinking process or reasoning steps. " \
    "Just give the final summary in 1-3 sentences." \
    "Add some emojis to the summary" 
