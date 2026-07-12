from openai import OpenAI
from .base import BaseProvider, Message
from typing import List


class OpenAIProvider(BaseProvider):
    name = "openai"

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.client = OpenAI(api_key=api_key)
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
        return ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
