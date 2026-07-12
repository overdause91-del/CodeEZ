from openai import OpenAI
from .base import BaseProvider, Message
from typing import List


class OpenRouterProvider(BaseProvider):
    name = "openrouter"

    def __init__(self, api_key: str, model: str = "openai/gpt-4o"):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )
        self._model = model

    def send(self, messages: List[Message], system: str = "", **kwargs) -> str:
        msgs = []
        if system:
            msgs.append({"role": "system", "content": system})
        for m in messages:
            msgs.append({"role": m.role, "content": m.content})

        res = self.client.chat.completions.create(
            model=kwargs.get("model", self._model),
            messages=msgs,
        )
        return res.choices[0].message.content or ""

    def models(self) -> List[str]:
        return [
            "openai/gpt-4o",
            "openai/gpt-4o-mini",
            "anthropic/claude-sonnet-4",
            "anthropic/claude-3.5-sonnet",
            "google/gemini-2.5-flash",
            "google/gemini-2.5-pro",
            "meta-llama/llama-3.3-70b",
            "deepseek/deepseek-chat",
        ]
