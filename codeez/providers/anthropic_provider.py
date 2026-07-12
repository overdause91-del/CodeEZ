from anthropic import Anthropic
from .base import BaseProvider, Message
from typing import List


class AnthropicProvider(BaseProvider):
    name = "anthropic"

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        self.client = Anthropic(api_key=api_key)
        self._model = model

    def send(self, messages: List[Message], system: str = "", **kwargs) -> str:
        msgs = [{"role": m.role, "content": m.content} for m in messages]

        res = self.client.messages.create(
            model=kwargs.get("model", self._model),
            max_tokens=4096,
            system=system or None,
            messages=msgs,
        )
        return res.content[0].text if res.content else ""

    def models(self) -> List[str]:
        return [
            "claude-sonnet-4-20250514",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
        ]
