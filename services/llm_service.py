# import os
# import time
# from dotenv import load_dotenv
# from google import genai
# from google.genai.errors import ServerError

# load_dotenv()

# # ----------------------------
# # CONFIG
# # ----------------------------
# API_KEY = os.getenv("GEMINI_API_KEY")

# MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
# FALLBACK_MODEL = "gemini-1.5-pro-002"

# client = genai.Client(api_key=API_KEY)


# # ----------------------------
# # SAFE GEMINI CALL
# # ----------------------------
# def safe_generate(prompt: str, retries: int = 3):
#     models_to_try = [MODEL_NAME, FALLBACK_MODEL]

#     for model in models_to_try:
#         for i in range(retries):
#             try:
#                 response = client.models.generate_content(
#                     model=model,
#                     contents=prompt,
#                     config={
#                         "temperature": 0.2,
#                         "max_output_tokens": 150,
#                     },
#                 )

#                 if response and getattr(response, "text", None):
#                     return response.text

#             except ServerError:
#                 # exponential backoff for 503 / overload
#                 time.sleep(2 ** i)

#             except Exception:
#                 # switch model immediately if unknown error
#                 break

#     return "AI service is temporarily busy. Please try again in a moment."


# # ----------------------------
# # MAIN FUNCTION
# # ----------------------------
# def generate_answer(
#     question: str,
#     transactions: list,
#     history: list,
#     summary: str
# ) -> str:

#     print("question:", question)
#     print("transactions:", transactions)
#     print("history:", history)
#     print("summary:", summary)

#     # ----------------------------
#     # LIMIT CONTEXT (performance optimization)
#     # ----------------------------
#     summary = summary[:500] if summary else ""

#     history = history[-5:] if history else []
#     history = [
#         {
#             "role": m.get("role", "user"),
#             "content": m.get("content", "")[:200]
#         }
#         for m in history
#     ]

#     # ----------------------------
#     # BUILD CONTEXT (lightweight & clean)
#     # ----------------------------
#     context_parts = []

#     if summary:
#         context_parts.append(f"MEMORY:\n{summary}")

#     if history:
#         context_parts.append(
#             "CHAT HISTORY:\n" +
#             "\n".join(
#                 f"{m.get('role', 'user')}: {m.get('content', '')}"
#                 for m in history
#             )
#         )

#     if transactions:
#         context_parts.append(
#             "TRANSACTIONS:\n" + "\n".join(transactions)
#         )

#     context_text = "\n\n".join(context_parts)

#     # ----------------------------
#     # OPTIMIZED PROMPT (lower tokens = faster + fewer 503)
#     # ----------------------------
#     prompt = f"""
# You are NexPay AI, a financial assistant.

# RULES:
# - Use ONLY provided context
# - Never guess missing data
# - If missing → say "not available"
# - If unclear → say "I don't have enough information"

# CONTEXT:
# {context_text}

# QUESTION:
# {question}

# Answer briefly and clearly.
# """

#     # ----------------------------
#     # GENERATE
#     # ----------------------------
#     return safe_generate(prompt)


import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

# ----------------------------
# CONFIG
# ----------------------------
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.1"


# ----------------------------
# SAFE OLLAMA CALL
# ----------------------------
def safe_generate(prompt: str, retries: int = 3):
    for i in range(retries):
        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.2,
                        "num_predict": 150
                    }
                },
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("response", "").strip()

        except requests.exceptions.RequestException:
            time.sleep(2 ** i)

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

    print("question:", question)
    print("transactions:", transactions)
    print("history:", history)
    print("summary:", summary)

    # ----------------------------
    # LIMIT CONTEXT
    # ----------------------------
    summary = summary[:500] if summary else ""

    history = history[-5:] if history else []
    history = [
        {
            "role": m.get("role", "user"),
            "content": m.get("content", "")[:200]
        }
        for m in history
    ]

    # ----------------------------
    # BUILD CONTEXT
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
        context_parts.append(
            "TRANSACTIONS:\n" + "\n".join(transactions)
        )

    context_text = "\n\n".join(context_parts)

    # ----------------------------
    # PROMPT
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
