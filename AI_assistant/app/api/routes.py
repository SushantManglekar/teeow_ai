# API route definitions
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.chat_session import ChatSessionCreate, ChatSessionOut
from app.schemas.message import MessageCreate, MessageOut
from app.models.chat_session import ChatSession
from app.models.message import Message
from app.crud import chat_session, message
from app.db.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

router = APIRouter()


# Creat chat session
@router.post("/chat_sessions", response_model=ChatSessionOut)
async def create_chat(session_in: ChatSessionCreate, db: AsyncSession = Depends(get_db)):
    db_session = ChatSession(**session_in.model_dump())
    return await chat_session.create_chat_session(db, db_session)

# READ - get by ID
@router.get("/chat_sessions/{session_id}", response_model=ChatSessionOut)
async def read_chat(session_id: UUID, db: AsyncSession = Depends(get_db)):
    session = await chat_session.get_chat_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session

# READ - list all (with optional pagination)
@router.get("/chat_sessions", response_model=List[ChatSessionOut])
async def list_chats(limit: int = 100, offset: int = 0, db: AsyncSession = Depends(get_db)):
    sessions = await chat_session.get_all_chat_sessions(db, limit=limit, offset=offset)
    return sessions

# UPDATE
@router.put("/chat_sessions/{session_id}", response_model=ChatSessionOut)
async def update_chat(session_id: UUID, session_update: ChatSessionCreate, db: AsyncSession = Depends(get_db)):
    updated_session = await chat_session.update_chat_session(db, session_id, session_update.model_dump(exclude_unset=True))
    if not updated_session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return updated_session

# DELETE
@router.delete("/chat_sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(session_id: UUID, db: AsyncSession = Depends(get_db)):
    success = await chat_session.delete_chat_session(db, session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return None


# Create Message
@router.post("/chat_sessions/{session_id}/messages", response_model=MessageOut)
async def create_msg(session_id: UUID, msg_in: MessageCreate, db: AsyncSession = Depends(get_db)):
    db_msg = Message(**msg_in.model_dump(), session_id=session_id)
    return await message.create_message(db, db_msg)

@router.get("/chat_sessions/{session_id}/messages/{message_id}", response_model=MessageOut)
async def get_msg(session_id: UUID, message_id: UUID, db: AsyncSession = Depends(get_db)):
    db_msg = await message.get_message(db, message_id)
    if not db_msg or db_msg.session_id != session_id:
        raise HTTPException(status_code=404, detail="Message not found in this session")
    return db_msg

@router.get("/chat_sessions/{session_id}/messages", response_model=List[MessageOut])
async def get_messages_for_session(session_id: UUID, db: AsyncSession = Depends(get_db)):
    return await message.get_messages_for_session(db, session_id)

@router.put("/chat_sessions/{session_id}/messages/{message_id}", response_model=MessageOut)
async def update_msg(session_id: UUID, message_id: UUID, msg_in: MessageCreate, db: AsyncSession = Depends(get_db)):
    db_msg = await message.get_message(db, message_id)
    if not db_msg or db_msg.session_id != session_id:
        raise HTTPException(status_code=404, detail="Message not found in this session")

    updated_msg = await message.update_message(db, message_id, msg_in.model_dump(exclude_unset=True))
    return updated_msg

@router.delete("/chat_sessions/{session_id}/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_msg(session_id: UUID, message_id: UUID, db: AsyncSession = Depends(get_db)):
    db_msg = await message.get_message(db, message_id)
    if not db_msg or db_msg.session_id != session_id:
        raise HTTPException(status_code=404, detail="Message not found in this session")

    deleted = await message.delete_message(db, message_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Message not found")