# Pydantic schema for messages
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from enum import Enum
from typing import Optional

class SenderType(str, Enum):
    user = "user"
    assistant = "ai"

class MessageCreate(BaseModel):
    sender: SenderType
    message: str
    response_to: Optional[UUID] = None

class MessageOut(MessageCreate):
    id: UUID
    response_to: Optional[UUID]
