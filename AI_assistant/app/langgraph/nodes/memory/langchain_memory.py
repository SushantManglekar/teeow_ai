from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
from langchain.memory import ConversationBufferMemory

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
from uuid import UUID

from app.models.message import Message
import logging

logger = logging.getLogger("ai_assistant")


class Memory:
    def __init__(self, session_id: UUID, db: AsyncSession):
        self.session_id = session_id
        self.db = db
        logger.debug(f"Initialized Memory for session_id: {session_id}")

    async def get_memory(self) -> ConversationBufferMemory:
        logger.debug(f"Creating ConversationBufferMemory for session_id: {self.session_id}")

        class _ChatHistory(BaseChatMessageHistory):
            def __init__(self, session_id: UUID, db: AsyncSession):
                self.session_id = session_id
                self.db = db
                self.messages: List = []
                self.limit: int = 10
                logger.debug(f"ChatHistory initialized for session_id: {session_id} with limit={self.limit}")

            async def load_messages(self) -> List:
                logger.debug(f"Loading last {self.limit} messages from DB for session_id: {self.session_id}")
                try:
                    result = await self.db.execute(
                        select(Message)
                        .where(Message.session_id == self.session_id)
                        .order_by(desc(Message.timestamp))
                        .limit(self.limit)
                    )
                    rows = result.scalars().all()
                    logger.info(f"Fetched {len(rows)} messages from DB for session_id: {self.session_id}")
                except Exception as e:
                    logger.exception(f"Failed to load messages for session_id: {self.session_id}")
                    rows = []

                self.messages = []

                for msg in reversed(rows):  # Ensure chronological order
                    if msg.sender == "user":
                        self.messages.append(HumanMessage(content=msg.message))
                        logger.debug(f"Loaded HumanMessage: {msg.message}")
                    elif msg.sender == "ai":
                        self.messages.append(AIMessage(content=msg.message))
                        logger.debug(f"Loaded AIMessage: {msg.message}")
                    else:
                        logger.warning(f"Unknown sender type: {msg.sender} for message ID: {msg.id}")

            def clear(self) -> None:
                logger.debug(f"Clearing in-memory chat history for session_id: {self.session_id}")
                self.messages = []

        # Create and load custom chat history
        chat_history = _ChatHistory(self.session_id, self.db)
        await chat_history.load_messages()

        logger.info(f"Returning ConversationBufferMemory for session_id: {self.session_id}")
        return ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            chat_memory=chat_history,
            input_key="user_query"
        )
