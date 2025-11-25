from typing import Iterable
from backend.llm.base import LLMClient


class MockLLMClient:
    def generate(self, prompt: str, **kwargs) -> str:
        return "Mock response based on prompt: " + prompt[:120]

    def generate_stream(self, prompt: str, **kwargs) -> Iterable[str]:
        base_text = self.generate(prompt)
        parts = [base_text[i : i + 40] for i in range(0, len(base_text), 40)]
        for part in parts:
            yield part


def get_llm_client(provider: str) -> LLMClient:
    return MockLLMClient()
