from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, Dict
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Persona Schemas
class PersonaBase(BaseModel):
    name: str
    relationship: str
    user_called_by: str
    persona_called_by: str
    legal_confirmed: bool

class PersonaCreate(PersonaBase):
    pass

class PersonaResponse(PersonaBase):
    id: int
    avatar_url: Optional[str] = None
    voice_sample_url: Optional[str] = None
    voice_model_status: str
    voice_id: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Message Schemas
class MessageBase(BaseModel):
    role: str
    content_text: Optional[str] = None

class MessageResponse(MessageBase):
    id: int
    audio_url: Optional[str] = None
    analysis: Optional[Dict] = None
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ChatResponse(BaseModel):
    user_message: MessageResponse
    assistant_message: MessageResponse
