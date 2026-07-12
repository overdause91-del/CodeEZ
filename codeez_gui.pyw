#!/usr/bin/env python3
"""
CodeEZ - Interface chat façon Cursor.
Zero dependance. Ollama (gratuit) + DeepSeek + OpenAI + Claude + Gemini.
"""

import json
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, font
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime


CONFIG_DIR = Path.home() / ".codeez"
CONFIG_FILE = CONFIG_DIR / "config.json"

C_BG = "#1a1a2e"
C_BG2 = "#16213e"
C_SURFACE = "#0f3460"
C_PRIMARY = "#e94560"
C_TEXT = "#e0e0e0"
C_TEXT2 = "#a0a0a0"
C_USER = "#1a5276"
C_BOT = "#1e3a5f"
C_INPUT = "#0d1b2a"

PROVIDERS = {
    "deepseek": {
        "name": "DeepSeek (gratuit)",
        "url": "https://api.deepseek.com/v1/chat/completions",
        "models": ["deepseek-chat", "deepseek-reasoner"],
        "default_model": "deepseek-chat",
        "doc_url": "https://platform.deepseek.com/api_keys",
        "tuto": "1. Va sur platform.deepseek.com\n2. Cree un compte gratuit\n3. Copie ta cle API (sk-...)",
    },
    "openai": {
        "name": "OpenAI",
        "url": "https://api.openai.com/v1/chat/completions",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
        "default_model": "gpt-4o-mini",
        "doc_url": "https://platform.openai.com/api-keys",
        "tuto": "1. Va sur platform.openai.com\n2. Va dans API keys\n3. Cree une key (sk-...)",
    },
    "anthropic": {
        "name": "Claude (Anthropic)",
        "url": "https://api.anthropic.com/v1/messages",
        "models": ["claude-sonnet-4-20250514", "claude-3-5-sonnet-20241022"],
        "default_model": "claude-sonnet-4-20250514",
        "doc_url": "https://console.anthropic.com/settings/keys",
        "tuto": "1. Va sur console.anthropic.com\n2. Settings > Keys\n3. Create key (sk-ant-...)",
    },
    "google": {
        "name": "Gemini (Google)",
        "url": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        "models": ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"],
        "default_model": "gemini-2.5-flash",
        "doc_url": "https://aistudio.google.com/apikey",
        "tuto": "1. Va sur aistudio.google.com\n2. Get API Key\n3. Copie (AIza...)",
    },
    "openrouter": {
        "name": "OpenRouter (100+)",
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "models": ["deepseek/deepseek-chat", "openai/gpt-4o-mini", "anthropic/claude-sonnet-4"],
        "default_model": "deepseek/deepseek-chat",
        "doc_url": "https://openrouter.ai/keys",
        "tuto": "1. Va sur openrouter.ai/keys\n2. Create key\n3. Copie (sk-or-...)",
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
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read())
            return True, [m["name"] for m in data.get("models", [])]
    except Exception:
        return False, []

def ask_ollama(messages, model):
    data = {"model": model, "messages": [{"role": m["role"], "content": m["content"]} for m in messages], "stream": False}
    req = urllib.request.Request("http://localhost:11434/api/chat", data=json.dumps(data).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read())["message"]["content"]

def ask_api(url, api_key, messages, model, extra_headers=None):
    data = {"model": model, "messages": [{"role": m["role"], "content": m["content"]} for m in messages]}
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    if extra_headers: headers.update(extra_headers)
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read())["choices"][0]["message"]["content"]

def ask_anthropic(messages, api_key, model):
    data = {"model": model, "max_tokens": 4096, "messages": [{"role": m["role"], "content": m["content"]} for m in messages]}
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json", "x-api-key": api_key, "anthropic-version": "2023-06-01"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read())["content"][0]["text"]

def ask_google(messages, api_key, model):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    contents = [{"role": m["role"], "parts": [{"text": m["content"]}]} for m in messages]
    req = urllib.request.Request(url, data=json.dumps({"contents": contents}).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read())["candidates"][0]["content"]["parts"][0]["text"]


class ChatApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CodeEZ")
        self.root.geometry("720x520")
        self.root.minsize(500, 400)
        self.root.configure(bg=C_BG)

        self.cfg = load_config()
        self.messages = []
        self.provider = self.cfg.get("default_provider", "deepseek")
        self.model = self.cfg.get("default_model", "deepseek-chat")
        self._active_provider = self.provider
        self._active_model = self.model
        self.api_key = self._get_key(self.provider)

        self._build_ui()
        self._auto_start()

    def _get_key(self, provider):
        k = self.cfg.get(f"{provider}_key")
        return k if k else os.environ.get(f"{provider.upper()}_API_KEY")

    def _build_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=0)

        header = tk.Frame(self.root, bg=C_BG2, height=48)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.columnconfigure(1, weight=1)

        tk.Label(header, text="CodeEZ", font=("Segoe UI", 12, "bold"), fg=C_PRIMARY, bg=C_BG2).grid(row=0, column=0, padx=16, pady=10, sticky="w")

        self.mode_label = tk.Label(header, text="", font=("Segoe UI", 9), fg=C_TEXT2, bg=C_BG2)
        self.mode_label.grid(row=0, column=1, sticky="w", padx=4)

        settings_btn = tk.Button(header, text="", command=self._open_settings,
            bg=C_BG2, fg=C_TEXT, bd=0, font=("Segoe UI", 11), cursor="hand2")
        settings_btn.grid(row=0, column=2, padx=8)

        chat_frame = tk.Frame(self.root, bg=C_BG)
        chat_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=4)
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(chat_frame, bg=C_BG, highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(chat_frame, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg=C_BG)

        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw", width=self.canvas.winfo_width())
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        input_frame = tk.Frame(self.root, bg=C_BG, height=60)
        input_frame.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 12))
        input_frame.columnconfigure(0, weight=1)

        entry_bg = tk.Frame(input_frame, bg=C_INPUT, bd=0, highlightbackground=C_SURFACE, highlightthickness=1)
        entry_bg.pack(fill=tk.X, padx=(0, 8), side=tk.LEFT, expand=True)
        entry_bg.columnconfigure(0, weight=1)

        self.input_text = tk.Text(entry_bg, height=2, bg=C_INPUT, fg=C_TEXT, bd=0,
            font=("Segoe UI", 10), insertbackground=C_TEXT, wrap=tk.WORD)
        self.input_text.grid(row=0, column=0, sticky="ew", padx=12, pady=8)
        self.input_text.bind("<Return>", self._on_enter)
        self.input_text.bind("<Shift-Return>", lambda e: None)
        self.input_text.focus()

        self.send_btn = tk.Button(input_frame, text=">", command=self._send_message,
            bg=C_PRIMARY, fg="white", bd=0, font=("Segoe UI", 14, "bold"),
            width=3, height=1, cursor="hand2", activebackground="#ff6b81")
        self.send_btn.pack(side=tk.RIGHT)

        bottom_bar = tk.Frame(self.root, bg=C_BG2, height=28)
        bottom_bar.grid(row=3, column=0, sticky="ew")
        bottom_bar.grid_propagate(False)

        self.status_btn = tk.Button(bottom_bar, text="", font=("Segoe UI", 8),
            bg=C_BG2, fg=C_TEXT2, bd=0, cursor="hand2", anchor="w", command=self._open_settings)
        self.status_btn.pack(side=tk.LEFT, padx=12, pady=4)

        self._show_welcome()

    def _on_canvas_resize(self, event):
        self.canvas.itemconfig(1, width=event.width)

    def _show_welcome(self):
        self.add_bubble("bot", "Bienvenue dans CodeEZ !")
        self.add_bubble("bot", "Mode Auto : je cherche Ollama (local, gratuit)...")

    def _auto_start(self):
        self.root.after(200, self._auto_init)

    def _auto_init(self):
        ok, models = check_ollama()
        if ok and models:
            self._active_provider = "ollama"
            self._active_model = models[0]
            self.api_key = ""
            self.cfg["default_provider"] = "ollama"
            self.cfg["default_model"] = models[0]
            save_config(self.cfg)
            self.mode_label.config(text="Ollama " + models[0])
            self.status_btn.config(text="Ollama: " + models[0], fg="#4caf50")
            self.add_bubble("bot", "Ollama connecte avec " + models[0] + " !")
            self.add_bubble("bot", "Pose ta question !")
        else:
            self.mode_label.config(text="DeepSeek (gratuit)")
            api_key = self._get_key("deepseek")
            if api_key:
                self._active_provider = "deepseek"
                self._active_model = "deepseek-chat"
                self.api_key = api_key
                self.status_btn.config(text="DeepSeek: OK", fg="#4caf50")
                self.add_bubble("bot", "DeepSeek connecte ! Pose ta question.")
            else:
                self.add_bubble("bot", "Configure une cle pour commencer.")
                self._open_settings()

    def add_bubble(self, role, text):
        align = "e" if role == "user" else "w"
        bubble = tk.Frame(self.scroll_frame, bg=C_BG)
        bubble.pack(fill=tk.X, padx=8, pady=4)

        inner = tk.Frame(bubble, bg=C_USER if role == "user" else C_BOT, bd=0)
        inner.pack(anchor=align, padx=(0, 0))

        label = tk.Label(inner, text=text, bg=C_USER if role == "user" else C_BOT,
            fg=C_TEXT, font=("Segoe UI", 10), wraplength=500, justify="left",
            anchor="w", padx=16, pady=10)
        label.pack()

        self.root.after(50, self._scroll_bottom)

    def _scroll_bottom(self):
        self.canvas.yview_moveto(1.0)

    def _on_enter(self, event):
        if not event.state & 0x1:
            self._send_message()
            return "break"
        return None

    def _send_message(self):
        text = self.input_text.get("1.0", "end-1c").strip()
        if not text:
            return
        self.input_text.delete("1.0", tk.END)
        self.add_bubble("user", text)
        self.messages.append({"role": "user", "content": text})

        if not self.api_key and self._active_provider != "ollama":
            self.add_bubble("bot", "Configure ta cle API d'abord.")
            self._open_settings()
            return

        self.send_btn.config(state=tk.DISABLED, text="...")
        threading.Thread(target=self._get_response, daemon=True).start()

    def _get_response(self):
        try:
            p = self._active_provider
            if p == "ollama":
                resp = ask_ollama(self.messages, self._active_model)
            elif p == "anthropic":
                resp = ask_anthropic(self.messages, self.api_key, self._active_model)
            elif p == "google":
                resp = ask_google(self.messages, self.api_key, self._active_model)
            elif p == "openrouter":
                resp = ask_api(PROVIDERS[p]["url"], self.api_key, self.messages, self._active_model,
                    {"HTTP-Referer": "https://github.com/overdause91-del/CodeEZ"})
            else:
                resp = ask_api(PROVIDERS[p]["url"], self.api_key, self.messages, self._active_model)
            self.root.after(0, self._on_response, resp)
        except Exception as e:
            err = str(e)
            if hasattr(e, "code"):
                try: err += ": " + e.read().decode()
                except: pass
            self.root.after(0, self._on_error, err)

    def _on_response(self, resp):
        self.messages.append({"role": "assistant", "content": resp})
        self.add_bubble("bot", resp)
        self.send_btn.config(state=tk.NORMAL, text=">")

    def _on_error(self, err):
        self.add_bubble("bot", "Erreur: " + err[:200])
        self.messages.pop() if self.messages else None
        self.send_btn.config(state=tk.NORMAL, text=">")

    def _open_settings(self):
        SettingsWindow(self.root, self)

    def run(self):
        self.root.mainloop()


