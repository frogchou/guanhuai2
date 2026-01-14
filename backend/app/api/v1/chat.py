import os
import uuid
import shutil
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.db import get_db
from app.models.all_models import User, Persona, Conversation, Message
from app.schemas.all_schemas import MessageResponse, ChatResponse
from app.api.v1.deps import get_current_user
from app.services.llm_service import get_llm_provider
from app.services.stt_service import get_stt_provider
from app.services.tts_service import get_tts_provider

router = APIRouter()
logger = logging.getLogger(__name__)

async def process_voice_message(
    conversation_id: int, 
    user_msg_id: int, 
    audio_path: str, 
    db_session_factory
):
    """
    Background task to handle: STT -> LLM -> TTS
    """
    # Create a new session for the background task
    async with db_session_factory() as db:
        try:
            # 1. Load Context
            stmt = select(Conversation).where(Conversation.id == conversation_id)
            result = await db.execute(stmt)
            conversation = result.scalar_one()
            
            # Load Persona details eagerly
            stmt_p = select(Persona).where(Persona.id == conversation.persona_id)
            res_p = await db.execute(stmt_p)
            persona = res_p.scalar_one()

            # 2. STT
            stt = get_stt_provider()
            transcription = await stt.transcribe(audio_path)
            
            # Update user message with text
            stmt_m = select(Message).where(Message.id == user_msg_id)
            res_m = await db.execute(stmt_m)
            user_msg = res_m.scalar_one()
            user_msg.content_text = transcription
            await db.commit()

            # 3. LLM
            # Build Prompt
            system_prompt = f"""
            You are roleplaying as {persona.name}.
            Your relationship to the user: {persona.relationship}.
            The user calls you: {persona.persona_called_by}.
            You call the user: {persona.user_called_by}.
            
            Analyze the user's input for emotion and intent.
            Reply in JSON format:
            {{
                "tone": "emotion_label",
                "content": "your_reply_text"
            }}
            Keep the reply conversational and concise.
            """
            
            llm = get_llm_provider()
            llm_result = await llm.generate_response(system_prompt, transcription)
            
            reply_text = llm_result.get("content", "I didn't catch that.")
            reply_tone = llm_result.get("tone", "neutral")

            # 4. Create Assistant Message (Pending Audio)
            asst_msg = Message(
                conversation_id=conversation_id,
                role="assistant",
                content_text=reply_text,
                analysis={"tone": reply_tone},
                status="processing"
            )
            db.add(asst_msg)
            await db.commit()
            await db.refresh(asst_msg)

            # 5. TTS
            tts = get_tts_provider()
            output_filename = f"reply_{asst_msg.id}_{uuid.uuid4()}.wav"
            output_path = os.path.join("static/audio", output_filename)
            
            # Use voice_file_path if available (absolute path for IndexTTS), otherwise fallback
            voice_ref = persona.voice_file_path if persona.voice_file_path else (persona.voice_id or "default")
            
            success = await tts.generate_audio(
                text=reply_text, 
                voice_id=voice_ref, 
                output_path=output_path
            )
            
            if success:
                asst_msg.audio_url = f"/static/audio/{output_filename}"
                asst_msg.status = "completed"
            else:
                asst_msg.status = "failed"
            
            await db.commit()
            
        except Exception as e:
            logger.error(f"Background task failed: {e}")
            # Update status to failed if possible
            pass

@router.get("/conversations", response_model=list)
async def get_conversations(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Simplify: return list of personas that have conversations
    # In a real app, we'd group by conversation
    return []

@router.get("/conversations/{persona_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    persona_id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user),
    limit: int = 50
):
    # Find or create conversation
    result = await db.execute(
        select(Conversation).where(
            Conversation.user_id == current_user.id, 
            Conversation.persona_id == persona_id
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        conversation = Conversation(user_id=current_user.id, persona_id=persona_id)
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        return []
        
    stmt = select(Message).where(Message.conversation_id == conversation.id).order_by(Message.created_at.desc()).limit(limit)
    res = await db.execute(stmt)
    msgs = res.scalars().all()
    return list(reversed(msgs)) # Return oldest first for chat view

@router.post("/conversations/{persona_id}/send", response_model=MessageResponse)
async def send_voice_message(
    persona_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Get Conversation
    result = await db.execute(
        select(Conversation).where(
            Conversation.user_id == current_user.id, 
            Conversation.persona_id == persona_id
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        conversation = Conversation(user_id=current_user.id, persona_id=persona_id)
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

    # 2. Save User Audio
    file_ext = file.filename.split(".")[-1]
    filename = f"msg_{conversation.id}_{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join("static/audio", filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 3. Create User Message Record
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        audio_url=f"/static/audio/{filename}",
        status="completed" # User audio is uploaded, so it's done
    )
    db.add(user_msg)
    await db.commit()
    await db.refresh(user_msg)
    
    # 4. Trigger Background Processing
    from app.core.db import AsyncSessionLocal
    background_tasks.add_task(
        process_voice_message, 
        conversation.id, 
        user_msg.id, 
        file_path,
        AsyncSessionLocal
    )
    
    return user_msg
