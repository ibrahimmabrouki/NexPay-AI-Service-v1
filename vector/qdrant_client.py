# This lets Python read the values from our os environment
import os

from dotenv import load_dotenv

# This is the official Python package used to make the connection with Qdrant.
from qdrant_client import QdrantClient


load_dotenv()

# A client is an object that lets your Python code communicate with another service.
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

# This client will be reused in the following:
# 1- retriever.py
# 2- embed_transactions.py
# 3- rag_pipeline.py