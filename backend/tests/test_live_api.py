import unittest
import os
import httpx
import wave
import contextlib
import tempfile
import shutil

class TestLiveIndexTTS(unittest.IsolatedAsyncioTestCase):
    BASE_URL = "http://192.168.2.252:8000"
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.dummy_wav = os.path.join(self.test_dir, "test_prompt.wav")
        self.output_wav = os.path.join(self.test_dir, "test_output.wav")
        
        # Create a dummy silent wav file for testing upload
        with contextlib.closing(wave.open(self.dummy_wav, 'w')) as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(44100)
            f.writeframes(b'\x00' * 44100) # 1 second silence

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    async def test_live_api_flow(self):
        """
        Test the live IndexTTS API flow:
        1. Upload a dummy audio file to /upload_audio
        2. Use the returned path to generate speech via /tts
        """
        print(f"\nTesting connection to {self.BASE_URL}...")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 1. Test Upload
            upload_url = f"{self.BASE_URL}/upload_audio"
            print(f"1. Uploading to {upload_url}...")
            
            if not os.path.exists(self.dummy_wav):
                self.fail("Dummy wav file generation failed")

            files = {'file': ('test_prompt.wav', open(self.dummy_wav, 'rb'), 'audio/wav')}
            
            try:
                resp = await client.post(upload_url, files=files)
            except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout) as e:
                print(f"   [SKIP] Connection failed: {e}")
                self.skipTest(f"Failed to connect to {self.BASE_URL} (Timeout/Refused). Is the server running?")
                return
            except Exception as e:
                self.fail(f"Upload request failed with exception: {e}")

            if resp.status_code != 200:
                self.fail(f"Upload failed: {resp.status_code} - {resp.text}")
            
            data = resp.json()
            voice_id = data.get("absolute_path")
            self.assertIsNotNone(voice_id, "Response JSON did not contain 'absolute_path'")
            print(f"   Success! Got voice_id: {voice_id}")

            # 2. Test TTS
            tts_url = f"{self.BASE_URL}/tts"
            print(f"2. Generating TTS at {tts_url}...")
            
            payload = {
                "text": "你好，这是一个测试。",
                "prompt_audio_path": voice_id,
                "emotion": {"mode": 0}
            }
            
            try:
                resp = await client.post(tts_url, json=payload)
            except Exception as e:
                self.fail(f"TTS request failed with exception: {e}")

            if resp.status_code != 200:
                self.fail(f"TTS failed: {resp.status_code} - {resp.text}")

            content_type = resp.headers.get("content-type", "")
            if "application/json" in content_type:
                self.fail(f"TTS returned JSON error despite 200 OK: {resp.text}")
            
            # Save output to verify we received data
            with open(self.output_wav, "wb") as f:
                f.write(resp.content)
            
            file_size = os.path.getsize(self.output_wav)
            print(f"   Success! Received audio ({file_size} bytes)")
            self.assertGreater(file_size, 100, "Received audio file is too small")

if __name__ == "__main__":
    unittest.main()
