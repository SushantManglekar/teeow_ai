# app/models/user.py

import uuid
from sqlalchemy import Column, String, Enum
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from enum import Enum as PyEnum


class TierEnum(PyEnum):
    FREE = "basic"
    PRO = "pro"
    PREMIUM = "premium"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, unique=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    tier = Column(Enum(TierEnum, name="tier_enum"), default=TierEnum.FREE, nullable=False)
