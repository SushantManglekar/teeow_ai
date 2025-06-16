# app/models/message.py
import uuid
from datetime import datetime
from sqlalchemy import Column, Text, String, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

# important: this import makes sure chat_sessions is in the metadata
from app.models.chat_session import ChatSession  

class Message(Base):
    __tablename__ = "messages"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id  = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=False)
    sender      = Column(String, nullable=False)  # ENUM: user, ai
    message     = Column(Text, nullable=False)
    timestamp   = Column(TIMESTAMP, default=datetime.utcnow)

    response_to = Column(UUID(as_uuid=True), ForeignKey("messages.id"), nullable=True)

    # Relationships
    session     = relationship("ChatSession", back_populates="messages")
    replied_to  = relationship("Message", remote_side=[id], backref="replies")
