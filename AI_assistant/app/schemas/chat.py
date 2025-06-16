from pydantic import BaseModel
from uuid import UUID
from typing import List,Dict
from enum import Enum


class ChatRequest(BaseModel):
    user_query: str
    chat_session_id: UUID


class ChatResponse(BaseModel):
    answer: Dict

