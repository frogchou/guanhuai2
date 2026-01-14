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
        self.base_url = settings.INDEXTTS_BASE_URL.rstrip('/')
        self.client = httpx.AsyncClient(timeout=120.0)

    async def clone_voice(self, audio_path: str, name: str) -> str:
        """
        Uploads an audio file to the TTS server and returns its absolute path.
        """
        upload_url = f"{self.base_url}/upload_audio"
        try:
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")

            with open(audio_path, 'rb') as f:
                # Use the correct key 'file' as per docs
                files = {'file': (os.path.basename(audio_path), f, 'audio/wav')}
                logger.info(f"IndexTTS: Uploading {audio_path} to {upload_url}")
                
                response = await self.client.post(upload_url, files=files)
            
            response.raise_for_status()
            data = response.json()
            
            absolute_path = data.get("absolute_path")
            if not absolute_path:
                raise ValueError(f"No 'absolute_path' in response: {data}")
                
            logger.info(f"IndexTTS: Upload success, server path: {absolute_path}")
            return absolute_path
            
        except Exception as e:
            logger.error(f"IndexTTS Upload Error: {e}")
            raise

    async def generate_audio(self, text: str, voice_id: str, output_path: str) -> bool:
        """
        Generates audio using the TTS server.
        voice_id: Should be the absolute_path returned by clone_voice (upload_audio)
        """
        tts_url = f"{self.base_url}/tts"
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            payload = {
                "text": text,
                "prompt_audio_path": voice_id, # The absolute path on the server
                "emotion": {
                    "mode": 0 # Default: same emotion as prompt audio
                },
                # Advanced defaults
                "max_text_tokens": 120,
                "temperature": 0.7,
                "top_p": 0.7,
                "top_k": 20
            }
            
            logger.info(f"IndexTTS: POST {tts_url} | Voice: {voice_id} | Text: {text[:20]}...")
            response = await self.client.post(tts_url, json=payload)
            
            if response.status_code != 200:
                logger.error(f"IndexTTS Gen Error ({response.status_code}): {response.text}")
                generate_silent_wav(output_path)
                return False
                
            # Verify we got audio content
            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type:
                logger.error(f"IndexTTS returned JSON error: {response.text}")
                generate_silent_wav(output_path)
                return False

            with open(output_path, "wb") as f:
                f.write(response.content)
            
            logger.info(f"IndexTTS: Audio saved to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"IndexTTS Gen Exception: {e}")
            generate_silent_wav(output_path)
            return False

def get_tts_provider() -> TTSProvider:
    if "mock" in settings.INDEXTTS_BASE_URL:
        return MockTTSProvider()
    return IndexTTSClient()
