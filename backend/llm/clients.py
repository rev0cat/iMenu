"""Concrete LLMClient implementations for OpenAI 兼容接口与 Gemini."""

import json
from typing import Iterable, Optional

import httpx

from backend.llm.base import LLMClient


class OpenAIStyleClient(LLMClient):
    """适配 OpenAI 兼容聊天接口的客户端，支持 qwen/deepseek 等。"""

    def __init__(self, model: str, api_key: str, base_url: str):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    @property
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _build_url(self) -> str:
        return f"{self.base_url}/v1/chat/completions"

    def generate(self, prompt: str, **kwargs) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            **({"temperature": kwargs["temperature"]} if "temperature" in kwargs else {}),
        }
        response = httpx.post(self._build_url(), headers=self._headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def generate_stream(self, prompt: str, **kwargs) -> Iterable[str]:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
            **({"temperature": kwargs["temperature"]} if "temperature" in kwargs else {}),
        }
        with httpx.stream(
            "POST", self._build_url(), headers=self._headers, json=payload, timeout=120
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line or not line.startswith(b"data:"):
                    continue
                chunk = line[len(b"data:") :].strip()
                if chunk == b"[DONE]":
                    break
                parsed = json.loads(chunk.decode())
                delta: Optional[str] = parsed["choices"][0]["delta"].get("content")
                if delta:
                    yield delta


class GeminiClient(LLMClient):
    """直接访问 Google Gemini REST 接口（非官方 SDK，便于脱离依赖）。"""

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str = "https://generativelanguage.googleapis.com/v1beta",
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    def _build_url(self, stream: bool = False) -> str:
        method = "streamGenerateContent" if stream else "generateContent"
        return f"{self.base_url}/models/{self.model}:{method}?key={self.api_key}"

    def generate(self, prompt: str, **kwargs) -> str:
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = httpx.post(self._build_url(stream=False), json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    def generate_stream(self, prompt: str, **kwargs) -> Iterable[str]:
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        with httpx.stream(
            "POST", self._build_url(stream=True), json=payload, timeout=120
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                try:
                    parsed = json.loads(line)
                    candidates = parsed.get("candidates") or []
                    if not candidates:
                        continue
                    parts = candidates[0].get("content", {}).get("parts", [])
                    for part in parts:
                        text = part.get("text")
                        if text:
                            yield text
                except json.JSONDecodeError:
                    continue

