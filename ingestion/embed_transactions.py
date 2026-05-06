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
    user_name = transaction.get("user_name", "a user")
    phone_number = transaction.get("phone_number", "unknown number")
    tx_type = transaction.get("type")
    created_at = transaction.get("created_at")

    user_identity = f"{user_name} (phone: {phone_number})"

    if tx_type == "TRANSFER":
        # here we need the mapping between the user_id and the name of the user in order to get the name of the receiver of the transaction, but for now we will just use a placeholder for the receiver.
        receiver_name = transaction.get("receiver_name", "another user")
        receiver_phone = transaction.get("receiver_phone", "unknown")

        receiver_identity = f"{receiver_name} (phone: {receiver_phone})"

        return (
            f"{user_identity} sent {transaction['amount']} "
            f"{transaction['currency']} to {receiver_identity} "
            f"on {created_at}"
        )

    # if tx_type == "TRANSFER_IN":
    #     # here we need the mapping between the user_id and the name of the user in order to get the name of the sender of the transaction, but for now we will just use a placeholder for the sender.
    #     sender = transaction.get("sender", "another user")
    #     return f"{user_identity} received {amount} {currency} from {sender} on {created_at}"

    # if tx_type == "STRIPE_TOPUP":
    #     return f"{user_identity} topped up {amount} {currency} using Stripe on {created_at}"

    if tx_type == "TOPUP":
        return (
            f"{user_identity} topped up {transaction['amount']} "
            f"{transaction['currency']} using Stripe "
            f"on {created_at}"
        )

    if tx_type == "CONVERSION":
        return (
            f"{user_identity} converted {transaction['amount_from']} "
            f"{transaction['from_currency']} to "
            f"{transaction['amount_to']} {transaction['to_currency']} "
            f"on {created_at}"
        )

    return f"{user_identity} performed a transaction on {created_at}"


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
