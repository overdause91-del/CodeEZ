#!/usr/bin/env python3
"""
CodeEZ GUI - Interface graphique pour LLM gratuits et configurable.
Zero dependance externe (utilise tkinter + urllib de la stdlib).
"""

import json
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import urllib.request
import urllib.error
from pathlib import Path
from functools import partial


CONFIG_DIR = Path.home() / ".codeez"
CONFIG_FILE = CONFIG_DIR / "config.json"


PROVIDERS = {
    "deepseek": {
        "name": "DeepSeek",
        "tag": "Gratuit",
        "url": "https://api.deepseek.com/v1/chat/completions",
        "models": ["deepseek-chat", "deepseek-reasoner"],
        "default_model": "deepseek-chat",
        "doc_url": "https://platform.deepseek.com/api_keys",
        "tuto": [
            "1. Va sur https://platform.deepseek.com/api_keys",
            "2. Cree un compte (gratuit)",
            "3. Copie ta cle API (commence par sk-)",
            "4. Colle-la ci-dessous",
        ],
    },
    "openai": {
        "name": "OpenAI",
        "tag": "Payant",
        "url": "https://api.openai.com/v1/chat/completions",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
        "default_model": "gpt-4o-mini",
        "doc_url": "https://platform.openai.com/api-keys",
        "tuto": [
            "1. Va sur https://platform.openai.com/api-keys",
            "2. Connecte-toi ou cree un compte",
            "3. Clique 'Create new secret key'",
            "4. Copie la cle (commence par sk-)",
        ],
    },
    "anthropic": {
        "name": "Anthropic Claude",
        "tag": "Payant",
        "url": "https://api.anthropic.com/v1/messages",
        "models": ["claude-sonnet-4-20250514", "claude-3-5-sonnet-20241022"],
        "default_model": "claude-sonnet-4-20250514",
        "doc_url": "https://console.anthropic.com/settings/keys",
        "tuto": [
            "1. Va sur https://console.anthropic.com/settings/keys",
            "2. Connecte-toi ou cree un compte",
            "3. Clique 'Create Key'",
            "4. Copie la cle (commence par sk-ant-)",
        ],
    },
    "google": {
        "name": "Google Gemini",
        "tag": "Gratuit",
        "url": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        "models": ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"],
        "default_model": "gemini-2.5-flash",
        "doc_url": "https://aistudio.google.com/apikey",
        "tuto": [
            "1. Va sur https://aistudio.google.com/apikey",
            "2. Connecte-toi avec un compte Google",
            "3. Clique 'Create API Key'",
            "4. Copie la cle (commence par AIza)",
        ],
    },
    "openrouter": {
        "name": "OpenRouter",
        "tag": "Mixte",
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "models": [
            "deepseek/deepseek-chat", "openai/gpt-4o-mini",
            "anthropic/claude-sonnet-4", "google/gemini-2.5-flash",
            "meta-llama/llama-3.3-70b",
        ],
        "default_model": "deepseek/deepseek-chat",
        "doc_url": "https://openrouter.ai/keys",
        "tuto": [
            "1. Va sur https://openrouter.ai/keys",
            "2. Cree un compte",
            "3. Clique 'Create Key'",
            "4. Copie la cle (commence par sk-or-)",
        ],
    },
    "ollama": {
        "name": "Ollama (local)",
        "tag": "100% Gratuit",
        "url": "http://localhost:11434/api/chat",
        "models": [],
        "default_model": "",
        "doc_url": "https://ollama.ai",
        "tuto": [
            "1. Va sur https://ollama.ai et telecharge Ollama",
            "2. Installe et lance Ollama",
            "3. Dans un terminal : ollama pull deepseek-coder:6.7b",
            "4. Reviens ici et clique 'Detecter Ollama'",
        ],
    },
}


def load_config():
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}


def save_config(cfg):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))


def check_ollama():
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read())
            models = [m["name"] for m in data.get("models", [])]
            return True, models
    except Exception:
        return False, []


def ask_ollama(messages, model):
    data = {
        "model": model,
        "messages": [{"role": m["role"], "content": m["content"]} for m in messages],
        "stream": False,
    }
    req = urllib.request.Request(
        "http://localhost:11434/api/chat",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read())
    return result["message"]["content"]


def ask_openai_compat(url, api_key, messages, model, extra_headers=None):
    data = {
        "model": model,
        "messages": [{"role": m["role"], "content": m["content"]} for m in messages],
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(
        url, data=json.dumps(data).encode(), headers=headers
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read())
    return result["choices"][0]["message"]["content"]


def ask_anthropic(messages, api_key, model):
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
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read())
    return result["content"][0]["text"]


