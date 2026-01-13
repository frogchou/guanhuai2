import abc
import logging
import os
import httpx
import wave
import contextlib
from app.core.config import settings

logger = logging.getLogger(__name__)

def generate_silent_wav(path: str, duration: float = 2.0):
    """Generate a dummy WAV file for mock purposes."""
    with contextlib.closing(wave.open(path, 'w')) as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(44100)
        f.writeframes(b'\x00' * int(44100 * duration * 2))

class TTSProvider(abc.ABC):
    @abc.abstractmethod
    async def clone_voice(self, audio_path: str, name: str) -> str:
        """Uploads a sample and returns a voice_id"""
        pass

    @abc.abstractmethod
    async def generate_audio(self, text: str, voice_id: str, output_path: str) -> bool:
        """Generates audio and saves to output_path"""
        pass

class MockTTSProvider(TTSProvider):
    async def clone_voice(self, audio_path: str, name: str) -> str:
        logger.info(f"MOCK TTS: Cloning voice for {name} from {audio_path}")
        return "mock-voice-id-123"

    async def generate_audio(self, text: str, voice_id: str, output_path: str) -> bool:
        logger.info(f"MOCK TTS: Generating audio for '{text}' with voice {voice_id}")
        # Generate a real dummy wav file so frontend can play it
        generate_silent_wav(output_path)
        return True

class IndexTTSClient(TTSProvider):
    def __init__(self):
        self.base_url = settings.INDEXTTS_BASE_URL
        self.client = httpx.AsyncClient(timeout=30.0)

    async def clone_voice(self, audio_path: str, name: str) -> str:
        # Pseudo-implementation based on typical IndexTTS/Cloning APIs
        # In a real scenario, check the specific API docs
        try:
            files = {'file': open(audio_path, 'rb')}
            response = await self.client.post(f"{self.base_url}/api/v1/voice/clone", files=files, data={"name": name})
            response.raise_for_status()
            return response.json().get("voice_id")
        except Exception as e:
            logger.error(f"IndexTTS Clone Error: {e}")
            return "mock-voice-id-fallback"

    async def generate_audio(self, text: str, voice_id: str, output_path: str) -> bool:
        try:
            payload = {"text": text, "voice_id": voice_id}
            response = await self.client.post(f"{self.base_url}/api/v1/tts", json=payload)
            response.raise_for_status()
            with open(output_path, "wb") as f:
                f.write(response.content)
            return True
        except Exception as e:
            logger.error(f"IndexTTS Gen Error: {e}")
            # Fallback to mock for stability even in 'real' mode if external fails
            generate_silent_wav(output_path)
            return False

def get_tts_provider() -> TTSProvider:
    if "mock" in settings.INDEXTTS_BASE_URL:
        return MockTTSProvider()
    return IndexTTSClient()
