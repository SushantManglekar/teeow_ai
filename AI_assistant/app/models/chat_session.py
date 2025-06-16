# app/models/chat_session.py
import uuid
from datetime import datetime
from sqlalchemy import Column, Enum, TIMESTAMP, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from app.models.user import User
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id      = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_type = Column(String, nullable=False)
    started_at   = Column(TIMESTAMP, default=datetime.utcnow)
    ended_at     = Column(TIMESTAMP, nullable=True)

    # ensure the Message model can refer back
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
