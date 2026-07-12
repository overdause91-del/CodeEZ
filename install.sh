#!/bin/bash
# CodeEZ - Installation script for Linux/macOS
set -e

echo "=== CodeEZ Installation ==="
echo ""

# Check Python
PYTHON_CMD=""
for cmd in python3 python; do
    if command -v $cmd &> /dev/null; then
        VER=$($cmd --version 2>&1 | grep -oP '3\.\K[0-9]+')
        if [ "$VER" -ge 10 ] 2>/dev/null; then
            PYTHON_CMD=$cmd
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "Python 3.10+ est requis. https://python.org"
    exit 1
fi
echo "[OK] Python: $($PYTHON_CMD --version)"

# Install
echo ""
echo "Installation des dependances..."
$PYTHON_CMD -m pip install -e . 2>/dev/null || $PYTHON_CMD -m pip install -r requirements.txt
echo "[OK] Dependances installees"

# Alias
SHELL_RC="$HOME/.bashrc"
if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
fi
if [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
fi

ALIAS_LINE="alias codeez='$PYTHON_CMD $(pwd)/main.py'"
if ! grep -q "alias codeez=" "$SHELL_RC" 2>/dev/null; then
    echo "$ALIAS_LINE" >> "$SHELL_RC"
    echo "[OK] Alias ajoute a $SHELL_RC"
else
    echo "[OK] Alias deja present dans $SHELL_RC"
fi

echo ""
echo "Relance ton terminal ou fais : source $SHELL_RC"
echo "Puis lance : codeez --setup"