class SettingsWindow:
    def __init__(self, parent, app):
        self.app = app
        win = tk.Toplevel(parent)
        win.title("Configuration")
        win.geometry("460x420")
        win.configure(bg=C_BG)
        win.transient(parent)
        win.grab_set()

        main = tk.Frame(win, bg=C_BG, padx=20, pady=16)
        main.pack(fill=tk.BOTH, expand=True)

        tk.Label(main, text="Fournisseur LLM", font=("Segoe UI", 13, "bold"),
            fg=C_TEXT, bg=C_BG).pack(anchor=tk.W)

        nb = ttk.Notebook(main)
        nb.pack(fill=tk.BOTH, expand=True, pady=12)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=C_BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=C_BG2, foreground=C_TEXT, padding=[12, 6])
        style.map("TNotebook.Tab", background=[("selected", C_SURFACE)])

        keys = list(PROVIDERS.keys())
        if app._active_provider in keys and app._active_provider != "ollama":
            keys.remove(app._active_provider)
            keys.insert(0, app._active_provider)

        for pid in keys:
            self._add_tab(nb, pid, app)

        tk.Button(main, text="Fermer", command=win.destroy,
            bg=C_SURFACE, fg=C_TEXT, bd=0, padx=20, pady=6, cursor="hand2").pack()

    def _add_tab(self, nb, pid, app):
        info = PROVIDERS.get(pid)
        if not info:
            return
        frame = tk.Frame(nb, bg=C_BG, padx=12, pady=12)
        nb.add(frame, text=info["name"].split(" (")[0])

        tk.Label(frame, text=info["name"], font=("Segoe UI", 11, "bold"),
            fg=C_PRIMARY, bg=C_BG).pack(anchor=tk.W)

        tk.Label(frame, text="Modele: " + info["default_model"],
            font=("Segoe UI", 9), fg=C_TEXT2, bg=C_BG).pack(anchor=tk.W, pady=(0, 8))

        if pid == "ollama":
            tk.Label(frame, text="LLM local 100% gratuit", font=("Segoe UI", 10),
                fg=C_TEXT, bg=C_BG).pack(anchor=tk.W, pady=4)
            tk.Label(frame, text="1. Installe Ollama depuis ollama.ai", fg=C_TEXT, bg=C_BG, anchor="w").pack(fill=tk.X, pady=1)
            tk.Label(frame, text='2. Dans un terminal: ollama pull deepseek-coder:6.7b', fg=C_TEXT, bg=C_BG, anchor="w").pack(fill=tk.X, pady=1)
            tk.Label(frame, text="3. Lance Ollama", fg=C_TEXT, bg=C_BG, anchor="w").pack(fill=tk.X, pady=1)
            detect_btn = tk.Button(frame, text="Detecter Ollama",
                bg=C_SURFACE, fg=C_TEXT, bd=0, padx=12, pady=4, cursor="hand2")
            detect_btn.pack(pady=12)
            def detect():
                ok, models = check_ollama()
                if ok and models:
                    app._active_provider = "ollama"
                    app._active_model = models[0]
                    app.api_key = ""
                    app.cfg["default_provider"] = "ollama"
                    app.cfg["default_model"] = models[0]
                    save_config(app.cfg)
                    app.mode_label.config(text="Ollama " + models[0])
                    app.status_btn.config(text="Ollama: " + models[0], fg="#4caf50")
                    app.add_bubble("bot", "Ollama connecte avec " + models[0] + " !")
                else:
                    app.add_bubble("bot", "Ollama non trouve. Installe-le depuis ollama.ai")
            detect_btn.config(command=detect)
            return

        tuto_frame = tk.Frame(frame, bg=C_BG2, padx=12, pady=8)
        tuto_frame.pack(fill=tk.X, pady=8)

        for line in info["tuto"].split("\n"):
            tk.Label(tuto_frame, text=line, fg=C_TEXT, bg=C_BG2, anchor="w").pack(fill=tk.X)

        tk.Label(frame, text="Cle API:", fg=C_TEXT, bg=C_BG).pack(anchor=tk.W, pady=(8, 2))

        entry_frame = tk.Frame(frame, bg=C_BG)
        entry_frame.pack(fill=tk.X)

        entry = tk.Entry(entry_frame, bg=C_INPUT, fg=C_TEXT, bd=0, font=("Segoe UI", 10),
            insertbackground=C_TEXT, show="*")
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 8))
        existing = app._get_key(pid)
        if existing:
            entry.insert(0, existing)

        def save():
            key = entry.get().strip()
            if not key:
                return
            app.cfg[f"{pid}_key"] = key
            app.cfg["default_provider"] = pid
            app.cfg["default_model"] = info["default_model"]
            save_config(app.cfg)
            app.api_key = key
            app._active_provider = pid
            app._active_model = info["default_model"]
            app.mode_label.config(text=info["name"])
            app.status_btn.config(text=info["name"] + ": OK", fg="#4caf50")
            app.add_bubble("bot", "Provider change: " + info["name"])

        btn_frame = tk.Frame(entry_frame, bg=C_BG)
        btn_frame.pack(side=tk.RIGHT)

        show_var = tk.BooleanVar()
        show_btn = tk.Button(btn_frame, text="Afficher", bg=C_SURFACE, fg=C_TEXT, bd=0,
            padx=8, cursor="hand2", command=lambda: entry.config(show="" if show_var.get() else "*") or show_var.set(not show_var.get()))
        show_btn.pack(side=tk.LEFT, padx=2)

        save_btn = tk.Button(btn_frame, text="OK", bg=C_PRIMARY, fg="white", bd=0,
            padx=12, cursor="hand2", command=save)
        save_btn.pack(side=tk.LEFT, padx=2)


def main():
    ChatApp().run()

if __name__ == "__main__":
    main()
