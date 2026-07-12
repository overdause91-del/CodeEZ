from .providers.openai_provider import OpenAIProvider
from .providers.anthropic_provider import AnthropicProvider
from .providers.google_provider import GoogleProvider
from .providers.openrouter_provider import OpenRouterProvider
from .providers.base import BaseProvider, Message
from . import config
from typing import Optional


def get_provider(name: Optional[str] = None) -> Optional[BaseProvider]:
    name = name or config.get_default_provider()
    api_key = config.get_provider_config(name)
    if not api_key:
        return None

    providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "google": GoogleProvider,
        "openrouter": OpenRouterProvider,
    }

    cls = providers.get(name)
    if not cls:
        return None

    return cls(api_key=api_key)
