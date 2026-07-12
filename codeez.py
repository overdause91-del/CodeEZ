#!/usr/bin/env python3
"""
CodeEZ - Agent IA zero-dependance.
Utilise uniquement la librairie standard Python.
DeepSeek (gratuit) par defaut. Supporte OpenAI, Anthropic, Google, OpenRouter.
"""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path


CONFIG_DIR = Path.home() / ".codeez"
CONFIG_FILE = CONFIG_DIR / "config.json"


PROVIDERS = {
    "deepseek": {
        "name": "DeepSeek (gratuit)",
        "url": "https://api.deepseek.com/v1/chat/completions",
        "models": ["deepseek-chat", "deepseek-reasoner"],
        "default_model": "deepseek-chat",
        "key_prefix": "sk-",
        "doc_url": "https://platform.deepseek.com/api_keys",
    },
    "openai": {
        "name": "OpenAI (payant)",
        "url": "https://api.openai.com/v1/chat/completions",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
        "default_model": "gpt-4o-mini",
        "key_prefix": "sk-",
        "doc_url": "https://platform.openai.com/api-keys",
    },
    "openrouter": {
        "name": "OpenRouter (100+ modeles)",
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "models": [
            "deepseek/deepseek-chat", "openai/gpt-4o", "openai/gpt-4o-mini",
            "anthropic/claude-sonnet-4", "google/gemini-2.5-flash",
            "meta-llama/llama-3.3-70b",
        ],
        "default_model": "deepseek/deepseek-chat",
        "key_prefix": "sk-or-",
        "doc_url": "https://openrouter.ai/keys",
    },
    "anthropic": {
        "name": "Anthropic Claude (payant)",
        "url": "https://api.anthropic.com/v1/messages",
        "models": ["claude-sonnet-4-20250514", "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"],
        "default_model": "claude-sonnet-4-20250514",
        "key_prefix": "sk-ant-",
        "doc_url": "https://console.anthropic.com/settings/keys",
    },
    "google": {
        "name": "Google Gemini (gratuit)",
        "url": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        "models": ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"],
        "default_model": "gemini-2.5-flash",
        "key_prefix": "AIza",
        "doc_url": "https://aistudio.google.com/apikey",
    },
}


def load_config():
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}


def save_config(cfg):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))


def ask_deepseek(messages, api_key, model="deepseek-chat"):
    return _ask_openai_compat(
        url="https://api.deepseek.com/v1/chat/completions",
        api_key=api_key,
        messages=messages,
        model=model,
    )


def ask_openai(messages, api_key, model="gpt-4o-mini"):
    return _ask_openai_compat(
        url="https://api.openai.com/v1/chat/completions",
        api_key=api_key,
        messages=messages,
        model=model,
    )


def ask_openrouter(messages, api_key, model="deepseek/deepseek-chat"):
    return _ask_openai_compat(
        url="https://openrouter.ai/api/v1/chat/completions",
        api_key=api_key,
        messages=messages,
        model=model,
        headers={"HTTP-Referer": "https://github.com/overdause91-del/CodeEZ"},
    )


