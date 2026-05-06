import os
from dotenv import load_dotenv
# importing the qdrant client already created to communicate with Qdrant
from vector.qdrant_client import qdrant_client

# importing the Distance and VectorParams classes from the qdrant_client.models module. These classes are used to specify the distance metric and vector parameters when creating a collection in Qdrant.
from qdrant_client.models import Distance, VectorParams

load_dotenv()

COLLECTION_NAME = os.getenv(
    "QDRANT_TRANSACTIONS_COLLECTION",
    "transactions"
)


qdrant_client.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)


print(f"Collection '{COLLECTION_NAME}' created successfully.")

# Important: recreate_collection deletes the collection if it already exists and creates it again.