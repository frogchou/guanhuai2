from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.db import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[Optional[str]] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    personas: Mapped[list["Persona"]] = relationship(back_populates="creator")
    conversations: Mapped[list["Conversation"]] = relationship(back_populates="user")


class Persona(Base):
    __tablename__ = "personas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    name: Mapped[str] = mapped_column(String(100))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(255))
    relationship: Mapped[str] = mapped_column(String(50)) # e.g. "Mother", "Friend"
    user_called_by: Mapped[str] = mapped_column(String(50)) # How persona calls user e.g. "Sweetie"
    persona_called_by: Mapped[str] = mapped_column(String(50)) # How user calls persona e.g. "Mom"
    
    # Voice Profile
    voice_sample_url: Mapped[Optional[str]] = mapped_column(String(255))
    voice_id: Mapped[Optional[str]] = mapped_column(String(100)) # ID from IndexTTS
    voice_model_status: Mapped[str] = mapped_column(String(20), default="pending") # pending, ready, failed
    
    # Compliance
    legal_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    creator: Mapped["User"] = relationship(back_populates="personas")
    conversations: Mapped[list["Conversation"]] = relationship(back_populates="persona")


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    persona_id: Mapped[int] = mapped_column(ForeignKey("personas.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    user: Mapped["User"] = relationship(back_populates="conversations")
    persona: Mapped["Persona"] = relationship(back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"))
    
    role: Mapped[str] = mapped_column(String(20)) # user, assistant
    content_text: Mapped[Optional[str]] = mapped_column(Text)
    audio_url: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Analysis / Metadata
    analysis: Mapped[Optional[dict]] = mapped_column(JSON) # {"emotion": "happy", "intent": "greeting"}
    
    # Processing Status
    status: Mapped[str] = mapped_column(String(20), default="completed") # pending, processing, completed, failed
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
