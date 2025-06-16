from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.message import Message
from sqlalchemy import update, delete
from datetime import datetime

async def create_message(db: AsyncSession, message: Message):
    if not message.timestamp:
        message.timestamp = datetime.utcnow()
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message

async def get_message(db: AsyncSession, message_id):
    result = await db.execute(select(Message).where(Message.id == message_id))
    return result.scalar_one_or_none()

async def get_messages_for_session(db: AsyncSession, session_id):
    result = await db.execute(select(Message).where(Message.session_id == session_id))
    return result.scalars().all()

async def update_message(db: AsyncSession, message_id, updated_fields: dict):
    # Use the SQLAlchemy core update construct for async update
    query = (
        update(Message)
        .where(Message.id == message_id)
        .values(**updated_fields)
        .execution_options(synchronize_session="fetch")
    )
    await db.execute(query)
    await db.commit()
    return await get_message(db, message_id)

async def delete_message(db: AsyncSession, message_id):
    query = delete(Message).where(Message.id == message_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0  # True if something was deleted
