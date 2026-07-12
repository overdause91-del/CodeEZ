# CodeEZ

**Agent IA zero-dependance - DeepSeek gratuit par defaut**

Pas de pip install. Pas de dependances. Un seul fichier Python. Clone et lance.

---

## Installation (15 secondes)

### Dans Cursor (ou n'importe quel terminal)

```powershell
git clone https://github.com/overdause91-del/CodeEZ.git
cd CodeEZ
python codeez.py --setup
```

> Si `git` n'est pas reconnu, telecharge le zip :
> https://github.com/overdause91-del/CodeEZ/archive/refs/heads/main.zip

> Si `python` n'est pas reconnu, utilise le chemin complet :
> ```powershell
> & "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe" codeez.py --setup
> ```

### Sinon, double-clic sur le fichier :
- `codeez.ps1` (Windows) - trouve Python automatiquement
- Ou ouvre `codeez.py` dans Cursor et appuie sur **Run** (▷)

---

## Configuration

Lance et suis les instructions :
```powershell
python codeez.py --setup
```

**DeepSeek (gratuit)** est propose par defaut.
- Va sur https://platform.deepseek.com/api_keys
- Cree un compte, copie ta cle API
- Colle-la dans le terminal

Termine ! Tu peux maintenant lancer :
```powershell
python codeez.py
```

---

## Switch vers d'autres modeles

En mode interactif, utilise :
```
/provider openai       # Switch vers OpenAI
/provider openrouter   # Switch vers OpenRouter (100+ modeles)
/provider anthropic    # Switch vers Claude
/provider google       # Switch vers Gemini (gratuit)
/model deepseek-chat   # Change le modele
```

Ou refais `--setup` pour changer de provider par defaut.

---

## Providers supportes

| Provider | Prix | Modele par defaut |
|----------|------|-------------------|
| **DeepSeek** | Gratuit | deepseek-chat |
| **Google Gemini** | Gratuit | gemini-2.5-flash |
| **OpenAI** | Payant | gpt-4o-mini |
| **Anthropic Claude** | Payant | claude-sonnet-4 |
| **OpenRouter** | Mixte | deepseek/deepseek-chat |

---

## Pourquoi zero dependance ?

`codeez.py` utilise uniquement la librairie standard Python (`urllib`, `json`).
Pas de `pip install`, pas de `requirements.txt`, pas de conflits de versions.

Ca marche sur n'importe quelle machine avec Python 3.10+.
