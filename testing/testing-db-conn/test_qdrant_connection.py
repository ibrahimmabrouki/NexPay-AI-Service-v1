from vector.qdrant_client import qdrant_client


collections = qdrant_client.get_collections()

print("Connected to Qdrant successfully")
print(collections)