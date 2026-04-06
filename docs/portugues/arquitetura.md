# Arquitetura MYC

## Visao Geral do Sistema

O MYC e composto por tres camadas independentes mas complementares:

```
┌─────────────────────────────────────────────────────┐
│                   MYC CLI                           │
│                                                     │
│  ┌───────────────────────────────────────────┐      │
│  │         Camada de Rotinas                  │      │
│  │  Grupos → Subcomandos → Dias → Acoes       │      │
│  │  (abrir URLs, apps, posicionar janelas)   │      │
│  └──────────────┬────────────────────────────┘      │
│                 │                                    │
│  ┌──────────────▼────────────────────────────┐      │
│  │         Camada de Agentes                  │      │
│  │  Perfis → Plataforma → env → Contexto      │      │
│  │  (lancar agentes IA com contexto MYC)     │      │
│  └──────────────┬────────────────────────────┘      │
│                 │                                    │
│  ┌──────────────▼────────────────────────────┐      │
│  │         Camada de Plugins                  │      │
│  │  Specialists + Companies + Departments     │      │
│  │  + Middlewares (componiveis)               │      │
│  └───────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────┘
```

## Camada 1: Gerenciador de Rotinas

**Proposito:** Automatizar a tarefa diaria de abrir os mesmos apps, URLs e abas do navegador.

### Como Funciona

1. Grupos sao registrados em `~/.myc/config.json`
2. Cada grupo contem subcomandos com:
   - Dias da semana disponiveis
   - Acoes (URLs do navegador ou caminhos de apps com monitor alvo)
3. Scripts de atalho sao gerados em `~/.myc/bin/`
4. Quando executado, o CLI abre URLs nos navegadores especificados nos monitores determinados

### Fluxo de Dados

```
config.json → runner.py → launch browser/app → posicionamento de janela (Win32 API)
    │
    ├── assistente add (questionary)
    ├── navegacao TUI
    └── scripts de atalho (.bat / .ps1)
```

## Camada 2: Gerenciamento de Agentes

**Proposito:** Gerenciar perfis de agentes IA que integram com diversas plataformas.

### Plataformas Suportadas

| Plataforma | Binario | Descricao |
|------------|---------|-----------|
| OpenClaude | `openclaude` | Qualquer modelo via API compativel com OpenAI |
| Cursor | `cursor` | Editor de codigo com IA |
| VS Code + Copilot | `code` | GitHub Copilot |
| OpenAI Codex | `codex` | CLI da OpenAI para programacao |
| Custom | Definido pelo usuario | Qualquer comando |

### Ciclo de Vida do Agente

```
1. Criar agente (wizard) → agents.json
2. Lancar agente → executa binario da plataforma
3. Injetar CLAUDE.md → arquivo de contexto com perfil + tarefas MYC
4. Executar plugins → hooks PRE_LAUNCH disparam
5. Usuario interage com IA
6. Registrar historico → history.json
```

## Camada 3: Sistema de Plugins

**O grande diferencial.** Uma arquitetura de plugins componivel com quatro tipos que podem ser misturados em qualquer nivel.

### Tipos de Plugin

#### 1. Specialists (65 plugins)

A unidade atomica. Um unico agente especialista com conhecimento profundo em uma area.

```
Execucao: PRE_LAUNCH → Agente executa com CONTEXT() → POST_LAUNCH
```

Cada specialist exporta:
- `NAME` — Nome exibido
- `DESCRIPTION` — Descricao curta
- `PRE_LAUNCH(profile)` — Hook antes do agente iniciar
- `CONTEXT(profile)` — Retorna texto de contexto para CLAUDE.md
- `POST_LAUNCH(profile)` — Hook pos-execucao (opcional)

#### 2. Companies (27 plugins)

Organizacoes multi-agente, cada uma com 3-8 sub-agentes. Sub-agentes podem reutilizar specialists existentes.

```
Contexto da Empresa → Papel do Sub-agente → Specialists Reutilizados → Pipeline de Middlewares
```

Cada company exporta:
- `NAME` — Nome da empresa
- `DESCRIPTION` — O que a empresa faz
- `SPECIALISTS` — Lista de sub-agentes com seus papeis e specialists referenciados
- `COMPANY_CONTEXT()` — Contexto geral da empresa

