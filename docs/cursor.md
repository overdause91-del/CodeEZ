# Utiliser CodeEZ avec Cursor

Cursor est un diteur de code bas sur VS Code intgrant des fonctionnalits IA.

## 1. Ouvrir CodeEZ dans Cursor

```bash
git clone https://github.com/TON_USER/CodeEZ.git
cd CodeEZ
cursor .
```

Ou : **File > Open Folder** et choisis le dossier CodeEZ.

## 2. Installer les dpendances

Ouvre le terminal intgr de Cursor (`Ctrl + ù` ou `Cmd + J`) :

```bash
pip install -r requirements.txt
```

## 3. Configurer ta cl API

Dans le terminal Cursor :

```bash
python main.py --setup
```

Suis les instructions l'cran pour entrer ta cl API.

Ou crer un fichier `.env` la racine du projet :

```env
OPENAI_API_KEY=sk-...
```

## 4. Utiliser CodeEZ

Dans le terminal Cursor :

```bash
python main.py
```

Pose tes questions directement.

### Exemple d'utilisation
```
> cris une fonction qui vrifie si un mot est un palindrome en Python

Voici une fonction simple :

def est_palindrome(mot):
    mot = mot.lower().replace(" ", "")
    return mot == mot[::-1]

# Test
print(est_palindrome("radar"))  # True
print(est_palindrome("hello"))  # False
```

## 5. Astuces

- Utilise **Ctrl+C** pour annuler une rponse en cours
- Utilise **/clear** pour vider l'historique de la session
- Change de modle avec **/model gpt-4o-mini** (moins cher mais plus rapide)
- Tu peux crer un alias dans le terminal intgr de Cursor :

```powershell
# Windows PowerShell
function codeez { python main.py @args }

# bash/zsh
alias codeez='python main.py'
```

## Problmes courants

| Problme | Solution |
|---------|----------|
| `Python n'est pas reconnu` | Installe Python depuis python.org et coche "Add to PATH" |
| `Module not found` | Relance `pip install -r requirements.txt` |
| `Cl API invalide` | Vrifie ta cl dans `~/.codeez/config.json` ou refais `--setup` |
| `Rate limit` | Attends quelques secondes ou change de modle |

## Pourquoi utiliser CodeEZ dans Cursor ?

- Cursor a dj un terminal intgr, pas besoin d'en ouvrir un autre
- Tu peux copier/coller du code directement de CodeEZ vers ton diteur
- Tout est dans la mme fentre
- Pas besoin de configurer un provider dans Cursor (conomie d'abonnement)

## Tu veux contribuer ?

Ouvre une issue ou une pull request sur le GitHub du projet !
