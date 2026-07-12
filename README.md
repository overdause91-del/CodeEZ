# CodeEZ

**Interface graphique pour LLM - Ollama (100% gratuit) + DeepSeek, OpenAI, Claude, Gemini...**

Zero dependance. Un seul clic pour lancer. Interface claire.

---

## Utilisation

### Option 1 : Interface graphique (recommande)

```powershell
python codeez_gui.py
```

Ouvre `codeez_gui.py` dans **Cursor / VS Code** et clique **Run** (▷).

L'interface propose :
- **Mode Auto** : detecte Ollama (local, gratuit), sinon guide vers DeepSeek
- **Config** : selection du provider avec tuto de connexion integre
- **Chat** : interface de discussion avec historique

### Option 2 : CLI (terminal)

```powershell
python codeez.py
```

---

## Mode Auto

Quand tu actives le **Mode Auto** :
1. CodeEZ cherche Ollama sur ton PC (http://localhost:11434)
2. **Si Ollama est trouve** : utilise les modeles locaux (100% gratuit, sans cle)
3. **Sinon** : propose DeepSeek avec un tuto pour obtenir ta cle gratuite

Pour installer Ollama : https://ollama.ai

---

## Providers disponibles

| Provider | Prix | Modele par defaut |
|----------|------|-------------------|
| **Ollama (local)** | 100% Gratuit | Modele installe localement |
| **DeepSeek** | Gratuit | deepseek-chat |
| **Google Gemini** | Gratuit | gemini-2.5-flash |
| **OpenAI** | Payant | gpt-4o-mini |
| **Anthropic Claude** | Payant | claude-sonnet-4 |
| **OpenRouter** | Mixte | deepseek/deepseek-chat |

---

## Configuration manuelle

Dans l'interface graphique, clique sur **Config** pour :
1. Choisir un provider
2. Suivre le tuto integre (lien + etapes)
3. Coller ta cle API
4. C'est pret !

---

## Structure du projet

```
CodeEZ/
  codeez_gui.py    # Interface graphique (tkinter)
  codeez.py        # Version CLI
  codeez.ps1       # Lanceur PowerShell
  README.md        # Ce fichier
```
