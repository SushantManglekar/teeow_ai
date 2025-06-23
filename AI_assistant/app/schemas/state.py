from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional, Any, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession

class ChatFlowState(BaseModel):
    session_id: UUID
    user_query: str
    db: AsyncSession

    # Intent detection output
    intent: Optional[str] = None
    sub_intent: Optional[str] = None
    intent_object: Optional[Dict] = None

    # Prompt building inputs
    user_location: Optional[str] = None
    current_time: Optional[str] = None
    user_preferences: Optional[str] = None
    realtime_info: Optional[str] = None
    chat_history_summary: Optional[str] = None

    # Prompt output
    prompt: Optional[List[Any]] = None  # LangChain Message types

    # LLM response
    response: Optional[Dict] = None

    # LangChain memory or tools
    chat_memory: Optional[Any] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)
