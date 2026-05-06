from vector.qdrant_client import qdrant_client
import os
from dotenv import load_dotenv

load_dotenv()

COLLECTION_NAME = os.getenv("QDRANT_TRANSACTIONS_COLLECTION")

qdrant_client.create_payload_index(
    collection_name=COLLECTION_NAME,
    field_name="user_id",
    field_schema="keyword",
)

print("Index created for user_id")