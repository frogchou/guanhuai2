import unittest
import os
import shutil
import tempfile
from unittest.mock import MagicMock, AsyncMock, patch
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Mock app.core.config BEFORE importing app.services.tts_service
# This avoids importing pydantic which is not installed/buildable in this environment
mock_config_module = MagicMock()
mock_config_module.settings.INDEXTTS_BASE_URL = "http://mock-url"
sys.modules["app.core.config"] = mock_config_module

# Also mock pydantic_settings just in case
sys.modules["pydantic_settings"] = MagicMock()
sys.modules["pydantic"] = MagicMock()

from app.services.tts_service import IndexTTSClient

class TestIndexTTSClient(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)

    async def test_generate_audio_success(self):
        """Test successful audio generation."""
        # Arrange
        client = IndexTTSClient()
        output_path = os.path.join(self.test_dir, "success.wav")
        voice_id = "test_voice"
        text = "Hello"
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake_audio_content"
        mock_response.headers = {"content-type": "audio/wav"}
        
        client.client.post = AsyncMock(return_value=mock_response)
        
        # Act
        result = await client.generate_audio(text, voice_id, output_path)
        
        # Assert
        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_path))
        with open(output_path, "rb") as f:
            content = f.read()
        self.assertEqual(content, b"fake_audio_content")

    async def test_generate_audio_failure_500(self):
        """Test handling of 500 server error."""
        # Arrange
        client = IndexTTSClient()
        output_path = os.path.join(self.test_dir, "fail_500.wav")
        
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        client.client.post = AsyncMock(return_value=mock_response)
        
        # Act
        result = await client.generate_audio("text", "vid", output_path)
        
        # Assert
        self.assertFalse(result)
        # Should generate silent wav fallback
        self.assertTrue(os.path.exists(output_path))
        self.assertGreater(os.path.getsize(output_path), 0)

    async def test_generate_audio_json_error(self):
        """Test handling of 200 OK but JSON error response."""
        # Arrange
        client = IndexTTSClient()
        output_path = os.path.join(self.test_dir, "fail_json.wav")
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.text = '{"error": "something wrong"}'
        mock_response.content = b'{"error": "something wrong"}'
        
        client.client.post = AsyncMock(return_value=mock_response)
        
        # Act
        result = await client.generate_audio("text", "vid", output_path)
        
        # Assert
        self.assertFalse(result)
        self.assertTrue(os.path.exists(output_path))
        # Should be silent wav, not the json content
        with open(output_path, "rb") as f:
            content = f.read()
        self.assertNotEqual(content, b'{"error": "something wrong"}')
        self.assertGreater(len(content), 0)

    async def test_generate_audio_exception(self):
        """Test handling of network exceptions."""
        # Arrange
        client = IndexTTSClient()
        output_path = os.path.join(self.test_dir, "exception.wav")
        
        client.client.post = AsyncMock(side_effect=Exception("Network error"))
        
        # Act
        result = await client.generate_audio("text", "vid", output_path)
        
        # Assert
        self.assertFalse(result)
        self.assertTrue(os.path.exists(output_path))
        self.assertGreater(os.path.getsize(output_path), 0)
