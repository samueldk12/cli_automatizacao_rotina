# MYC — My Commands

> CLI toolkit for routine automation, multi-monitor app orchestration, and a composable AI agent system with 121 plugins.

---

## Overview

MYC solves two problems in one tool:

1. **Routine Automation** — Register groups of commands (URLs, apps, browsers) organized by day of the week, launch them with a single command, and position windows across multiple monitors.
2. **AI Agent System** — Deploy a modular plugin architecture with 69 specialists, 27 companies, 14 departments, and 11 middlewares that compose into teams of specialized AI agents.

## Table of Contents

- [Quick Start](#quick-start)
- [Command Reference](#command-reference)
- [Documentation in Other Languages](#documentation-in-other-languages)
- [How the Routine System Works](#how-the-routine-system-works)
- [How the AI Agent System Works](#how-the-ai-agent-system-works)
- [Agent Architecture](#agent-architecture)
- [Specialists (69 plugins)](#specialists-69-plugins)
- [Companies (27 plugins)](#companies-27-plugins)
- [Departments (14 plugins)](#departments-14-plugins)
- [Middlewares (11 plugins)](#middlewares-11-plugins)
- [Plugin Interface](#plugin-interface)
- [Agent Profiles & Platforms](#agent-profiles--platforms)
- [Configuration Structure](#configuration-structure)
- [Directory Layout](#directory-layout)
- [Dependencies & Build](#dependencies--build)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Quick Start

### 1. Install

```powershell
git clone https://github.com/samueldk12/cli_automatizacao_rotina.git
cd cli_automatizacao_rotina
.\install.ps1
```

Or manually:

```powershell
pip install -e .
myc setup --auto   # adds ~/.myc/bin to your PATH
# then restart your terminal
```

### 2. Install AI Agent Platform (optional)

```powershell
myc install openclaude    # installs OpenClaude + configures your API key
myc agent bundle-install --all    # installs all 69 specialist plugins
```

### 3. Create Your First Routine

```powershell
myc add    # interactive wizard
# → pick a group name (e.g., "work")
# → add subcommands with URLs/apps
# → choose days of the week
# MYC generates shortcut scripts automatically

# Then run it:
work open-email    # opens your configured URLs/apps
```

### 4. Query an AI Specialist

```powershell
myc agent-specialist frontend_dev "build a responsive login form with validation"
myc agent-specialist social_media "create a 30-day content calendar for Instagram"
```

### 5. Launch a Multi-Agent Company

```powershell
myc agent-company dev_agency tech_lead "architect a microservices backend"
myc agent-company bounty_company recon_specialist "map the attack surface of example.com"
```

---

## Command Reference

### Routine Management

| Command | Description |
|---------|-------------|
| `myc add` | Create a new routine command (interactive wizard) |
| `myc list` | List all registered commands |
| `myc list -g <group>` | List commands in a specific group |
| `myc run <group> <cmd>` | Execute a routine |
| `myc run <group> <day> <cmd>` | Execute a routine with day filter |
| `myc tui` | Open interactive terminal navigation |
| `myc tui --group <group>` | Open TUI filtered to a group |
| `myc edit <group> <cmd>` | Edit an existing command |
| `myc delete <group> <cmd>` | Remove a subcommand |
| `myc delete <group>` | Remove an entire group |
| `myc monitors` | List detected monitors with resolution/position |
| `myc setup` | Generate shortcut scripts for all groups |
| `myc setup --auto` | Generate scripts and add to Windows PATH |
| `myc config` | Configure global settings (e.g. Chrome path) |
| `myc config-html` | Open web dashboard at localhost:8787 |

### Agent Management

| Command | Description |
|---------|-------------|
| `myc install openclaude` | Install and configure the OpenClaude AI platform |
| `myc agent add` | Create a new AI agent profile (wizard) |
| `myc agent list` | List all configured agents |
| `myc agent launch <name>` | Launch an agent in its working directory |
| `myc agent launch <name> --cwd <dir>` | Launch an agent in a specific directory |
| `myc agent delete <name>` | Remove an agent |
| `myc agent history` | Show launch history |
| `myc agent history -a <name>` | Filter history by agent |
| `myc agent plugins` | List installed specialist plugins |
| `myc agent plugin-add` | Create a custom specialist plugin (wizard) |
| `myc agent company-add` | Create a custom company plugin (wizard) |
| `myc agent department-add` | Create a custom department plugin (wizard) |
| `myc agent bundle-install --all` | Install all specialist bundles |
| `myc agent bundle-install <id>` | Install a specific bundle |
| `myc agent bundle-list` | List available specialist bundles |
| `myc agent bundle-list --company` | List available company bundles |
| `myc agent middleware --list` | List all available middlewares |
| `myc automate <agent> --group <g>` | Launch agent with MYC routines as context |

### Direct Plugin Invocation

| Command | Description |
|---------|-------------|
| `myc agent-specialist <name> "query"` | Query an individual specialist |
| `myc agent-specialist <name> -o <mw> "query"` | Query with middleware pipeline |
| `myc agent-company <company> [sub] "query"` | Query a company (sub-agent optional) |
| `myc agent-department <dept> "query"` | Query a department/team |
| `myc agent-department <dept> -c <company> "query"` | Query department within company context |
| `myc agent-department --list` | List all available departments |

---

## Documentation in Other Languages

| Language | Location | Files |
|----------|----------|-------|
| English | `docs/english/` | [Getting Started](docs/english/getting-started.md), [Architecture](docs/english/architecture.md), [Use Cases](docs/english/use_cases.md) |
| Portuguese | `docs/portugues/` | [Introdução](docs/portugues/introducao.md), [Arquitetura](docs/portugues/arquitetura.md), [Casos de Uso](docs/portugues/casos_de_uso.md) |
| Use Cases (PT) | `docs/agentes/` | [Casos de Uso](docs/agentes/use_cases.md) — including how an AI Company documented this project |

---

## How the Routine System Works

### The Problem

You open the same set of websites and apps every day — email, Slack, Jira, your course, your editor — scattered across multiple monitors. You waste 2-5 minutes per day arranging them. Over a year, that's 12+ hours.

### The Solution

1. **Register** your routines once with `myc add`
2. **Organize** by day (e.g., Monday = gym + standup, Friday = review + planning)
3. **Launch** with a single word — all URLs and apps open in the right monitors

### Example

```jsonc
// ~/.myc/config.json (simplified)
{
  "commands": {
    "work": {
      "description": "Workday tools",
      "subcommands": {
        "open-email": {
          "description": "Open email + Slack + Jira",
          "days": [],              // empty = every day
          "actions": [
            {
              "type": "browser",
              "url": "https://mail.google.com",
              "monitor": 0,         // first monitor
              "new_window": true,
              "browser": "chrome"
            },
            {
              "type": "browser",
              "url": "https://app.slack.com",
              "monitor": 1,         // second monitor
              "new_window": true,
              "browser": "chrome"
            }
          ]
        }
      }
    }
  }
}
```

```powershell
# Type this once. It opens both windows in the right monitors.
work open-email
```

### How Shortcut Scripts Work

When you run `myc setup`, shortcut scripts are generated:

| Script | What it does |
|--------|-------------|
| `estudar` (no args) | Opens TUI filtered to the "estudar" group |
| `estudar visao` | Runs `myc run estudar visao-computacional` directly |
| `estudar segunda visao` | Runs with day filter: `myc run estudar segunda visao-computacional` |

These scripts are placed in `~/.myc/bin/` and added to PATH, so you can invoke them from anywhere.

---

## How the AI Agent System Works

### The Problem

A single "chat with AI" prompt can't match the quality of a team where each member has a specific role, specialized knowledge, and a defined workflow.

### The Solution

Four plugin types that compose into teams:

| Layer | Type | Count | Analogy |
|-------|------|-------|---------|
| **Specialist** | Individual expert | 69 | A senior consultant in one domain |
| **Company** | Multi-agent org | 27 | A company with sub-teams, each reusing specialists |
| **Department** | Coordinated team | 14 | A department that can be standalone or part of any company |
| **Middleware** | Behavior modifier | 11 | A lens that modifies input prompts or output responses |

### Example: One Query, Multiple Layers

```bash
myc agent-department dev_backend \
  -c dev_agency \
  -o prompt_enhancer \
  -o code_quality \
  "build a REST API with JWT authentication"
```

What happens behind the scenes:

1. `prompt_enhancer` (PRE middleware) restructures the query into a well-formed prompt with context, objectives, and guidelines
2. `dev_backend` department defines which specialists to use (backend_dev, database_designer, devops_deploy)
3. `dev_agency` company adds organizational context (code review culture, CI/CD practices, team workflow)
4. The most relevant specialist is selected and the system prompt is assembled from ROLE + CONTEXT() + company context
5. The LLM generates the response
6. `code_quality` (POST middleware) analyzes any code blocks for anti-patterns, security issues, and style violations
7. The final output is displayed — code with quality analysis appended

---

## Agent Architecture

### Execution Pipeline

```
User Query
    │
    ▼
┌──────────────────────┐
│  Middlewares (PRE)   │  ← prompt_enhancer, security_checker
│  (chained)           │     Restructure the prompt before sending
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Department          │  ← Defines which specialists to use
│  (optional)          │     Injects ROLE + DEPARTMENT_CONTEXT()
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Company             │  ← Adds organizational context (if -c flag)
│  (optional)          │     Injects COMPANY_CONTEXT() + sub-agent role
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Specialist          │  ← ROLE + CONTEXT() + PRE_LAUNCH hook
│  Selected            │     Final system prompt assembled
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  LLM (AI)            │  ← Response generation
│  (OpenClaude/etc.)   │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Middlewares (POST)  │  ← code_quality, summarizer, text_compressor
│  (chained)           │     Analyze, compress, or summarize output
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  POST_LAUNCH         │  ← Final hooks (save files, artifacts)
│  (specialist)        │
└──────┬───────────────┘
       │
       ▼
  Final Output
```

### Context Injection

For OpenClaude and Codex platforms, context is injected via `CLAUDE.md`:

```
# Agent: dev_backend

## Department Context

You are a backend development department responsible for...

## Company Context (dev_agency)

The company values clean code, peer review, tests, and CI/CD...

---

## Task

Build a REST API with JWT authentication
```

---

## Specialists (69 plugins)

Specialists grouped by 16+ bundles. Each bundle contains 4-5 related specialists.

### Development & Engineering

| Bundle | ID | Plugins |
|--------|-----|---------|
| Full Stack | `fullstack` | `frontend_dev`, `backend_dev`, `database_designer`, `devops_deploy` |
| Software Engineering | `software_engineering` | `software_architect`, `code_reviewer`, `test_engineer`, `ci_cd_expert` |
| Computer Engineering | `computer_engineering` | `embedded_dev`, `iot_engineer`, `network_analyzer`, `os_internals` |
| Data Engineering | `data_engineering` | `etl_builder`, `pipeline_designer`, `data_quality`, `warehouse_architect` |
| Mobile Apps | `app_mobile` | `mobile_architect`, `ui_mobile`, `native_bridge`, `app_store_prep` |
| Computer Vision | `visao_computacional` | `cv_architect`, `dataset_builder`, `model_trainer`, `cv_deployer` |

### Marketing & Business

| Bundle | ID | Plugins |
|--------|-----|---------|
| Marketing | `marketing` | `social_media`, `seo_analyst`, `copywriter`, `campaign_manager` |
| Sales & Growth | `vendas` | `sales_pitch`, `sales_funnel`, `business_model`, `growth_hacker` |
| Innovation | `ideias` | `brainstorm`, `design_thinking`, `idea_validator`, `mvp_builder` |

### Security & Investigation

| Bundle | ID | Plugins |
|--------|-----|---------|
| Web Security | `seguranca_web` | `web_auditor`, `owasp_checker`, `pentest_helper`, `hardening_guide` |
| Bug Bounty | `bugbounty` | `recon`, `exploit_writer`, `bounty_report`, `vuln_triage` |
| OSINT | `osint` | `osint_collector`, `source_analyzer`, `digital_footprint`, `data_correlator` |

### Domain-Specific

| Bundle | ID | Plugins |
|--------|-----|---------|
| Brazilian Law | `advocacia` | `legislacao_br`, `contratos_br`, `peticoes`, `jurisprudencia` |
| Journalism | `jornalismo` | `pauta_journal`, `fact_checker`, `redacao_news`, `editorial` |
| Game Design | `gamedesign` | `level_designer`, `game_narrative`, `mechanics_balancer`, `game_ux` |
| Education | `professor` | `lesson_planner`, `exam_creator`, `didatica`, `content_creator_edu` |

### Translation & Linguistics

| Language Pair | Specialist | Description |
|--------------|-----------|-------------|
| PT ↔ EN | `pt_en_translator` | Portuguese ↔ English bidirectional (technical, legal, business) |
| EN ↔ ES | `en_es_translator` | English ↔ Spanish (Latin American and European) |
| EN ↔ ZH | `en_zh_translator` | English ↔ Mandarin Chinese (Simplified and Traditional) |
| EN ↔ FR | `en_fr_translator` | English ↔ French (formal and informal registers) |
| EN ↔ JA | `en_ja_translator` | English ↔ Japanese (keigo, technical, casual) |

### Additional Standalone Specialists

| Specialist | Description |
|------------|-------------|
| `math_site_builder` | Mathematical content builder for educational sites |

---

## Companies (27 plugins)

Each company aggregates 3-8 sub-agents. Sub-agents can reuse existing specialists and have their own departments and middlewares.

### Technology Companies

| Company | ID | Sub-agents | Departments |
|---------|-----|------------|-------------|
| Software Agency | `dev_agency` | 8 | negocios, gestao, desenvolvimento, infra |
| DevOps Company | `devops_company` | 4 | infrastructure, security, monitoring |
| Security Company | `security_company` | 4 | web, app, infra, incident response |
| AI Company | `ai_company` | 4 | ML engineering, content, architecture, review |
| Data Company | `data_company` | 4 | data eng, analytics, warehouse, quality |

### Creative Companies

| Company | ID | Sub-agents |
|---------|-----|------------|
| Game Studio | `game_studio_company` | level design, narrative, mechanics, UX |
| Design Studio | `design_studio` | UI, product, brand |
| Art Studio | `art_studio` | art direction, illustration, motion |
| Music Company | `musica` | composition, production, arrangement, mixing |

### Business Companies

| Company | ID | Sub-agents |
|---------|-----|------------|
| Marketing Agency | `marketing_agency_company` | social strategy, SEO, copy, campaigns |
| Sales Company | `sales_company` | pitch, funnel, growth |
| Consulting Firm | `consulting_firm` | strategy, process analysis, change mgmt |
| Accounting Firm | `accounting_firm` | tax, audit, compliance |
| Investments | `investimentos` | portfolio, analysis, strategy, risk |
| HR Company | `rh_company` | recruitment, development, evaluation, compensation |

### Domain Companies

| Company | ID | Sub-agents |
|---------|-----|------------|
| Bug Bounty Enterprise | `bounty_company` | recon, pentest, exploit, report |
| News Media | `news_media_company` | reporter, editor, fact-checker, publisher |
| Law Firm | `law_firm` | legislation, contracts, petitions, research |
| Medical Company | `medica` | diagnosis, research, patient, compliance |
| Sports Company | `esporte_saude` | analysis, training, nutrition, psychology |
| School | `escola` | curriculum, pedagogy, evaluation, coordination |
| ENAM Prep | `enem_preparatoria` | content, exercises, review, strategy |
| Publishing House | `editora` | editing, revision, design, distribution |
| Culinary | `culinaria` | recipes, nutrition, techniques, presentation |
| Concurso (Exam Prep) | `concurso` | content, exercises, strategy, review |
| Artistic Production | `producao_artistica` | direction, production, coordination, promotion |

---

## Departments (14 plugins)

Departments can be used standalone or linked to any company via the `-c` flag.

| Department | ID | Specialists | Typical Command |
|-----------|-----|-------------|-----------------|
| Marketing | `marketing` | social_media, seo_analyst, copywriter, campaign_manager | `myc agent-department marketing "Q4 campaign"` |
| Frontend Dev | `dev_frontend` | frontend_dev, ui_mobile | `myc agent-department dev_frontend "dashboard UI"` |
| Backend Dev | `dev_backend` | backend_dev, database_designer, devops_deploy | `myc agent-department dev_backend "REST API"` |
| Security | `security` | web_auditor, owasp_checker, pentest_helper, hardening_guide | `myc agent-department security "audit server"` |
| Brazilian Law | `law_brazil` | legislacao_br, contratos_br, peticoes, jurisprudencia | `myc agent-department law_brazil "labor law"` |
| Journalism | `journalism` | pauta_journal, fact_checker, redacao_news, editorial | `myc agent-department journalism "investigation"` |
| Game Design | `game_design` | level_designer, game_narrative, mechanics_balancer, game_ux | `myc agent-department game_design "level design"` |
| Sales | `sales` | sales_pitch, sales_funnel, business_model, growth_hacker | `myc agent-department sales "enterprise pitch"` |
| Data Eng | `data_eng` | etl_builder, pipeline_designer, data_quality, warehouse_architect | `myc agent-department data_eng "build ETL"` |
| Software Eng | `software_eng` | software_architect, code_reviewer, test_engineer, ci_cd_expert | `myc agent-department software_eng "architecture"` |
| DevOps | `devops` | devops_deploy, ci_cd_expert, network_analyzer, os_internals | `myc agent-department devops "CI/CD pipeline"` |
| Education | `education` | lesson_planner, exam_creator, didatica, content_creator_edu | `myc agent-department education "course plan"` |
| OSINT | `osint` | osint_collector, source_analyzer, digital_footprint, data_correlator | `myc agent-department osint "investigate entity"` |
| **Linguistics** | `linguistics` | pt_en_translator, en_es_translator, en_zh_translator, en_fr_translator, en_ja_translator | `myc agent-department linguistics "translate docs"` |

---

## Middlewares (11 plugins)

Middlewares intercept the flow at specific points and can be chained with `-o` flags.

| Middleware | ID | Type | Phase | What It Does |
|-----------|-----|------|-------|--------------|
| Prompt Enhancer | `prompt_enhancer` | prompt_modifier | pre | Restructures the query with context, objectives, and guidelines |
| Text Compressor | `text_compressor` | output_modifier | post | Removes filler, compresses verbose output |
| Security Checker | `security_checker` | content_filter | both | Security checklist on input, leak detection on output |
| Code Quality | `code_quality` | output_modifier | post | Analyzes code blocks for anti-patterns, security issues, style |
| Summarizer | `summarizer` | output_modifier | post | Generates an executive summary of long responses |
| Caveman Mimic | `caveman_mimic` | output_modifier | post | Translates output to simple, plain language |
| Guided Flow | `guided_flow` | prompt_modifier | pre | Structured step-by-step interaction flow |
| Token Saver | `token_saver` | prompt_modifier | pre | Reduces token usage by compressing context |
| *(additional)* | | | | Custom middlewares can be created with `myc agent middleware --help` |

### Stacking Middlewares

```bash
# Chain multiple middlewares on any plugin type
myc agent-specialist backend_dev \
  -o prompt_enhancer \
  -o security_checker \
  -o code_quality \
  "implement OAuth2 authentication"
```

---

## Plugin Interface

### Specialist

```python
# plugins/specialists/example.py
NAME = "Example Specialist"
DESCRIPTION = "Short description of expertise"

def PRE_LAUNCH(profile):
    """Runs before the agent starts. Modify env vars, validate prerequisites."""
    profile["env"]["MYC_PLUGIN_X"] = "1"

def CONTEXT(profile) -> str:
    """Returns context text injected into CLAUDE.md as the system prompt."""
    return "Detailed instructions that define the specialist's expertise..."
```

### Company

```python
# plugins/companies/example.py
NAME = "Example Company"
DESCRIPTION = "What this company does"

SPECIALISTS = [
    {
        "id": "sub_agent_id",                # unique identifier
        "name": "Sub-agent Display Name",
        "role": "Detailed prompt defining this sub-agent's role",
        "specialists": ["specialist_1"],       # reuses existing specialists
        "department": "dept_name",            # department this sub-agent belongs to
    },
]

def COMPANY_CONTEXT():
    return "General context shared by all sub-agents..."
```

### Department

```python
# plugins/departments/example.py
NAME = "Example Department"
DESCRIPTION = "Short description"
SPECIALISTS = ["specialist_1", "specialist_2"]   # specialist IDs used
MIDDLEWARES: list[str] = []                       # default middlewares
PARENT_COMPANY = None                             # or "company_id"
ROLE = "Detailed system prompt for the department..."

def DEPARTMENT_CONTEXT():
    return "Additional context injected..."
```

### Middleware

```python
# plugins/middlewares/example.py
NAME = "Example Middleware"
DESCRIPTION = "What it does"
MIDDLEWARE_TYPE = "prompt_modifier"   # prompt_modifier | output_modifier | content_filter
RUNS_WHEN = "pre"                     # pre | post | both | manual

def PROMPT_MODIFY(text, profile):
    """Modifies the user's query before sending to LLM."""
    return f"Add context:\n{context}\n\nOriginal: {text}"

def OUTPUT_MODIFY(text, profile):
    """Modifies the LLM's response before displaying."""
    return processed_text
```

---

## Agent Profiles & Platforms

### Creating an Agent

```powershell
myc agent add
```

The wizard asks:

1. **Agent name** — identifier without spaces (e.g., `dev`, `research`)
2. **Platform** — which AI tool to launch
3. **API configuration** — provider, model, API key (for OpenAI-compatible)
4. **Working directory** — where the agent operates
5. **Initial context** — default instructions for the agent
6. **Role** — primary function (dev, artist, writer, researcher, educator, musician, business, generalist)
7. **MYC routines** — link routines to this agent for context injection
8. **Plugin filter** — which specialists this agent handles (optional)
9. **Callable agents** — which other agents this one can invoke (optional)

### Supported Platforms

| Platform | Binary | Setup | Best For |
|----------|--------|-------|----------|
| **OpenClaude** | `openclaude` | OpenRouter/Ollama/Gemini API key | General-purpose LLM access |
| **Cursor** | `cursor .` | Cursor account | Code editing with AI |
| **VS Code + Copilot** | `code .` | GitHub Copilot subscription | IDE-integrated AI |
| **OpenAI Codex** | `codex` | OpenAI API key | OpenAI's coding CLI |
| **Custom** | Any command | User-defined | Any external tool |

### OpenAI-Compatible Provider Setup

```powershell
myc install openclaude
```

Supported providers:

| Provider | Base URL | API Key | Models |
|----------|----------|---------|--------|
| OpenAI | `https://api.openai.com/v1` | `sk-...` | gpt-4o, gpt-4o-mini |
| OpenRouter | `https://openrouter.ai/api/v1` | `sk-or-v1-...` | 100+ models |
| Ollama (local) | `http://localhost:11434/v1` | `ollama` | llama3, mistral, etc. |
| Gemini | `https://generativelanguage.googleapis.com/v1beta/openai` | Gemini key | gemini-2.5-pro |
| Custom | Any | Any | Any |

### Agent-to-Agent Communication

Agents can invoke each other, enabling multi-agent workflows:

```python
# Link agents (caller → callee)
myc agent link-agent dev artist            # dev can call artist
myc agent link-agent dev artist --bi       # bidirectional

# Now when a dev agent needs UI work, it can call the artist agent
# The called agent receives: "Called by agent 'dev'"
```

---

## Configuration Structure

### Routine Configuration (`~/.myc/config.json`)

```jsonc
{
  "commands": {
    "estudar": {
      "description": "Study routines",
      "subcommands": {
        "visao-computacional": {
          "description": "Computer Vision course",
          "days": ["segunda", "quarta", "sexta"],    // empty = every day
          "actions": [
            {
              "type": "browser",
              "url": "https://udemy.com/course/...",
              "monitor": 0,
              "new_window": true,
              "browser": "chrome"
            },
            {
              "type": "browser",
              "url": "https://colab.research.google.com",
              "monitor": 1,
              "new_window": true,
              "browser": "chrome"
            }
          ]
        }
      }
    }
  },
  "settings": {
    "chrome_path": ""   // leave empty for auto-detection
  }
}
```

### Action Types

| Type | Required Fields | Optional Fields | Description |
|------|----------------|-----------------|-------------|
| `browser` | `url`, `monitor` | `new_window` (default: true), `browser` (default: chrome) | Opens a URL in a specific browser on a specific monitor |
| `app` | `path` | `args` (list of strings) | Launches an executable with arguments |

### Valid Days

`segunda` · `terca` · `quarta` · `quinta` · `sexta` · `sabado` · `domingo`

An empty `days` list means the routine is available **every day**.

### Agent Storage (`~/.myc/agents/`)

```
~/.myc/agents/
├── agents.json              # All agent profiles
├── history.json             # Launch history (max 500 entries)
├── plugin_registry.json     # Plugin installation registry
├── plugins/                 # Installed specialist plugins
├── companies/               # Installed company plugins
├── departments/             # Installed department plugins
└── middlewares/             # Installed middleware plugins
```

---

## Directory Layout

```
cli_automatizacao_rotina/
├── myc/                              # Core CLI package
│   ├── __init__.py
│   ├── __main__.py                   # Entry point (python -m myc)
│   ├── cli.py                        # All Click CLI command definitions
│   ├── config.py                     # config.json loader/saver
│   ├── monitor.py                    # Multi-monitor detection (screeninfo)
│   ├── runner.py                     # Browser/app execution engine
│   ├── tui.py                        # Terminal UI navigation (questionary + rich)
│   ├── agent.py                      # Agent lifecycle, profiles, history
│   ├── agent_plugins.py              # Specialist + Company plugin loading
│   ├── department.py                 # Department plugin system
│   ├── plugin_installer.py           # Plugin installation logic
│   ├── plugin_manager.py             # Bundle management & auto-assignment
│   └── html_dashboard.py             # Web dashboard server (localhost:8787)
│
├── plugins/                          # Built-in plugin repository
│   ├── specialists/                  # 69 individual expert agents
│   ├── companies/                    # 27 multi-agent organizations
│   ├── departments/                  # 14 coordinated teams
│   └── middlewares/                  # 11 prompt/output modifiers
│
├── docs/                             # Documentation
│   ├── ARCHITECTURE.md               # Architecture deep dive
│   ├── plugins/README.md             # Plugin system reference
│   ├── agents-and-plugins.md         # Agent integration guide
│   ├── openrouter-setup.md           # OpenRouter setup tutorial
│   ├── specialists/                  # Individual specialist documentation
│   ├── ingles/                       # English documentation
│   │   ├── getting-started.md
│   │   ├── architecture.md
│   │   └── use_cases.md
│   ├── portugues/                    # Portuguese documentation
│   │   ├── introducao.md
│   │   ├── arquitetura.md
│   │   └── casos_de_uso.md
│   └── agentes/                      # Agent-specific docs
│       └── use_cases.md              # Real-world scenarios
│                                     #   including: AI Company documenting this project
│
├── pyproject.toml                    # Python package metadata
├── requirements.txt                  # Dependencies
├── install.ps1                       # Windows installation script
└── build_exe.py                      # PyInstaller build script
```

---

## Dependencies & Build

### Runtime Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `click` | — | CLI framework (commands, options, arguments) |
| `rich` | — | Console output (tables, panels, syntax highlighting) |
| `questionary` | — | Interactive prompts (select, checkbox, text, confirm) |
| `screeninfo` | — | Multi-monitor detection (resolution, position, primary) |

### Build Dependencies

| Package | Purpose |
|---------|---------|
| `pyinstaller` | Package into standalone `myc.exe` |

### Build

```powershell
python build_exe.py
# Output: dist/myc.exe (~20MB standalone)
```

### Build for Distribution

```powershell
pyinstaller myc.spec
# Uses the spec file for full configuration
```

---

## Web Dashboard

```powershell
myc config-html          # opens at localhost:8787
myc config-html -p 9000  # custom port
```

The dashboard displays:
- **Agents** — all configured profiles with platform, env vars, working directory
- **Routines** — all command groups with subcommands, days, and actions
- **Plugins** — installed specialists, companies, departments, middlewares
- **History** — launch log with timestamps, status, and routine references
- **Statistics** — charts and summary data

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `myc` not recognized | PATH not updated | Restart terminal, or run `myc setup --auto` |
| Browser doesn't open | Chrome path not detected | Set manually: `myc config` → Chrome path |
| Plugin "not found" | Bundle not installed | Run `myc agent bundle-install <id>` |
| Middleware not applied | Not installed locally | `myc agent middleware --list` shows status |
| Agent launch fails: no binary | OpenClaude not installed | Run `myc install openclaude` |
| Encoding issues on Windows | Non-UTF8 terminal | The CLI sets `PYTHONUTF8=1` automatically in generated scripts |
| Company sub-agent "not found" | Typo in sub-agent ID | Run `myc agent-company <name>` without sub-agent to list available |
| Department not found | Missing leading slash in query | Use exact ID: `myc agent-department --list` to see IDs |

---

## License

MIT