const vscode = require('vscode');

function activate(context) {
    const provider = new CodeEZViewProvider(context);
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('codeez.chat', provider)
    );
    context.subscriptions.push(
        vscode.commands.registerCommand('codeez.openChat', () => {
            vscode.commands.executeCommand('workbench.view.extension.codeez-chat');
        })
    );
}
exports.activate = activate;

class CodeEZViewProvider {
    constructor(context) {
        this.context = context;
        this._view = null;
    }

    resolveWebviewView(webviewView) {
        this._view = webviewView;
        webviewView.webview.options = { enableScripts: true };
        webviewView.webview.html = this._getHtml(webviewView.webview);

        webviewView.webview.onDidReceiveMessage(async (msg) => {
            if (msg.type === 'sendMessage') {
                const config = vscode.workspace.getConfiguration('codeez');
                const provider = msg.provider || 'deepseek';
                const model = msg.model || 'deepseek-chat';
                const messages = msg.messages;
                let apiKey = config.get(provider + 'Key') || '';
                if (provider === 'openrouter') {
                    apiKey = config.get('openrouterKey') || '';
                }

                if (!apiKey) {
                    webviewView.webview.postMessage({ type: 'error', text: 'Configure ta cle API dans les parametres (Ctrl+,) > CodeEZ' });
                    return;
                }

                try {
                    let resp;
                    if (provider === 'anthropic') {
                        resp = await this._askAnthropic(apiKey, messages, model);
                    } else if (provider === 'google') {
                        resp = await this._askGoogle(apiKey, messages, model);
                    } else {
                        resp = await this._askOpenAI(provider, apiKey, messages, model);
                    }
                    webviewView.webview.postMessage({ type: 'response', text: resp });
                } catch (err) {
                    webviewView.webview.postMessage({ type: 'error', text: err.message || String(err) });
                }
            } else if (msg.type === 'checkOllama') {
                try {
                    const resp = await this._fetch('http://localhost:11434/api/tags');
                    const data = JSON.parse(resp);
                    const models = (data.models || []).map(m => m.name);
                    webviewView.webview.postMessage({ type: 'ollamaStatus', ok: true, models });
                } catch {
                    webviewView.webview.postMessage({ type: 'ollamaStatus', ok: false, models: [] });
                }
            } else if (msg.type === 'openSettings') {
                vscode.commands.executeCommand('workbench.action.openSettings', 'codeez');
            }
        });
    }

    async _askOpenAI(provider, apiKey, messages, model) {
        const urls = {
            deepseek: 'https://api.deepseek.com/v1/chat/completions',
            openai: 'https://api.openai.com/v1/chat/completions',
            openrouter: 'https://openrouter.ai/api/v1/chat/completions',
        };
        const url = urls[provider] || urls.deepseek;
        const body = { model, messages };
        const resp = await this._fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + apiKey },
            body: JSON.stringify(body),
        });
        return JSON.parse(resp).choices[0].message.content;
    }

    async _askAnthropic(apiKey, messages, model) {
        const resp = await this._fetch('https://api.anthropic.com/v1/messages', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'x-api-key': apiKey, 'anthropic-version': '2023-06-01' },
            body: JSON.stringify({ model, max_tokens: 4096, messages }),
        });
        return JSON.parse(resp).content[0].text;
    }

    async _askGoogle(apiKey, messages, model) {
        const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`;
        const contents = messages.map(m => ({ role: m.role, parts: [{ text: m.content }] }));
        const resp = await this._fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ contents }),
        });
        return JSON.parse(resp).candidates[0].content.parts[0].text;
    }

    async _fetch(url, opts = {}) {
        const response = await fetch(url, opts);
        if (!response.ok) {
            const text = await response.text();
            throw new Error(`HTTP ${response.status}: ${text.slice(0, 200)}`);
        }
        return response.text();
    }

    _getHtml(webview) {
        const styleUri = webview.asWebviewUri(vscode.Uri.joinPath(this.context.extensionUri, 'media', 'style.css'));
        const scriptUri = webview.asWebviewUri(vscode.Uri.joinPath(this.context.extensionUri, 'media', 'main.js'));
        return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <link rel="stylesheet" href="${styleUri}">
</head>
<body>
  <div id="app">
    <div id="header">
      <span id="title">CodeEZ</span>
      <span id="status"></span>
    </div>
    <div id="chat"></div>
    <div id="input-bar">
      <textarea id="input" rows="2" placeholder="Pose ta question..."></textarea>
      <button id="send-btn">></button>
    </div>
    <div id="bottom-bar">
      <span id="provider-label">deepseek</span>
      <button id="config-btn"></button>
    </div>
  </div>
  <script src="${scriptUri}"></script>
</body>
</html>`;
    }
}
exports.deactivate = function () {};
