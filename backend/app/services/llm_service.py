import abc
import json
import logging
from app.core.config import settings
import httpx

logger = logging.getLogger(__name__)

class LLMProvider(abc.ABC):
    @abc.abstractmethod
    async def generate_response(self, system_prompt: str, user_text: str) -> dict:
        pass

class MockLLMProvider(LLMProvider):
    async def generate_response(self, system_prompt: str, user_text: str) -> dict:
        logger.info("MOCK LLM: Generating response...")
        return {
            "tone": "gentle",
            "content": f"Mock reply to: {user_text}. I hope you are doing well!"
        }

class OpenAILLMProvider(LLMProvider):
    def __init__(self):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate_response(self, system_prompt: str, user_text: str) -> dict:
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text}
                ],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            logger.error(f"OpenAI Error: {e}")
            # Fallback
            return {"tone": "neutral", "content": "I'm having trouble thinking right now, but I'm here."}

def get_llm_provider() -> LLMProvider:
    if settings.OPENAI_API_KEY == "mock":
        return MockLLMProvider()
    return OpenAILLMProvider()
