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
        import httpx
        
        http_client = httpx.AsyncClient(proxy=settings.OPENAI_PROXY) if settings.OPENAI_PROXY else None
        
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            http_client=http_client
        )

    async def generate_response(self, system_prompt: str, user_text: str) -> dict:
        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
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
    api_key = settings.OPENAI_API_KEY
    if not api_key or api_key == "mock":
        logger.info("LLM Provider: Mock (API Key is missing or 'mock')")
        return MockLLMProvider()
    
    masked_key = api_key[:8] + "..." if len(api_key) > 8 else "..."
    logger.info(f"LLM Provider: OpenAI (API Key starts with {masked_key})")
    return OpenAILLMProvider()
