from pydantic import BaseModel


class MemoryRequest(BaseModel):
    messages: list[dict]