def ask_google(messages, api_key, model):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    contents = [{"role": m["role"], "parts": [{"text": m["content"]}]} for m in messages]
    data = {"contents": contents}
    req = urllib.request.Request(
        url, data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read())
    return result["candidates"][0]["content"]["parts"][0]["text"]


class CodeEZGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CodeEZ - Agent IA")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        self.cfg = load_config()
        self.messages = []
        self.provider = self.cfg.get("default_provider", "deepseek")
        self.model = self.cfg.get("default_model", "deepseek-chat")
        self.api_key = self._get_key(self.provider)
        self.auto_mode = self.cfg.get("auto_mode", True)
        self.ollama_available = False
        self.ollama_models = []
        self._build_ui()

    def _get_key(self, provider):
        k = self.cfg.get(f"{provider}_key")
        if k:
            return k
        return os.environ.get(f"{provider.upper()}_API_KEY")

    def _build_ui(self):
        top = ttk.Frame(self.root)
        top.pack(fill=tk.X, padx=8, pady=4)

        self.auto_var = tk.BooleanVar(value=self.auto_mode)
        self.auto_btn = ttk.Checkbutton(
            top, text="Mode Auto", variable=self.auto_var,
            command=self._toggle_auto
        )
        self.auto_btn.pack(side=tk.LEFT, padx=4)

        ttk.Separator(top, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)

        ttk.Label(top, text="Provider:").pack(side=tk.LEFT, padx=4)
        self.provider_combo = ttk.Combobox(
            top, values=list(PROVIDERS.keys()), state="readonly", width=20
        )
        self.provider_combo.set(self.provider)
        self.provider_combo.pack(side=tk.LEFT, padx=4)
        self.provider_combo.bind("<<ComboboxSelected>>", self._on_provider_change)

        ttk.Label(top, text="Modele:").pack(side=tk.LEFT, padx=4)
        self.model_combo = ttk.Combobox(top, state="readonly", width=25)
        self.model_combo.pack(side=tk.LEFT, padx=4)
        self.model_combo.bind("<<ComboboxSelected>>", self._on_model_change)

        self.config_btn = ttk.Button(top, text="Config", command=self._open_settings)
        self.config_btn.pack(side=tk.RIGHT, padx=4)

        self.detect_btn = ttk.Button(
            top, text="Detecter Ollama", command=self._detect_ollama
        )

        self.status_label = ttk.Label(top, text="", foreground="gray")
        self.status_label.pack(side=tk.RIGHT, padx=8)

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        self.chat_area = scrolledtext.ScrolledText(
            main_frame, wrap=tk.WORD, state=tk.DISABLED,
            font=("Segoe UI", 10),
            bg="#1e1e1e", fg="#d4d4d4",
            insertbackground="white",
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True)

        bottom = ttk.Frame(self.root)
        bottom.pack(fill=tk.X, padx=8, pady=4)

        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(bottom, textvariable=self.input_var)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.input_entry.bind("<Return>", self._send_message)

        self.send_btn = ttk.Button(bottom, text="Envoyer", command=self._send_message)
        self.send_btn.pack(side=tk.RIGHT)

        self._update_model_list()
        self._check_ollama_at_start()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._log("CodeEZ pret. Mode Auto: " + ("ON" if self.auto_mode else "OFF"))

    def _toggle_auto(self):
        self.auto_mode = self.auto_var.get()
        self.cfg["auto_mode"] = self.auto_mode
        save_config(self.cfg)
        if self.auto_mode:
            self.detect_btn.pack_forget()
            self._check_ollama_at_start()
        self._log("Mode Auto: " + ("ON" if self.auto_mode else "OFF"))

    def _detect_ollama(self):
        self.status_label.config(text="Detection...")
        self.root.update()
        ok, models = check_ollama()
        if ok and models:
            PROVIDERS["ollama"]["models"] = models
            self.ollama_available = True
            self.ollama_models = models
            self.provider = "ollama"
            self.model = models[0]
            self.api_key = ""
            self.cfg["default_provider"] = "ollama"
            self.cfg["default_model"] = models[0]
            save_config(self.cfg)
            self.provider_combo.set("ollama")
            self._update_model_list()
            self.status_label.config(text="Ollama OK", foreground="green")
            self._log("Ollama detecte avec " + str(len(models)) + " modeles")
        else:
            self.status_label.config(text="Ollama introuvable", foreground="orange")
            self._log("Ollama non detecte. Utilise DeepSeek ou configure un provider.")

    def _check_ollama_at_start(self):
        if not self.auto_mode:
            return
        self.status_label.config(text="Verification Ollama...")
        self.root.update()
        ok, models = check_ollama()
        if ok and models:
            PROVIDERS["ollama"]["models"] = models
            self.ollama_available = True
            self.ollama_models = models
            self.provider = "ollama"
            self.model = models[0]
            self.api_key = ""
            self.cfg["default_provider"] = "ollama"
            self.cfg["default_model"] = models[0]
            save_config(self.cfg)
            self.provider_combo.set("ollama")
            self._update_model_list()
            self.status_label.config(text="Ollama OK", foreground="green")
            self.detect_btn.pack_forget()
            self._log("Mode Auto: Ollama connecte - " + models[0])
        else:
            self.status_label.config(text="Mode Auto: DeepSeek (gratuit)", foreground="gray")
            self._log("Mode Auto: Ollama non trouve -> utilise DeepSeek")
            if not self.api_key:
                self._auto_configure_deepseek()

    def _auto_configure_deepseek(self):
        self.provider = "deepseek"
        self.model = "deepseek-chat"
        self.provider_combo.set("deepseek")
        self._update_model_list()
        if not self._get_key("deepseek"):
            self._log("Mode Auto: Configure DeepSeek (gratuit) pour continuer...")
            self._open_settings(provider="deepseek")

    def _on_provider_change(self, event=None):
        p = self.provider_combo.get()
        if p == "ollama":
            self._detect_ollama()
            return
        self.provider = p
        self.model = PROVIDERS[p]["default_model"]
        self.api_key = self._get_key(p)
        self.cfg["default_provider"] = p
        self.cfg["default_model"] = self.model
        save_config(self.cfg)
        self._update_model_list()
        self._log("Provider change: " + PROVIDERS[p]["name"])

    def _on_model_change(self, event=None):
        self.model = self.model_combo.get()
        self.cfg["default_model"] = self.model
        save_config(self.cfg)

    def _update_model_list(self):
        info = PROVIDERS.get(self.provider)
        if info and info["models"]:
            self.model_combo["values"] = info["models"]
            if self.model in info["models"]:
                self.model_combo.set(self.model)
            else:
                self.model = info["default_model"]
                self.model_combo.set(info["default_model"])
        else:
            self.model_combo["values"] = []
            self.model_combo.set("")

    def _log(self, msg):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"[{msg}]\n", "log")
        self.chat_area.tag_config("log", foreground="#888888")
        self.chat_area.see(tk.END)
        self.chat_area.config(state=tk.DISABLED)

    def _add_message(self, role, content):
        self.chat_area.config(state=tk.NORMAL)
        tag = "user" if role == "user" else "assistant"
        prefix = "> " if role == "user" else ""
        self.chat_area.insert(tk.END, f"{prefix}{content}\n\n", tag)
        if role == "user":
            self.chat_area.tag_config("user", foreground="#569cd6")
        else:
            self.chat_area.tag_config("assistant", foreground="#ce9178")
        self.chat_area.see(tk.END)
        self.chat_area.config(state=tk.DISABLED)

    def _send_message(self, event=None):
        text = self.input_var.get().strip()
        if not text:
            return
        self.input_var.set("")
        self._add_message("user", text)
        self.messages.append({"role": "user", "content": text})
        self.send_btn.config(state=tk.DISABLED)
        self.input_entry.config(state=tk.DISABLED)
        self.status_label.config(text="En cours...", foreground="blue")
        threading.Thread(target=self._get_response, daemon=True).start()

    def _get_response(self):
        try:
            if self.provider == "ollama":
                resp = ask_ollama(self.messages, self.model)
            elif self.provider == "anthropic":
                resp = ask_anthropic(self.messages, self.api_key, self.model)
            elif self.provider == "google":
                resp = ask_google(self.messages, self.api_key, self.model)
            else:
                info = PROVIDERS[self.provider]
                resp = ask_openai_compat(info["url"], self.api_key, self.messages, self.model)
            self.root.after(0, self._on_response, resp)
        except urllib.error.HTTPError as e:
            err = f"Erreur HTTP {e.code}"
            try:
                err += ": " + e.read().decode()
            except Exception:
                pass
            self.root.after(0, self._on_error, err)
        except Exception as e:
            self.root.after(0, self._on_error, str(e))

    def _on_response(self, resp):
        self.messages.append({"role": "assistant", "content": resp})
        self._add_message("assistant", resp)
        self.send_btn.config(state=tk.NORMAL)
        self.input_entry.config(state=tk.NORMAL)
        self.input_entry.focus()
        self.status_label.config(text="Pret", foreground="green")

    def _on_error(self, err):
        self._log("Erreur: " + err)
        self.messages.pop()
        self.send_btn.config(state=tk.NORMAL)
        self.input_entry.config(state=tk.NORMAL)
        self.input_entry.focus()
        self.status_label.config(text="Erreur", foreground="red")

    def _open_settings(self, provider=None):
        SettingsDialog(self.root, self, provider)

    def _on_close(self):
        save_config(self.cfg)
        self.root.destroy()

    def run(self):
        self.root.mainloop()


