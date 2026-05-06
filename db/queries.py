from db.postgres import SessionLocal
from db.models import LedgerTransaction, User, Transfer, CurrencyConversion, StripeTopup
from ingestion.embed_transactions import upsert_transaction


def get_unembedded_transactions(limit: int = 100):
    db = SessionLocal()
    try:
        return (
            db.query(LedgerTransaction, User)
            .join(User, LedgerTransaction.user_id == User.id)
            .filter(LedgerTransaction.embedded == False)
            .limit(limit)
            .all()
        )
    finally:
        db.close()


def mark_as_embedded(transaction_id: str):
    db = SessionLocal()
    try:
        tx = db.query(LedgerTransaction).filter(
            LedgerTransaction.id == transaction_id
        ).first()

        if tx:
            tx.embedded = True
            db.commit()
    finally:
        db.close()



# BUILDERS PER TYPE

def build_transfer_dict(db, tx, user):
    transfer = db.query(Transfer).filter(
        Transfer.id == tx.reference_id
    ).first()

    if not transfer:
        return None

    receiver = db.query(User).filter(User.id == transfer.receiver_id).first()

    return {
        "id": str(transfer.id),  # IMPORTANT: use transfer id (dedup)
        "user_id": tx.user_id,
        "user_name": user.full_name,
        "phone_number": user.phone_number,
        "type": "TRANSFER",
        "amount": transfer.amount,
        "currency": transfer.currency,
        "receiver_name": receiver.full_name if receiver else "unknown",
        "receiver_phone": receiver.phone_number if receiver else "unknown",
        "created_at": str(transfer.created_at),
    }


def build_conversion_dict(db, tx, user):
    conv = db.query(CurrencyConversion).filter(
        CurrencyConversion.id == tx.reference_id
    ).first()

    if not conv:
        return None

    return {
        "id": str(conv.id),  # deduplicate
        "user_id": tx.user_id,
        "user_name": user.full_name,
        "phone_number": user.phone_number,
        "type": "CONVERSION",
        "from_currency": conv.from_currency,
        "to_currency": conv.to_currency,
        "amount_from": float(conv.amount_from),
        "amount_to": float(conv.amount_to),
        "created_at": str(conv.created_at),
    }


def build_topup_dict(db, tx, user):
    topup = db.query(StripeTopup).filter(
        StripeTopup.id == tx.reference_id
    ).first()

    if not topup:
        return None

    return {
        "id": str(topup.id),
        "user_id": tx.user_id,
        "user_name": user.full_name,
        "phone_number": user.phone_number,
        "type": "TOPUP",
        "amount": float(topup.amount),
        "currency": topup.currency,
        "created_at": str(topup.created_at),
    }


# ----------------------------
# MAIN INGESTION
# ----------------------------

if __name__ == "__main__":
    db = SessionLocal()

    try:
        transactions = get_unembedded_transactions()

        processed_refs = set()  

        for tx, user in transactions:

            if tx.reference_id in processed_refs:
                continue

            processed_refs.add(tx.reference_id)

            event = None

            # ----------------------------
            # TYPE HANDLING
            # ----------------------------

            if tx.reference_type == "TRANSFER":
                event = build_transfer_dict(db, tx, user)

            elif tx.reference_type == "CONVERSION":
                event = build_conversion_dict(db, tx, user)

            elif tx.reference_type == "STRIPE":
                event = build_topup_dict(db, tx, user)

            # ----------------------------
            # PROCESS
            # ----------------------------

            if event:
                upsert_transaction(event)

                # mark ALL ledger rows with same reference as embedded
                db.query(LedgerTransaction).filter(
                    LedgerTransaction.reference_id == tx.reference_id
                ).update({"embedded": True})

                db.commit()

    finally:
        db.close()
