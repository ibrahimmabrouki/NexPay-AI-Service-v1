from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def generate_memory_summary(messages: list[dict]) -> str:
    """
    Generates a compact financial memory summary for a user
    based on their chat history.
    """

    formatted_messages = "\n".join(
        f"{msg.get('role', 'user')}: {msg.get('content', '')}"
        for msg in messages
    )

    prompt = f"""
You are a memory compression engine for a fintech application called NexPay.

Your job is to summarize the user's conversation history into a compact financial memory.

Rules:
- Focus ONLY on financially relevant information.
- Capture:
  - frequent transactions
  - users interacted with
  - currencies used
  - spending or transfer patterns
  - important preferences
- Ignore greetings, small talk, and irrelevant chat.
- Keep it short (max 8-12 lines).
- Do NOT hallucinate or assume missing data.

Conversation:
{formatted_messages}

Return a structured memory summary.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    return response.text