class SettingsDialog:
    def __init__(self, parent, app, preset_provider=None):
        self.app = app
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Configuration CodeEZ")
        self.dialog.geometry("550x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        main = ttk.Frame(self.dialog, padding=16)
        main.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main, text="Fournisseur LLM", font=("", 12, "bold")).pack(anchor=tk.W)
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)

        self.notebook = ttk.Notebook(main)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.entries = {}
        keys = list(PROVIDERS.keys())
        if preset_provider and preset_provider in keys:
            idx = keys.index(preset_provider)
            keys.remove(preset_provider)
            keys.insert(0, preset_provider)

        for pid in keys:
            self._add_provider_tab(pid)

        if preset_provider:
            for i, pid in enumerate(keys):
                if pid == preset_provider:
                    self.notebook.select(i)
                    break

        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(fill=tk.X, padx=16, pady=8)
        ttk.Button(btn_frame, text="Fermer", command=self.dialog.destroy).pack(side=tk.RIGHT)

    def _add_provider_tab(self, pid):
        info = PROVIDERS[pid]
        frame = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(frame, text=info["name"] + " (" + info["tag"] + ")")

        if pid == "ollama":
            ttk.Label(frame, text="Ollama - LLM local 100% gratuit", font=("", 11, "bold")).pack(anchor=tk.W, pady=4)
            for line in info["tuto"]:
                ttk.Label(frame, text=line).pack(anchor=tk.W, padx=8, pady=1)
            ttk.Button(frame, text="Detecter Ollama", command=self._detect).pack(pady=12)
            return

        ttk.Label(frame, text=info["name"], font=("", 11, "bold")).pack(anchor=tk.W, pady=4)

        tuto_frame = ttk.LabelFrame(frame, text="Configuration", padding=8)
        tuto_frame.pack(fill=tk.BOTH, expand=True, pady=4)

        for line in info["tuto"]:
            ttk.Label(tuto_frame, text=line).pack(anchor=tk.W, padx=4, pady=1)

        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)

        ttk.Label(frame, text="Cle API:").pack(anchor=tk.W)
        entry_frame = ttk.Frame(frame)
        entry_frame.pack(fill=tk.X, pady=4)

        entry = ttk.Entry(entry_frame, width=50, show="*")
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        existing = self.app._get_key(pid)
        if existing:
            entry.insert(0, existing)

        btn_save = ttk.Button(
            entry_frame, text="Enregistrer",
            command=lambda p=pid, e=entry: self._save_key(p, e)
        )
        btn_save.pack(side=tk.RIGHT, padx=4)

        show_var = tk.BooleanVar()
        show_btn = ttk.Checkbutton(
            entry_frame, text="Afficher", variable=show_var,
            command=lambda e=entry, v=show_var: e.config(show="" if v.get() else "*")
        )
        show_btn.pack(side=tk.RIGHT, padx=4)

        self.entries[pid] = entry

    def _save_key(self, pid, entry):
        key = entry.get().strip()
        if not key:
            return
        self.app.cfg[f"{pid}_key"] = key
        self.app.cfg["default_provider"] = pid
        self.app.cfg["default_model"] = PROVIDERS[pid]["default_model"]
        save_config(self.app.cfg)
        self.app.api_key = key
        self.app.provider = pid
        self.app.model = PROVIDERS[pid]["default_model"]
        self.app.provider_combo.set(pid)
        self.app._update_model_list()
        self.app._log("Cle " + PROVIDERS[pid]["name"] + " enregistree")

    def _detect(self):
        ok, models = check_ollama()
        if ok and models:
            PROVIDERS["ollama"]["models"] = models
            self.app.ollama_available = True
            self.app.ollama_models = models
            self.app.provider = "ollama"
            self.app.model = models[0]
            self.app.api_key = ""
            self.app.cfg["default_provider"] = "ollama"
            self.app.cfg["default_model"] = models[0]
            save_config(self.app.cfg)
            self.app.provider_combo.set("ollama")
            self.app._update_model_list()
            self.app._log("Ollama connecte: " + ", ".join(models[:3]))
            messagebox.showinfo("Ollama", f"Ollama detecte avec {len(models)} modele(s) !")
        else:
            messagebox.showwarning("Ollama", "Ollama non trouve.\nAssure-toi qu'Ollama est installe et lance.")


def main():
    app = CodeEZGUI()
    app.run()


if __name__ == "__main__":
    main()
