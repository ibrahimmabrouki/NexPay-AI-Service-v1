# the main function in this file is the retrieve_transactions function which takes a query and returns a list of transactions that are similar to the query based on the cosine similarity between the query embedding and the transaction embeddings stored in Qdrant.
# later on we will use this function in the RAG pipeline to retrieve the relevant transactions based on the user query and then use these transactions to generate a response to the user query.

import os
from dotenv import load_dotenv
from qdrant_client.models import Filter, FieldCondition, MatchValue
from vector.qdrant_client import qdrant_client
from services.embedder import embed_text

load_dotenv()

COLLECTION_NAME = os.getenv(
    "QDRANT_TRANSACTIONS_COLLECTION",
    "transactions"
)


# In the function below we are creating a filter to filter the transactions based on the user_id
# this is very important step because we want to make sure that we are only retrieving the transactions that only belong to the user who is asking
# if we don't do this step we might retrieve transactions that belong to other users and this is a big privacy issue.
def search_transactions(user_id: str, question: str, limit: int = 5) -> list[dict]:
    question_verctor = embed_text(question)

    results = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=question_verctor,
        limit=limit,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="user_id",
                    match=MatchValue(value=user_id)
                )
            ]
        )
    )

    # print("Search results:", results)
    return [
        {
            "payload": result.payload,
            "score": result.score
        }
        for result in results.points
    ]
