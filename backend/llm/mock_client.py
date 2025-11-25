import time
from typing import Iterable
from .base import LLMClient


class MockLLMClient(LLMClient):
    def generate(self, prompt: str, **kwargs) -> str:
        return f"Mock response for prompt: {prompt[:60]}..."

    def generate_stream(self, prompt: str, **kwargs) -> Iterable[str]:
        chunks = ["Mock ", "stream ", "response ", "for ", "prompt"]
        for part in chunks:
            time.sleep(0.05)
            yield part

