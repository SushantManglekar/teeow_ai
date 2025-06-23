from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List

class ChatRequest(BaseModel):
    user_query: str
    chat_session_id: UUID

class Suggestion(BaseModel):
    title: str
    location: str
    details: str
    link: Optional[str] = None

class ChatResponseSchema(BaseModel):
    answer: str
    follow_up: Optional[str] = None
    suggestions: List[Suggestion] = []