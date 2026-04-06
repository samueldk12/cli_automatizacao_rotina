# Guia de Configuracao do OpenRouter + OpenClaude

## Passo 1: Instalar o OpenClaude

### Via npm
```powershell
npm install -g @gitlawb/openclaude
```

### Via MYC
```powershell
myc install openclaude
```

Tutorial em video: https://www.youtube.com/watch?v=AxE8gDFeMic

---

## Passo 2: Criar conta no OpenRouter

1. Acesse https://openrouter.ai/
2. Clique em **Sign In** (Google, GitHub, ou Discord)
3. Va para https://openrouter.ai/keys
4. Clique em **Create Key**
5. Copie a chave gerada (formato: `sk-or-v1-...`)

---

## Passo 3: Configurar o MYC

```powershell
myc install openclaude
```

O wizard vai pedir sua API Key e o modelo desejado.

---

## Modelos Disponiveis no OpenRouter

| Modelo | Provedor | Preco | Uso Ideal |
|--------|----------|-------|-----------|
| `qwen/qwen3.6-plus:free` | Qwen | Gratuito | Uso geral, coding |
| `deepseek/deepseek-chat-v3-0324:free` | DeepSeek | Gratuito | Coding, raciocinio |
| `google/gemini-2.5-pro` | Google | Pago | Multimodal |
| `openai/gpt-4o` | OpenAI | Pago | Uso geral |
| `anthropic/claude-sonnet-4-6-20250514` | Anthropic | Pago | Coding |

---

## Variaveis de Ambiente (manual)

```powershell
$env:CLAUDE_CODE_USE_OPENAI="1"
$env:OPENAI_BASE_URL="https://openrouter.ai/api/v1"
$env:OPENAI_API_KEY="sk-or-v1-SUA_CHAVE_AQUI"
$env:OPENAI_MODEL="qwen/qwen3.6-plus:free"

openclaude
```

---

## Comandos

```powershell
# Lancar agente padrao
myc agent launch default

# Lista agentes
myc agent list

# Ver historico
myc agent history

# Instalar plugins
myc agent bundle-install --all
```
