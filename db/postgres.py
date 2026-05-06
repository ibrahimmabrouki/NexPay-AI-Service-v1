import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("POSTGRES_URL")

# engine is an object that represents the connection to the database.
# create_engine is a function from SQLAlchemy that creates an engine object based on the provided database URL. This engine will be used to interact with the PostgreSQL database.
engine = create_engine(DATABASE_URL)

# SessionLocal is a class that will be used to create sessions for interacting with the database. A session is a temporary connection to the database that allows us to execute queries and manage transactions.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
