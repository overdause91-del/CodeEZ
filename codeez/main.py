import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from . import config
from . import llm
from .providers.base import Message
from .utils import print_header, print_error, print_success, print_info


def cmd_setup():
    config.interactive_setup()


def cmd_models():
    provider = llm.get_provider()
    if not provider:
        print_error("Aucun provider configur.")
        print_info("Utilise : codeez --setup")
        return
    print(f"\nModles disponibles pour {provider.name} :")
    for m in provider.models():
        print(f"  - {m}")
    print()


def cmd_ask(args: list):
    provider = llm.get_provider()
    if not provider:
        print_error("Aucun provider configur.")
        print_info("Utilise : codeez --setup")
        return

    question = " ".join(args) if args else input("\nTa question : ").strip()
    if not question:
        return

    print(f"\n[{provider.name}] Rflexion en cours...\n")
    try:
        response = provider.send(
            messages=[Message(role="user", content=question)],
            system="Tu es un assistant de codage. Rponds en franais de manire concise et prcise.",
        )
        print(response)
        print()
    except Exception as e:
        print_error(f"Erreur : {e}")


def interactive_mode():
    provider = llm.get_provider()
    if not provider:
        print_error("Aucun provider configur.")
        print_info("Lance d'abord : codeez --setup")
        return

    print_header(f"CodeEZ - Mode interactif ({provider.name})")
    print("Commandes : /exit quitter, /help aide, /model changer de modle")
    print()

    messages = []
    system = "Tu es un assistant de codage. Rponds en franais de manire concise et prcise."

    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nAu revoir !")
            break

        if not user_input:
            continue

        if user_input == "/exit":
            print("\nAu revoir !")
            break
        elif user_input == "/help":
            print("\nCommandes disponibles :")
            print("  /exit   - Quitter")
            print("  /help   - Cette aide")
            print("  /clear  - Effacer l'historique")
            print("  /models - Voir les modles disponibles")
            print("  /model <nom> - Changer de modle")
            print()
            continue
        elif user_input == "/clear":
            messages.clear()
            print(" Historique effac.\n")
            continue
        elif user_input == "/models":
            for m in provider.models():
                print(f"  - {m}")
            print()
            continue
        elif user_input.startswith("/model "):
            model = user_input.split(" ", 1)[1]
            provider._model = model
            print_success(f"Modle chang pour : {model}\n")
            continue

        messages.append(Message(role="user", content=user_input))

        try:
            response = provider.send(messages=messages, system=system)
            messages.append(Message(role="assistant", content=response))
            print(f"\n{response}\n")
        except Exception as e:
            print_error(f"Erreur : {e}\n")
            messages.pop()


def main():
    args = sys.argv[1:]

    if not args:
        interactive_mode()
        return

    cmd = args[0]

    if cmd in ("--setup", "-s"):
        cmd_setup()
    elif cmd in ("--models", "-m"):
        cmd_models()
    elif cmd in ("--ask", "-a"):
        cmd_ask(args[1:])
    elif cmd in ("--help", "-h"):
        print("""
CodeEZ - Agent de codage IA simple et puissant

Utilisation :
  codeez              Mode interactif
  codeez --setup      Configuration (API keys)
  codeez --ask <msg>  Poser une question rapide
  codeez --models     Voir les modles disponibles
  codeez --help       Cette aide
""")
    else:
        print_error(f"Commande inconnue : {cmd}")
        print_info("Utilise : codeez --help")


if __name__ == "__main__":
    main()
