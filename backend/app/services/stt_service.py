import abc
import shutil
import os
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class STTProvider(abc.ABC):
    @abc.abstractmethod
    async def transcribe(self, audio_path: str) -> str:
        pass

class MockSTTProvider(STTProvider):
    async def transcribe(self, audio_path: str) -> str:
        logger.info(f"MOCK STT: Transcribing {audio_path}")
        return "This is a simulated transcription of your voice message."

class OpenAIWhisperProvider(STTProvider):
    def __init__(self):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def transcribe(self, audio_path: str) -> str:
        try:
            with open(audio_path, "rb") as audio_file:
                transcript = await self.client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
            return transcript.text
        except Exception as e:
            logger.error(f"Whisper Error: {e}")
            return "Error transcribing audio."

def get_stt_provider() -> STTProvider:
    if settings.OPENAI_API_KEY == "mock":
        return MockSTTProvider()
    return OpenAIWhisperProvider()
