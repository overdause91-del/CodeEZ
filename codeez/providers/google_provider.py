from google import genai
from google.genai import types
from .base import BaseProvider, Message
from typing import List


class GoogleProvider(BaseProvider):
    name = "google"

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self.client = genai.Client(api_key=api_key)
        self._model = model

    def send(self, messages: List[Message], system: str = "", **kwargs) -> str:
        msgs = [{"role": m.role, "content": m.content} for m in messages]
        model = kwargs.get("model", self._model)

        config = types.GenerateContentConfig(system_instruction=system) if system else None
        res = self.client.models.generate_content(
            model=model,
            contents=msgs,
            config=config,
        )
        return res.text or ""

    def models(self) -> List[str]:
        return ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"]