#### 3. Departments (13 plugins)

Equipes independentes ou vinculadas a empresas. Um departamento coordena especialistas de um dominio.

```
ROLE do Departamento → Lista de specialists → Pipeline de middlewares → Saida consolidada
```

Cada department exporta:
- `NAME` — Nome do departamento
- `DESCRIPTION` — Descricao
- `SPECIALISTS` — Lista de IDs de specialists
- `MIDDLEWARES` — Middlewares padrao
- `PARENT_COMPANY` — ID da empresa pai ou None
- `ROLE` — System prompt completo
- `DEPARTMENT_CONTEXT()` — Contexto adicional

#### 4. Middlewares (8 plugins)

Modificadores de prompt/saida anexaveis em qualquer nivel: specialist, company, department.

```
Consulta → [Middlewares PRE] → Specialist → LLM → [Middlewares POST] → Saida
```

Tipos:
- `prompt_modifier` — Modifica o prompt de entrada (PRE)
- `output_modifier` — Modifica o texto de saida (POST)
- `content_filter` — Modifica entrada E filtra saida (BOTH)
- `agent_runner` — Executa sub-agente como middleware (MANUAL)

### Pipeline de Execucao

```
Consulta do Usuario ("crie uma API REST")
       │
       ▼
┌──────────────────┐
│  PROMPT_MODIFY   │  ← prompt_enhancer reestrutura consulta
│    (PRE)         │     com contexto, objetivos, diretrizes
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Departamento   │  ← Injeta ROLE + lista de specialists
│   (opcional)     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│     Empresa      │  ← Adiciona contexto organizacional
│   (opcional)     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Specialist     │  ← Injeta CONTEXT() + PRE_LAUNCH
│   Selecionado    │     System prompt final montado
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│    LLM (IA)      │  ← Geracao da resposta
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  OUTPUT_MODIFY   │  ← code_quality, summarizer, text_compressor
│    (POST)        │     analisam, comprimem, resumem
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  POST_LAUNCH     │  ← Salva arquivos, gera artefatos
└────────┬─────────┘
         │
         ▼
   Saida Final
```

### Composicao entre Plugins

Plugins ganham poder extraordinario quando combinados:

```bash
# Specialist + 2 middlewares
myc agent-specialist backend_dev -o prompt_enhancer -o code_quality "implemente auth JWT"

# Sub-agente de empresa + middleware
myc agent-company dev_agency dev_frontend -o code_quality "crie dashboard admin"

# Departamento + contexto de empresa + middleware
myc agent-department dev_backend -c dev_agency -o prompt_enhancer "refatore API"

# Empresa sem sub-agente (lista disponiveis)
myc agent-company dev_agency
```

## Instalacao e Ciclo de Vida de Plugins

### Instalacao de Bundles

```bash
# Instalar todos os bundles de especialistas
myc agent bundle-install --all

# Instalar bundle especifico
myc agent bundle-install fullstack

# Listar bundles disponiveis
myc agent bundle-list
```

### Auto-Instalacao

Quando uma empresa, departamento ou middleware e usado pela primeira vez, seus plugins sao copiados automaticamente do diretorio `plugins/` integrado para `~/.myc/agents/`.

### Wizards de Criacao de Plugins

```bash
myc agent plugin-add        # Criar plugin specialist
myc agent company-add       # Criar plugin company
myc agent department-add    # Criar plugin department
```

## Arquivos de Configuracao

| Arquivo | Localizacao | Finalidade |
|---------|-------------|------------|
| `config.json` | `~/.myc/config.json` | Definicoes de rotinas |
| `agents.json` | `~/.myc/agents/agents.json` | Perfis de agentes |
| `history.json` | `~/.myc/agents/history.json` | Historico de lancamentos |
| `plugin_registry.json` | `~/.myc/agents/plugin_registry.json` | Registro de plugins |

### Estrutura de Diretorios

```
~/.myc/
├── config.json
├── bin/                        # Atalhos gerados
│   ├── estudar.bat
│   ├── estudar.ps1
│   └── ...
└── agents/
    ├── agents.json
    ├── history.json
    ├── plugins/                # Specialists instalados
    ├── companies/              # Empresas instaladas
    ├── departments/            # Departamentos instalados
    └── middlewares/            # Middlewares instalados
```
