from fastapi import Header, HTTPException, Depends
import os
from dotenv import load_dotenv
load_dotenv()
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY")


def verify_internal_key(x_internal_api_key: str = Header(...)):
    if x_internal_api_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")
