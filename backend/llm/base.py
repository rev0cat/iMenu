from typing import Iterable, Protocol


class LLMClient(Protocol):
    def generate(self, prompt: str, **kwargs) -> str:
        ...

    def generate_stream(self, prompt: str, **kwargs) -> Iterable[str]:
        ...

