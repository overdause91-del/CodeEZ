const vscode = acquireVsCodeApi();
let messages = [];
let provider = 'deepseek';
let model = 'deepseek-chat';
let configOpen = false;

const PROVIDERS = {
    deepseek: {
        name: 'DeepSeek', models: ['deepseek-chat', 'deepseek-reasoner'], defaultModel: 'deepseek-chat',
        tuto: '1. Va sur platform.deepseek.com/api_keys\n2. Cree un compte\n3. Copie ta cle (sk-...)'
    },
    openai: {
        name: 'OpenAI', models: ['gpt-4o', 'gpt-4o-mini'], defaultModel: 'gpt-4o-mini',
        tuto: '1. Va sur platform.openai.com/api-keys\n2. Cree une key\n3. Copie (sk-...)'
    },
    anthropic: {
        name: 'Claude', models: ['claude-sonnet-4-20250514', 'claude-3-5-sonnet-20241022'], defaultModel: 'claude-sonnet-4-20250514',
        tuto: '1. Va sur console.anthropic.com/settings/keys\n2. Create Key\n3. Copie (sk-ant-...)'
    },
    google: {
        name: 'Gemini', models: ['gemini-2.5-flash', 'gemini-2.5-pro'], defaultModel: 'gemini-2.5-flash',
        tuto: '1. Va sur aistudio.google.com/apikey\n2. Create API Key\n3. Copie (AIza...)'
    },
    openrouter: {
        name: 'OpenRouter', models: ['deepseek/deepseek-chat', 'openai/gpt-4o-mini', 'anthropic/claude-sonnet-4'], defaultModel: 'deepseek/deepseek-chat',
        tuto: '1. Va sur openrouter.ai/keys\n2. Create Key\n3. Copie (sk-or-...)'
    },
    ollama: {
        name: 'Ollama (local)', models: [], defaultModel: '',
        tuto: '1. Installe Ollama depuis ollama.ai\n2. Dans un terminal: ollama pull deepseek-coder:6.7b\n3. Lance Ollama'
    }
};

window.onload = () => {
    const chat = document.getElementById('chat');
    const input = document.getElementById('input');
    const sendBtn = document.getElementById('send-btn');
    const status = document.getElementById('status');
    const configBtn = document.getElementById('config-btn');
    const providerLabel = document.getElementById('provider-label');

    addBubble('bot', 'Bienvenue dans CodeEZ !');
    addBubble('bot', 'Detection d\'Ollama...');
    vscode.postMessage({ type: 'checkOllama' });

    sendBtn.onclick = sendMessage;
    input.onkeydown = (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } };

    configBtn.onclick = toggleConfig;

    window.addEventListener('message', (e) => {
        const msg = e.data;
        if (msg.type === 'response') {
            messages.push({ role: 'assistant', content: msg.text });
            addBubble('bot', msg.text);
            sendBtn.disabled = false;
            sendBtn.textContent = '>';
            input.disabled = false;
            input.focus();
        } else if (msg.type === 'error') {
            addBubble('error', msg.text);
            sendBtn.disabled = false;
            sendBtn.textContent = '>';
            input.disabled = false;
        } else if (msg.type === 'ollamaStatus') {
            if (msg.ok && msg.models.length > 0) {
                provider = 'ollama';
                model = msg.models[0];
                providerLabel.textContent = 'Ollama: ' + msg.models[0];
                status.textContent = 'Ollama ✓';
                status.style.color = '#4caf50';
                addBubble('bot', 'Ollama connecte avec ' + msg.models[0] + ' !');
            } else {
                providerLabel.textContent = 'DeepSeek (gratuit)';
                status.textContent = '';
                status.style.color = '#888';
                addBubble('bot', 'Ollama non trouve. Configure une cle DeepSeek gratuite.');
                createConfigPanel();
            }
        }
    });

    let configPanel = null;
    function toggleConfig() {
        if (!configPanel) createConfigPanel();
        configPanel.style.display = configPanel.style.display === 'none' ? 'flex' : 'none';
    }

    function createConfigPanel() {
        configPanel = document.createElement('div');
        configPanel.className = 'config-panel';
        configPanel.style.display = 'none';

        const sel = document.createElement('select');
        Object.keys(PROVIDERS).forEach(k => {
            const opt = document.createElement('option');
            opt.value = k;
            opt.textContent = PROVIDERS[k].name;
            sel.appendChild(opt);
        });
        sel.value = provider;
        configPanel.appendChild(sel);

        const modelSel = document.createElement('select');
        modelSel.id = 'model-select';
        configPanel.appendChild(modelSel);

        const tutoDiv = document.createElement('div');
        tutoDiv.className = 'tuto';
        configPanel.appendChild(tutoDiv);

        const keyInput = document.createElement('input');
        keyInput.type = 'text';
        keyInput.placeholder = 'Colle ta cle API ici...';
        configPanel.appendChild(keyInput);

        const btnRow = document.createElement('div');
        btnRow.style.display = 'flex';
        btnRow.style.gap = '8px';

        const saveBtn = document.createElement('button');
        saveBtn.textContent = 'OK';
        btnRow.appendChild(saveBtn);

        if (provider === 'ollama' || sel.value === 'ollama') {
            const detectBtn = document.createElement('button');
            detectBtn.textContent = 'Detecter Ollama';
            btnRow.appendChild(detectBtn);
            detectBtn.onclick = () => vscode.postMessage({ type: 'checkOllama' });
        }

        const settingsBtn = document.createElement('button');
        settingsBtn.textContent = 'Parametres';
        btnRow.appendChild(settingsBtn);
        settingsBtn.onclick = () => vscode.postMessage({ type: 'openSettings' });

        configPanel.appendChild(btnRow);

        function updateModelList() {
            const p = sel.value;
            const info = PROVIDERS[p];
            modelSel.innerHTML = '';
            if (p === 'ollama') {
                modelSel.innerHTML = '<option>Detecte automatiquement</option>';
                tutoDiv.textContent = info.tuto;
                keyInput.style.display = 'none';
                return;
            }
            keyInput.style.display = 'block';
            info.models.forEach(m => {
                const opt = document.createElement('option');
                opt.value = m;
                opt.textContent = m;
                modelSel.appendChild(opt);
            });
            modelSel.value = info.defaultModel;
            tutoDiv.textContent = info.tuto;
        }

        sel.onchange = () => {
            updateModelList();
            if (sel.value === 'ollama') {
                btnRow.querySelector('button:last-child')?.remove();
            }
        };
        updateModelList();

        saveBtn.onclick = () => {
            provider = sel.value;
            model = provider === 'ollama' ? 'detect' : modelSel.value;
            providerLabel.textContent = PROVIDERS[provider].name;
            if (provider !== 'ollama' && keyInput.value.trim()) {
                vscode.postMessage({ type: 'saveKey', provider, key: keyInput.value.trim() });
            }
            configPanel.style.display = 'none';
        };

        document.getElementById('app').appendChild(configPanel);
    }

    function sendMessage() {
        const text = input.value.trim();
        if (!text) return;
        input.value = '';
        messages.push({ role: 'user', content: text });
        addBubble('user', text);
        sendBtn.disabled = true;
        sendBtn.textContent = '...';
        input.disabled = true;

        vscode.postMessage({
            type: 'sendMessage',
            provider,
            model,
            messages: messages.map(m => ({ role: m.role, content: m.content }))
        });
    }

    function addBubble(role, text) {
        const div = document.createElement('div');
        div.className = 'msg ' + role;
        div.textContent = text;
        chat.appendChild(div);
        chat.scrollTop = chat.scrollHeight;
    }
};
