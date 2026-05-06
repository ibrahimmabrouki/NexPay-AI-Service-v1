# similarly here we are using the os in order to read the values from our .env file
import os

from dotenv import load_dotenv

# This is the official Python package used to create the embeddings.
# SentenceTransformer is a class that allows us to easily create embeddings from text using pre-trained models.
# This model is used to transform the text from the created from the ledger_transactions table into a vector that can be stored in Qdrant.
from sentence_transformers import SentenceTransformer

load_dotenv()

# here we are getting the model name from the .env file and if it is not found we are using a default model name which is "sentence-transformers/all-MiniLM-L6-v2"
MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME",
                       "sentence-transformers/all-MiniLM-L6-v2")

# her we are creating an instance of the SentenceTransformer class and passing the model name to it.
# This will load the pre-trained model and allow us to use it to create embeddings from text.
model = None

def get_model():
    global model
    if model is None:
        model = SentenceTransformer(MODEL_NAME)
    return model

# input is text and output is a list of floats which is the vector representation of the input text.
def embed_text(text: str) -> list[float]:
    vector = get_model().encode(text).tolist()
    return vector
