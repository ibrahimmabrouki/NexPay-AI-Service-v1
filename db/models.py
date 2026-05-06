from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# ----------------------------
# USERS
# ----------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    full_name = Column(String)
    phone_number = Column(String)


# ----------------------------
# LEDGER TRANSACTIONS
# ----------------------------
class LedgerTransaction(Base):
    __tablename__ = "ledger_transactions"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    type = Column(String)
    amount = Column(Integer)
    currency = Column(String)

    reference_id = Column(String)
    reference_type = Column(String)

    created_at = Column(DateTime)
    embedded = Column(Boolean, default=False)

    user = relationship("User")


# ----------------------------
# TRANSFERS
# ----------------------------
class Transfer(Base):
    __tablename__ = "transfers"

    id = Column(String, primary_key=True)

    sender_id = Column(String, ForeignKey("users.id"))
    receiver_id = Column(String, ForeignKey("users.id"))

    amount = Column(Integer)
    currency = Column(String)

    created_at = Column(DateTime)

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])


# ----------------------------
# CURRENCY CONVERSIONS
# ----------------------------
class CurrencyConversion(Base):
    __tablename__ = "currency_conversions"

    id = Column(String, primary_key=True)

    user_id = Column(String, ForeignKey("users.id"))

    from_currency = Column(String)
    to_currency = Column(String)

    amount_from = Column(Integer)
    amount_to = Column(Integer)

    created_at = Column(DateTime)

    user = relationship("User")


# ----------------------------
# STRIPE TOPUPS
# ----------------------------
class StripeTopup(Base):
    __tablename__ = "stripe_topups"

    id = Column(String, primary_key=True)

    user_id = Column(String, ForeignKey("users.id"))

    amount = Column(Integer)
    currency = Column(String)

    created_at = Column(DateTime)

    user = relationship("User")