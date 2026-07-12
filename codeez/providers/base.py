from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import List


@dataclass
class Message:
    role: str
    content: str


class BaseProvider(ABC):
    name: str = ""

    @abstractmethod
    def send(self, messages: List[Message], system: str = "", **kwargs) -> str:
        ...

    @abstractmethod
    def models(self) -> List[str]:
        ...
