from services.retriever import search_transactions
from services.llm_service import generate_answer


def rag_pipeline(user_id: str, question: str, history: list, summary: str) -> str:
    # 1. retrieve relevant transactions
    results = search_transactions(user_id=user_id, question=question)

    # 2. pass them to LLM
    answer = generate_answer(
        question=question,
        transactions=results,
        history=history,
        summary=summary
    )
    return answer


# User question
# → search_transactions (Qdrant)
# → get relevant context
# → send to LLM
# → return final answer
