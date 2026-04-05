# Agentes de IA no MYC

O MYC agora integra agentes de IA como parte do seu workflow. Cada agente e um perfil configurado com variaveis de ambiente, plataforma, diretorio de trabalho e contexto inicial.

## Visao Geral

```
┌─────────────────────────────────────────────────────┐
│                    MYC CLI                          │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │ Rotinas  │──│ Agente   │──│ Plugins (hooks)  │   │
│  │ (urls,   │  │ (IA)     │  │ (contexto extra) │   │
│  │ apps)    │  │          │  │                  │   │
│  └──────────┘  └──────────┘  └──────────────────┘   │
│       │              │               │               │
│       │              │               │               │
│       ▼              ▼               ▼               │
│  Abre browsers   Lanca IA       Injeta info        │
│  e apps          no terminal    no contexto        │
└─────────────────────────────────────────────────────┘
```

## Agent Default

Ja configurado na sua maquina com OpenRouter + `qwen/qwen3.6-plus:free`:

```powershell
myc agent launch default
```

## Comandos Disponiveis

| Comando | Descricao |
|---------|-----------|
| `myc agent add` | Wizard para criar novo agente |
| `myc agent list` | Lista agentes configurados |
| `myc agent launch <nome>` | Lanca o agente (abre terminal da IA) |
| `myc agent delete <nome>` | Remove agente |
| `myc agent history` | Historico de uso (data, agente, status) |
| `myc agent plugins` | Lista plugins instalados |
| `myc agent plugin-add` | Cria plugin customizado |
| `myc agent bundle-install --all` | Instala todos os bundles de plugins |
| `myc agent bundle-install <id>` | Instala bundle especifico |
| `myc agent bundles` | Lista bundles disponiveis |
| `myc agent install-plugin <arquivo>` | Instala plugin de um arquivo .py |
| `myc automate <agente> --group X` | Lanca agente com contexto de rotinas MYC |

## Plataformas Suportadas

| Plataforma | Como Funciona | Comando |
|-----------|---------------|---------|
| **OpenClaude** | Qualquer modelo via OpenAI API (OpenRouter, Ollama, Gemini) | `openclaude` |
| **Cursor** | Editor de codigo com IA integrada | `cursor .` |
| **VS Code + Copilot** | GitHub Copilot no VS Code | `code .` |
| **OpenAI Codex CLI** | CLI da OpenAI para coding | `codex` |
| **Custom** | Qualquer comando de sua escolha | Configuravel |

## Integracao com Rotinas MYC

Ao lancá um agente com `myc automate`, as rotinas MYC sao injetadas como contexto:

```powershell
# Lanca o agente default com rotinas do grupo 'estudar' como contexto
myc automate default --group estudar

# Filtra por subcomando especifico
myc automate default --group trabalhar --subcommand daily-standup
```

O agente recebe no CLAUDE.md:
- Lista de todas as rotinas configuradas
- Dias da semana de cada rotina
- URLs e apps que serao abertos
- Numero de acoes por rotina

## Historico

Cada lancamento gera um registro com data, agente, plataforma, diretorio, rotina e status:

```powershell
myc agent history               # ultimas 20 entradas
myc agent history -a default    # filtrar por agente
myc agent history -n 50         # mais entradas
```

---
