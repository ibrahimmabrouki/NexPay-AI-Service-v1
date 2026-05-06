from services.retriever import search_transactions


results = search_transactions(
    user_id="user_123",
    question="How much did I send to Ahmad?",
    limit=3,
)


for item in results:
    print("Score:", item["score"])
    print("Text:", item["payload"]["text"])
    print()
