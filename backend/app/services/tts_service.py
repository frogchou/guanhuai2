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
        # Implements upload to IndexTTS to get absolute server path
        try:
            # We need to open the file again
            with open(audio_path, 'rb') as f:
                files = {'file': f}
                # Use /upload_audio endpoint as per docs
                response = await self.client.post(f"{self.base_url}/upload_audio", files=files)
            
            response.raise_for_status()
            data = response.json()
            return data.get("absolute_path", "")
        except Exception as e:
            logger.error(f"IndexTTS Upload Error: {e}")
            # In case of error, we might return empty or raise
            raise e

    async def generate_audio(self, text: str, voice_id: str, output_path: str) -> bool:
        try:
            # voice_id here is expected to be the absolute_path
            payload = {
                "text": text, 
                "prompt_audio_path": voice_id,
                "emotion": {"mode": 0}
            }
            response = await self.client.post(f"{self.base_url}/tts", json=payload, timeout=60.0)
            
            if response.status_code != 200:
                logger.error(f"IndexTTS Gen Error: {response.text}")
                generate_silent_wav(output_path)
                return False
                
            with open(output_path, "wb") as f:
                f.write(response.content)
            return True
        except Exception as e:
            logger.error(f"IndexTTS Gen Error: {e}")
            # Fallback to mock for stability
            generate_silent_wav(output_path)
            return False

def get_tts_provider() -> TTSProvider:
    if "mock" in settings.INDEXTTS_BASE_URL:
        return MockTTSProvider()
    return IndexTTSClient()
