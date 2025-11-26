"""LLM client selector based on配置，支持 qwen/deepseek/gemini 等。"""

from functools import lru_cache

from backend.config import get_settings
from backend.llm.clients import GeminiClient, OpenAIStyleClient
from backend.llm.base import LLMClient

DEFAULT_BASE = {
    "openai": "https://api.openai.com",
    "openai_compatible": "https://api.openai.com",
    "deepseek": "https://api.deepseek.com",
    "qwen": "https://dashscope.aliyuncs.com/compatible-mode",
}


@lru_cache()
def get_llm_client() -> LLMClient:
    settings = get_settings()
    provider = settings.llm_provider.lower()

    if provider in {"openai", "openai_compatible", "deepseek", "qwen"}:
        api_key = settings.llm_api_key
        if not api_key:
            raise ValueError("请设置 llm_api_key 环境变量或 .env 中的值")
        base_url = settings.llm_base_url or DEFAULT_BASE.get(provider, DEFAULT_BASE["openai_compatible"])
        model = settings.llm_model
        return OpenAIStyleClient(model=model, api_key=api_key, base_url=base_url)

    if provider == "gemini":
        api_key = settings.gemini_api_key or settings.llm_api_key
        if not api_key:
            raise ValueError("请设置 gemini_api_key 或 llm_api_key")
        model = settings.gemini_model or settings.llm_model
        return GeminiClient(api_key=api_key, model=model)

    raise ValueError(f"Unsupported llm_provider: {settings.llm_provider}")

