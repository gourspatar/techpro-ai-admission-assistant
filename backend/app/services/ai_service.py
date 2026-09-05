from typing import TypedDict


class ChatMessage(TypedDict):
    role: str
    content: str


SYSTEM_PROMPT = """
You are TechPro's AI Admission Assistant.

Your job is to help prospective students with questions about
TechPro's courses and admission process.

Be helpful, professional, and concise.

Do not invent information about TechPro.
"""


def generate_ai_response(messages: list[ChatMessage]) -> str:
    # Temporary mock response.
    # We will replace this with the OpenAI API call later.

    latest_message = messages[-1]["content"]

    return f"Mock AI response to: {latest_message}"