def ask_anthropic(messages, api_key, model="claude-sonnet-4-20250514"):
    data = {
        "model": model,
        "max_tokens": 4096,
        "messages": [{"role": m["role"], "content": m["content"]} for m in messages],
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(data).encode(),
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    return result["content"][0]["text"]


def ask_google(messages, api_key, model="gemini-2.5-flash"):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    contents = [{"role": m["role"], "parts": [{"text": m["content"]}]} for m in messages]
    data = {"contents": contents}
    req = urllib.request.Request(
        url, data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    return result["candidates"][0]["content"]["parts"][0]["text"]


def _ask_openai_compat(url, api_key, messages, model, headers=None):
    data = {
        "model": model,
        "messages": [{"role": m["role"], "content": m["content"]} for m in messages],
    }
    req_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    if headers:
        req_headers.update(headers)

    req = urllib.request.Request(
        url, data=json.dumps(data).encode(), headers=req_headers
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    return result["choices"][0]["message"]["content"]


FUNCTIONS = {
    "deepseek": ask_deepseek,
    "openai": ask_openai,
    "openrouter": ask_openrouter,
    "anthropic": ask_anthropic,
    "google": ask_google,
}


def get_api_key(provider):
    cfg = load_config()
    key = cfg.get(f"{provider}_key")
    if key:
        return key
    return os.environ.get(f"{provider.upper()}_API_KEY")


def interactive_setup():
    print("=" * 50)
    print("  CodeEZ - Configuration")
    print("=" * 50)
    print()

    providers_list = list(PROVIDERS.items())
    print("Choix du provider :")
    for i, (key, info) in enumerate(providers_list, 1):
        print(f"  {i}. {info['name']}")
    print()

    choice = input("Choix (1-5, defaut=1 DeepSeek) : ").strip()
    try:
        idx = int(choice) - 1 if choice else 0
        provider = providers_list[idx][0]
    except (ValueError, IndexError):
        provider = "deepseek"

    info = PROVIDERS[provider]
    print(f"\nProvider choisi : {info['name']}")
    print(f"Modele par defaut : {info['default_model']}")
    print(f"\nObtenir ta cle : {info['doc_url']}")
    print()

    existing = get_api_key(provider)
    if existing:
        print(f"Cle deja configuree (finissant par ...{existing[-4:]})")
        change = input("Changer ? (o/N) : ").strip().lower()
        if change != "o":
            cfg = load_config()
            cfg["default_provider"] = provider
            cfg["default_model"] = info["default_model"]
            save_config(cfg)
            print("Configuration terminee !")
            return

    key = input(f"Entre ta cle API {info['name']} : ").strip()
    if key:
        cfg = load_config()
        cfg[f"{provider}_key"] = key
        cfg["default_provider"] = provider
        cfg["default_model"] = info["default_model"]
        save_config(cfg)
        print("Cle enregistree !")
    else:
        print("Pas de cle fournie. Utilise --setup plus tard.")

    print("\nConfiguration terminee !")
    print("Tu peux maintenant lancer : python codeez.py")


def get_model_options(provider):
    info = PROVIDERS.get(provider)
    return info["models"] if info else []


def main():
    args = sys.argv[1:]

    if "--setup" in args or "-s" in args:
        interactive_setup()
        return

    if "--help" in args or "-h" in args:
        print("""
CodeEZ - Agent IA zero-dependance

Utilisation :
  python codeez.py              Mode interactif
  python codeez.py --setup      Configuration (cle API)
  python codeez.py --ask <msg>  Question rapide
  python codeez.py --models     Modeles disponibles

Commandes interactives :
  /exit      Quitter
  /help      Aide
  /clear     Effacer l'historique
  /models    Voir les modeles
  /model <m> Changer de modele
  /provider <p> Changer de provider (deepseek, openai, ...)
""")
        return

    if "--models" in args or "-m" in args:
        cfg = load_config()
        provider = cfg.get("default_provider", "deepseek")
        print(f"\nModeles disponibles pour {PROVIDERS[provider]['name']} :")
        for m in PROVIDERS[provider]["models"]:
            print(f"  - {m}")
        print()
        return

    if "--ask" in args or "-a" in args:
        try:
            idx = args.index("--ask") if "--ask" in args else args.index("-a")
            question = " ".join(args[idx + 1:])
        except (ValueError, IndexError):
            question = input("Ta question : ").strip()
        if not question:
            return
        cfg = load_config()
        provider = cfg.get("default_provider", "deepseek")
        model = cfg.get("default_model", PROVIDERS[provider]["default_model"])
        api_key = get_api_key(provider)
        if not api_key:
            print("Configure d'abord ta cle : python codeez.py --setup")
            return
        fn = FUNCTIONS[provider]
        try:
            resp = fn(
                [{"role": "user", "content": question}],
                api_key,
                model,
            )
            print(f"\n{resp}\n")
        except Exception as e:
            print(f"Erreur : {e}")
        return

    interactive_mode()


def interactive_mode():
    cfg = load_config()
    provider = cfg.get("default_provider", "deepseek")
    model = cfg.get("default_model", PROVIDERS[provider]["default_model"])
    api_key = get_api_key(provider)

    if not api_key:
        print("=" * 50)
        print("  CodeEZ - Bienvenue !")
        print("=" * 50)
        print()
        print("Configure-toi en 30 secondes :")
        print("  1. Va sur https://platform.deepseek.com/api_keys")
        print("  2. Copie ta cle API (gratuite)")
        print("  3. Lance : python codeez.py --setup")
        print()
        print("Ou choisis un autre provider plus tard.")
        return

    info = PROVIDERS[provider]
    print("=" * 50)
    print(f"  CodeEZ - {info['name']}")
    print(f"  Modele : {model}")
    print("=" * 50)
    print("  /exit quitter  |  /help aide  |  /models liste")
    print()

    messages = []
    fn = FUNCTIONS[provider]

    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAu revoir !")
            break

        if not user_input:
            continue

        if user_input == "/exit":
            print("Au revoir !")
            break
        elif user_input == "/help":
            print("\nCommandes :")
            print("  /exit            Quitter")
            print("  /help            Cette aide")
            print("  /clear           Effacer l'historique")
            print("  /models          Voir les modeles disponibles")
            print("  /model <nom>     Changer de modele")
            print("  /provider <nom>  Changer de fournisseur (deepseek, openai, openrouter, anthropic, google)")
            print()
            continue
        elif user_input == "/clear":
            messages.clear()
            print("Historique efface.\n")
            continue
        elif user_input == "/models":
            for m in get_model_options(provider):
                print(f"  - {m}")
            print()
            continue
        elif user_input.startswith("/model "):
            model = user_input.split(" ", 1)[1]
            cfg["default_model"] = model
            save_config(cfg)
            print(f"Modele change pour : {model}\n")
            continue
        elif user_input.startswith("/provider "):
            p = user_input.split(" ", 1)[1]
            if p in FUNCTIONS:
                provider = p
                cfg["default_provider"] = p
                model = cfg.get("default_model", PROVIDERS[p]["default_model"])
                fn = FUNCTIONS[p]
                api_key = get_api_key(p)
                save_config(cfg)
                if not api_key:
                    print(f"Provider change mais pas de cle API pour {p}.\n")
                else:
                    print(f"Provider change pour : {PROVIDERS[p]['name']}\n")
            else:
                print(f"Provider inconnu. Choisis parmi : {', '.join(FUNCTIONS.keys())}\n")
            continue

        messages.append({"role": "user", "content": user_input})

        try:
            response = fn(messages, api_key, model)
            messages.append({"role": "assistant", "content": response})
            print(f"\n{response}\n")
        except urllib.error.HTTPError as e:
            print(f"Erreur HTTP {e.code} : {e.read().decode()}\n")
            messages.pop()
        except Exception as e:
            print(f"Erreur : {e}\n")
            messages.pop()


if __name__ == "__main__":
    main()
