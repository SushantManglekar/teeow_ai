from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.message import Message
from sqlalchemy import update, delete
from datetime import datetime
import logging

logger = logging.getLogger("ai_assistant")

async def create_message(db: AsyncSession, message: Message):
    if not message.timestamp:
        message.timestamp = datetime.utcnow()
    logger.debug(f"Creating message: content={message.message}, role={message.sender}, session_id={message.session_id}")
    db.add(message)
    await db.commit()
    await db.refresh(message)
    logger.info(f"Message created with ID: {message.id}")
    return message

async def get_message(db: AsyncSession, message_id):
    logger.debug(f"Fetching message with ID: {message_id}")
    result = await db.execute(select(Message).where(Message.id == message_id))
    message = result.scalar_one_or_none()
    if message:
        logger.info(f"Message fetched with ID: {message_id}")
    else:
        logger.warning(f"No message found with ID: {message_id}")
    return message

async def get_messages_for_session(db: AsyncSession, session_id):
    logger.debug(f"Fetching messages for session ID: {session_id}")
    result = await db.execute(select(Message).where(Message.session_id == session_id))
    messages = result.scalars().all()
    logger.info(f"Fetched {len(messages)} messages for session ID: {session_id}")
    return messages

async def update_message(db: AsyncSession, message_id, updated_fields: dict):
    logger.debug(f"Updating message ID {message_id} with fields: {updated_fields}")
    query = (
        update(Message)
        .where(Message.id == message_id)
        .values(**updated_fields)
        .execution_options(synchronize_session="fetch")
    )
    result = await db.execute(query)
    await db.commit()
    if result.rowcount:
        logger.info(f"Message ID {message_id} updated successfully")
    else:
        logger.warning(f"Message ID {message_id} update failed or no changes")
    return await get_message(db, message_id)

async def delete_message(db: AsyncSession, message_id):
    logger.debug(f"Attempting to delete message ID: {message_id}")
    query = delete(Message).where(Message.id == message_id)
    result = await db.execute(query)
    await db.commit()
    if result.rowcount > 0:
        logger.info(f"Message ID {message_id} deleted successfully")
        return True
    else:
        logger.warning(f"Message ID {message_id} not found or already deleted")
        return False
