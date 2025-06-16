from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from app.models.chat_session import ChatSession
from datetime import datetime
from uuid import UUID

# CREATE
async def create_chat_session(db: AsyncSession, session: ChatSession) -> ChatSession:
    if not session.started_at:
        session.started_at = datetime.utcnow()
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session

# READ - get one by ID
async def get_chat_session(db: AsyncSession, session_id) -> Optional[ChatSession]:
    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    return result.scalar_one_or_none()

# READ - get all
async def get_all_chat_sessions(db: AsyncSession, limit: int = 100, offset: int = 0) -> List[ChatSession]:
    result = await db.execute(
        select(ChatSession).offset(offset).limit(limit)
    )
    return result.scalars().all()

# UPDATE
async def update_chat_session(db: AsyncSession, session_id: UUID, update_data: dict) -> Optional[ChatSession]:
    await db.execute(
        update(ChatSession)
        .where(ChatSession.id == session_id)
        .values(**update_data)
    )
    await db.commit()
    # Re-fetch updated session
    return await get_chat_session(db, session_id)

# DELETE
async def delete_chat_session(db: AsyncSession, session_id) -> bool:
    result = await db.execute(
        delete(ChatSession).where(ChatSession.id == session_id)
    )
    await db.commit()
    return result.rowcount > 0
