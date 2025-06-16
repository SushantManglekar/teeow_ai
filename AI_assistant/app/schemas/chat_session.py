# Pydantic schema for chat_sessions
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum


class SessionType(str, Enum):
    chat = "chat"
    form = "form"
    wizard = "wizard"

class ChatSessionCreate(BaseModel):
    user_id: UUID
    session_type: SessionType

class ChatSessionOut(ChatSessionCreate):
    id: UUID
    started_at:Optional[datetime]
    ended_at: Optional[datetime]
