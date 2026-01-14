from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.db import get_db
from app.models.all_models import User, Persona
from app.schemas.all_schemas import PersonaCreate, PersonaResponse
from app.core.security import settings
from app.services.tts_service import get_tts_provider
from typing import Annotated
from app.api.v1.deps import get_current_user
import shutil
import os
import uuid

router = APIRouter()

@router.get("/", response_model=list[PersonaResponse])
async def get_personas(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Persona).where(Persona.creator_id == current_user.id))
    return result.scalars().all()

@router.post("/", response_model=PersonaResponse)
async def create_persona(
    persona_in: PersonaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not persona_in.legal_confirmed:
        raise HTTPException(status_code=400, detail="You must confirm you have the rights to clone this voice.")
    
    new_persona = Persona(
        **persona_in.model_dump(),
        creator_id=current_user.id
    )
    db.add(new_persona)
    await db.commit()
    await db.refresh(new_persona)
    return new_persona

@router.post("/{persona_id}/voice", response_model=PersonaResponse)
async def upload_voice_sample(
    persona_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify ownership
    result = await db.execute(select(Persona).where(Persona.id == persona_id, Persona.creator_id == current_user.id))
    persona = result.scalar_one_or_none()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    # Save file locally first (for UI playback if needed)
    os.makedirs("static/audio", exist_ok=True)
    file_ext = file.filename.split(".")[-1]
    filename = f"voice_sample_{persona.id}_{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join("static/audio", filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    persona.voice_sample_url = f"/static/audio/{filename}"
    persona.voice_model_status = "processing"
    await db.commit()
    
    try:
        # Upload to TTS Service
        tts_provider = get_tts_provider()
        # This now returns the absolute path on the TTS server
        absolute_path = await tts_provider.clone_voice(file_path, persona.name)
        
        persona.voice_file_path = absolute_path
        persona.voice_id = absolute_path # Use absolute path as voice_id
        persona.voice_model_status = "ready"
    except Exception as e:
        persona.voice_model_status = "failed"
        # We still keep the local file
        print(f"TTS Upload Failed: {e}")
        
    await db.commit()
    await db.refresh(persona)
    
    return persona

@router.post("/{persona_id}/avatar", response_model=PersonaResponse)
async def upload_avatar(
    persona_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify ownership
    result = await db.execute(select(Persona).where(Persona.id == persona_id, Persona.creator_id == current_user.id))
    persona = result.scalar_one_or_none()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    # Save file
    os.makedirs("static/images", exist_ok=True)
    file_ext = file.filename.split(".")[-1]
    if file_ext.lower() not in ['jpg', 'jpeg', 'png', 'webp']:
        raise HTTPException(status_code=400, detail="Invalid image format")
        
    filename = f"avatar_{persona.id}_{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join("static/images", filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    persona.avatar_url = f"/static/images/{filename}"
    await db.commit()
    await db.refresh(persona)
    
    return persona
