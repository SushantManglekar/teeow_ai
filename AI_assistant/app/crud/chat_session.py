import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from app.models.chat_session import ChatSession
from datetime import datetime
from uuid import UUID
from app.utils.setup_logger import setup_logger

logger = logging.getLogger("ai_assistant")

# CREATE
async def create_chat_session(db: AsyncSession, session: ChatSession) -> ChatSession:
    if not session.started_at:
        session.started_at = datetime.utcnow()
    db.add(session)
    await db.commit()
    await db.refresh(session)
    logger.info(f"Chat session created: {session.id}")
    return session

# READ - get one by ID
async def get_chat_session(db: AsyncSession, session_id: UUID) -> Optional[ChatSession]:
    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    session = result.scalar_one_or_none()
    if session:
        logger.info(f"Chat session fetched: {session_id}")
    else:
        logger.warning(f"Chat session not found: {session_id}")
    return session

# READ - get all
async def get_all_chat_sessions(db: AsyncSession, limit: int = 100, offset: int = 0) -> List[ChatSession]:
    result = await db.execute(
        select(ChatSession).offset(offset).limit(limit)
    )
    sessions = result.scalars().all()
    logger.info(f"Fetched {len(sessions)} chat sessions (limit={limit}, offset={offset})")
    return sessions

# UPDATE
async def update_chat_session(db: AsyncSession, session_id: UUID, update_data: dict) -> Optional[ChatSession]:
    await db.execute(
        update(ChatSession)
        .where(ChatSession.id == session_id)
        .values(**update_data)
    )
    await db.commit()
    logger.info(f"Updated chat session: {session_id} with data: {update_data}")
    return await get_chat_session(db, session_id)

# DELETE
async def delete_chat_session(db: AsyncSession, session_id: UUID) -> bool:
    result = await db.execute(
        delete(ChatSession).where(ChatSession.id == session_id)
    )
    await db.commit()
    success = result.rowcount > 0
    if success:
        logger.info(f"Deleted chat session: {session_id}")
    else:
        logger.warning(f"Tried to delete non-existent chat session: {session_id}")
    return success
