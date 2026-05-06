import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError

load_dotenv()

# ----------------------------
# CONFIG
# ----------------------------
API_KEY = os.getenv("GEMINI_API_KEY")

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-002")
FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "gemini-1.5-pro-002")

client = genai.Client(api_key=API_KEY)


# ----------------------------
# SAFE GEMINI CALL
# ----------------------------
def safe_generate(prompt: str, retries: int = 100) -> str:
    models_to_try = [MODEL_NAME, FALLBACK_MODEL]

    for model in models_to_try:
        for i in range(retries):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )

                if response and getattr(response, "text", None):
                    return response.text

            except ServerError:
                # exponential backoff for 503 / overload
                time.sleep(2 ** i)

            except Exception:
                # switch model immediately if unknown error
                break

    return "AI service is temporarily busy. Please try again in a moment."


# ----------------------------
# MAIN FUNCTION
# ----------------------------
def generate_answer(
    question: str,
    transactions: list,
    history: list,
    summary: str
) -> str:

    # ----------------------------
    # LIMIT CONTEXT (performance optimization)
    # ----------------------------
    history = history[-5:] if history else []
    transactions = transactions[:6] if transactions else []

    # ----------------------------
    # BUILD CONTEXT (lightweight & clean)
    # ----------------------------
    context_parts = []

    if summary:
        context_parts.append(f"MEMORY:\n{summary}")

    if history:
        context_parts.append(
            "CHAT HISTORY:\n" +
            "\n".join(
                f"{m.get('role', 'user')}: {m.get('content', '')}"
                for m in history
            )
        )

    if transactions:
        tx_lines = []
        for item in transactions:
            if isinstance(item, dict):
                payload = item.get("payload", {})
                text = payload.get("text")
                if text:
                    tx_lines.append(text)
                else:
                    tx_lines.append(str(payload))
            else:
                tx_lines.append(str(item))

        context_parts.append("TRANSACTIONS:\n" + "\n".join(tx_lines))

    context_text = "\n\n".join(context_parts)

    # ----------------------------
    # OPTIMIZED PROMPT (lower tokens = faster + fewer 503)
    # ----------------------------
    prompt = f"""
    You are NexPay AI, a financial assistant.

    RULES:
    - Use ONLY provided context
    - Never guess missing data
    - If missing → say "not available"
    - If unclear → say "I don't have enough information"

    CONTEXT:
    {context_text}

    QUESTION:
    {question}

    Answer briefly and clearly.
    """

    # ----------------------------
    # GENERATE
    # ----------------------------
    return safe_generate(prompt)
