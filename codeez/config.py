import os
import json
from pathlib import Path
from typing import Optional


CONFIG_DIR = Path.home() / ".codeez"
CONFIG_FILE = CONFIG_DIR / "config.json"
ENV_FILE = CONFIG_DIR / ".env"


def _ensure_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    _ensure_dir()
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}


def save_config(config: dict):
    _ensure_dir()
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def get_provider_config(provider: str) -> Optional[str]:
    config = load_config()
    key = config.get(f"{provider}_api_key")
    if key:
        return key
    return os.environ.get(f"{provider.upper()}_API_KEY")


def set_provider(provider: str):
    config = load_config()
    config["default_provider"] = provider
    save_config(config)


def get_default_provider() -> str:
    config = load_config()
    return config.get("default_provider", "openai")


def set_api_key(provider: str, api_key: str):
    config = load_config()
    config[f"{provider}_api_key"] = api_key
    save_config(config)


def interactive_setup():
    _ensure_dir()
    print("=" * 50)
    print("  CodeEZ - Configuration")
    print("=" * 50)

    config = load_config()

    providers = [
        ("openai", "OpenAI (clavier, GPT-4o, etc.)"),
        ("anthropic", "Anthropic (Claude)"),
        ("google", "Google (Gemini)"),
        ("openrouter", "OpenRouter (acc.s a 100+ modles)"),
    ]

    print("\nQuel provider veux-tu utiliser par dfaut ?\n")
    for i, (key, name) in enumerate(providers, 1):
        print(f"  {i}. {name}")

    choice = input("\nChoix (1-4) : ").strip()
    try:
        idx = int(choice) - 1
        provider = providers[idx][0]
    except (ValueError, IndexError):
        print("Choix invalide, on prend OpenAI par dfaut.")
        provider = "openai"

    existing = get_provider_config(provider)
    if existing:
        print(f"\nCl API {provider} dj configure.")
        change = input("Changer ? (o/N) : ").strip().lower()
        if change != "o":
            set_provider(provider)
            print("\n Configuration termine !")
            return

    key = input(f"\nEntre ta cl API {provider} : ").strip()
    if key:
        set_api_key(provider, key)
        set_provider(provider)
        print(f" Cl API {provider} enregistre !")
    else:
        print("Pas de cl fournie. Tu pourras la configurer plus tard avec : codeez --setup")

    print("\n Configuration termine !")
    print("Utilise 'codeez' pour dmarrer une session.")
