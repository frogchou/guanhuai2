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
        import httpx
        
        http_client = httpx.AsyncClient(proxy=settings.OPENAI_PROXY) if settings.OPENAI_PROXY else None

        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            http_client=http_client
        )

    async def transcribe(self, audio_path: str) -> str:
        try:
            size = os.path.getsize(audio_path) if os.path.exists(audio_path) else 0
            logger.info(f"Whisper: Transcribing file {audio_path} (size={size} bytes)")
            with open(audio_path, "rb") as audio_file:
                transcript = await self.client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
            return transcript.text
        except Exception as e:
            logger.error(f"Whisper Error: {e} | path={audio_path}")
            return "Error transcribing audio."

def get_stt_provider() -> STTProvider:
    api_key = settings.OPENAI_API_KEY
    if not api_key or api_key == "mock":
        logger.info("STT Provider: Mock")
        return MockSTTProvider()
    logger.info("STT Provider: OpenAI Whisper")
    return OpenAIWhisperProvider()
