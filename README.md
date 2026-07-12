# CodeEZ

**Agent de codage IA - Simple, rapide, gratuit.**

CodeEZ est un assistant de codage en ligne de commande qui fonctionne avec les principaux modles d'IA (OpenAI, Claude, Gemini, OpenRouter).

Pas besoin d'tre expert : clone le projet, configure ta cl API, et commence coder.

---

## Installation (1 minute)

### Prrequis
- Python 3.10 ou plus rcent
- Une cl API d'un fournisseur d'IA (OpenAI, Anthropic, Google, ou OpenRouter)

### Windows
```powershell
git clone https://github.com/TON_USER/CodeEZ.git
cd CodeEZ
py -3 -m pip install -r requirements.txt
py -3 main.py --setup
```

Si `py` ne fonctionne pas, utilise le chemin complet :
```powershell
python -m pip install -r requirements.txt
python main.py --setup
```

### macOS / Linux
```bash
git clone https://github.com/TON_USER/CodeEZ.git
cd CodeEZ
python3 -m pip install -r requirements.txt
python3 main.py --setup
```

### Ou avec le script d'installation
```bash
# Windows (PowerShell)
.\install.ps1

# macOS / Linux
chmod +x install.sh && ./install.sh
```

---

## Utilisation

### Mode interactif
```bash
# Si tu as install avec pip
codeez

# Sinon, depuis le dossier du projet
py -3 main.py
# ou
python main.py
```
Pose tes questions directement dans le terminal. L'historique est conserv pendant la session.

### Question rapide
```bash
codeez --ask "cris une fonction fibonacci en python"
# ou
python main.py -a "cris une fonction fibonacci en python"
```

### Liste des modles
```bash
codeez --models
# ou
python main.py --models
```

---

## Commandes en mode interactif

| Commande | Description |
|----------|-------------|
| `/exit` | Quitter |
| `/help` | Aide |
| `/clear` | Effacer l'historique |
| `/models` | Voir les modles |
| `/model <nom>` | Changer de modle |

---

## Configuration

Lance `codeez --setup` pour configurer ta cl API.

Tu peux aussi crer un fichier `.env` dans le dossier `~/.codeez/` :
```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
OPENROUTER_API_KEY=sk-or-...
```

Ou utiliser les variables d'environnement directement.

---

## Providers supports

| Provider | Cl API | Modles |
|----------|--------|--------|
| **OpenAI** | `sk-...` | GPT-4o, GPT-4o-mini, GPT-4-turbo |
| **Anthropic** | `sk-ant-...` | Claude Sonnet 4, Claude 3.5 |
| **Google** | `AIza...` | Gemini 2.5 Flash, Pro |
| **OpenRouter** | `sk-or-...` | 100+ modles (GPT, Claude, Gemini, Llama, DeepSeek...) |

---

## Utiliser avec Cursor

[Voir le guide complet](docs/cursor.md)

Rsume : ouvre le dossier CodeEZ dans Cursor, configure ton `.env`, et utilise le terminal intgr de Cursor pour lancer `codeez`.

---

## Structure du projet

```
CodeEZ/
  codeez/           # Code source
    main.py         # Point d'entre CLI
    config.py       # Gestion de configuration
    llm.py          # Interface avec les LLM
    providers/      # Implmentations des providers
  docs/             # Documentation
    cursor.md       # Guide d'utilisation avec Cursor
  codeez.bat        # Lanceur direct pour Windows
  main.py           # Script d'entre
  install.sh        # Script d'install (Unix)
  install.ps1       # Script d'install (Windows)
  README.md         # Ce fichier
```
