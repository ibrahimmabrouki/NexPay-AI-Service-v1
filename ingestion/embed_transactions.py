import os
from dotenv import load_dotenv
from qdrant_client.models import PointStruct
from vector.qdrant_client import qdrant_client
from services.embedder import embed_text
import uuid

load_dotenv()

COLLECTION_NAME = os.getenv(
    "QDRANT_TRANSACTIONS_COLLECTION",
    "transactions"
)


# we need a method that will transform the transaction data from the ledger_transactions table into a text format so that we later embed this text (beacuse it is better to embed text than to embed structured data)
# and then store the embedding in Qdrant.
def transaction_to_text(transaction: dict) -> str:
    tx_type = transaction.get("type")
    created_at = transaction.get("created_at")

    user_name = transaction.get("user_name", "Unknown")
    phone_number = transaction.get("phone_number", "Unknown")

    if tx_type == "TRANSFER":
        return (
            f"TRANSFER | "
            f"sender: {user_name} | "
            f"sender_phone: {phone_number} | "
            f"receiver: {transaction.get('receiver_name', 'Unknown')} | "
            f"receiver_phone: {transaction.get('receiver_phone', 'Unknown')} | "
            f"amount: {transaction.get('amount')} "
            f"{transaction.get('currency')} | "
            f"date: {created_at}"
        )

    if tx_type == "TOPUP":
        return (
            f"TOPUP | "
            f"user: {user_name} | "
            f"phone: {phone_number} | "
            f"amount: {transaction.get('amount')} "
            f"{transaction.get('currency')} | "
            f"date: {created_at}"
        )

    if tx_type == "CONVERSION":
        return (
            f"CONVERSION | "
            f"user: {user_name} | "
            f"phone: {phone_number} | "
            f"from: {transaction.get('amount_from')} "
            f"{transaction.get('from_currency')} | "
            f"to: {transaction.get('amount_to')} "
            f"{transaction.get('to_currency')} | "
            f"date: {created_at}"
        )

    return (
        f"TRANSACTION | "
        f"user: {user_name} | "
        f"phone: {phone_number} | "
        f"date: {created_at}"
    )


def upsert_transaction(transaction: dict):
    text = transaction_to_text(transaction)
    vector = embed_text(text)

    point = PointStruct(
        id=str(uuid.uuid4()),  # IMPORTANT → always string
        vector=vector,
        # in the below payload sometimes not all the fields are there because for example in the case of a transfer we have the receiver_name and receiver_phone but in the case of a topup we don't have these fields, and in the case of a conversion we have from_currency, to_currency, amount_from, amount_to but in the case of a transfer we don't have these fields, so we will just use the get method to get the values of these fields and if they are not there we will use None as the default value.
        # this won't cause an error since .get() will return None if the key is not found in the dictionart.
        payload={
            "event_id": str(transaction["id"]),
            "user_id": transaction["user_id"],
            "user_name": transaction.get("user_name"),
            "phone_number": transaction.get("phone_number"),

            "event_type": transaction["type"],

            # -------- Common --------
            "created_at": transaction["created_at"],
            "text": text,

            # -------- Transfer --------
            "receiver_name": transaction.get("receiver_name"),
            "receiver_phone": transaction.get("receiver_phone"),

            # -------- Conversion --------
            "from_currency": transaction.get("from_currency"),
            "to_currency": transaction.get("to_currency"),
            "amount_from": transaction.get("amount_from"),
            "amount_to": transaction.get("amount_to"),

            # -------- General --------
            "amount": transaction.get("amount"),
            "currency": transaction.get("currency"),
        },
    )

    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=[point],
    )
