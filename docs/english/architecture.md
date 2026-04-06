# MYC Architecture

## System Overview

MYC is composed of three independent but complementary layers:

```
┌─────────────────────────────────────────────────────┐
│                   MYC CLI                           │
│                                                     │
│  ┌───────────────────────────────────────────┐      │
│  │           Routine Layer                    │      │
│  │  Groups → Subcommands → Days → Actions     │      │
│  │  (open URLs, launch apps, position windows) │      │
│  └──────────────┬────────────────────────────┘      │
│                 │                                    │
│  ┌──────────────▼────────────────────────────┐      │
│  │           Agent Layer                      │      │
│  │  Profiles → Platform → env → Context       │      │
│  │  (launch AI agents with MYC context)       │      │
│  └──────────────┬────────────────────────────┘      │
│                 │                                    │
│  ┌──────────────▼────────────────────────────┐      │
│  │           Plugin Layer                     │      │
│  │  Specialists + Companies + Departments     │      │
│  │  + Middlewares (composable)                │      │
│  └───────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────┘
```

## Layer 1: Routine Manager

**Purpose:** Automate the daily task of opening the same apps, URLs, and browser tabs.

### How It Works

1. Groups are registered in `~/.myc/config.json`
2. Each group contains subcommands with:
   - Days of the week availability
   - Actions (browser URLs or app paths with monitor target)
3. Shortcut scripts are generated in `~/.myc/bin/`
4. When executed, the CLI opens URLs in specified browsers on specified monitors

### Data Flow

```
config.json → runner.py → browser/app launch → window positioning (Win32 API)
    │
    ├── add wizard (questionary)
    ├── TUI navigation
    └── shortcut scripts (.bat / .ps1)
```

## Layer 2: Agent Management

**Purpose:** Manage AI agent profiles that integrate with various platforms.

### Supported Platforms

| Platform | Binary | Description |
|----------|--------|-------------|
| OpenClaude | `openclaude` | Any model via OpenAI-compatible API |
| Cursor | `cursor` | AI code editor |
| VS Code + Copilot | `code` | GitHub Copilot |
| OpenAI Codex | `codex` | OpenAI's CLI for coding |
| Custom | User-defined | Any command |

### Agent Lifecycle

```
1. Create agent (wizard) → agents.json
2. Launch agent → spawns platform binary
3. Inject CLAUDE.md → context file with agent profile + MYC tasks
4. Execute plugins → PRE_LAUNCH hooks fire
5. User interacts with AI
6. Record history → history.json
```

### Agent-to-Agent Communication

Agents can call other agents:

```python
# Link agents
myc agent link-agent dev artist  # dev can call artist

# Call from within an agent context
call_agent("artist", "create UI mockup", called_by="dev")
```

## Layer 3: Plugin System

**The core differentiator.** A composable plugin architecture with four plugin types that can be mixed at any level.

### Plugin Types

#### 1. Specialists (65 plugins)

The atomic unit. A single expert agent with deep knowledge in one area.

```
Execution: PRE_LAUNCH → Agent runs with CONTEXT() → POST_LAUNCH
```

Each specialist exports:
- `NAME` — Display name
- `DESCRIPTION` — Short description
- `PRE_LAUNCH(profile)` — Hook before agent starts
- `CONTEXT(profile)` — Returns context text for CLAUDE.md
- `POST_LAUNCH(profile)` — Post-execution hook (optional)

#### 2. Companies (27 plugins)

Multi-agent organizations, each with 3-8 sub-agents. Sub-agents can reuse existing specialists.

```
Company Context → Sub-agent Role → Reused Specialists → Middleware pipeline
```

Each company exports:
- `NAME` — Company name
- `DESCRIPTION` — What the company does
- `SPECIALISTS` — List of sub-agents with their roles and referenced specialists
- `COMPANY_CONTEXT()` — General context for the company

#### 3. Departments (14 plugins)

Standalone or company-linked teams. A department coordinates specialists for a domain.

```
Department ROLE → Listed specialists → Middleware pipeline → Consolidated output
```

Each department exports:
- `NAME` — Department name
- `DESCRIPTION` — Description
- `SPECIALISTS` — List of specialist IDs
- `MIDDLEWARES` — Default middlewares
- `PARENT_COMPANY` — Parent company ID or None
- `ROLE` — System prompt
- `DEPARTMENT_CONTEXT()` — Additional context

#### 4. Middlewares (8 plugins)

Prompt/output modifiers attachable at any level: specialist, company, department.

```
User Query → [PRE Middlewares] → Specialist → LLM → [POST Middlewares] → Output
```

Types:
- `prompt_modifier` — Modifies input prompt (PRE)
- `output_modifier` — Modifies output text (POST)
- `content_filter` — Modifies input AND filters output (BOTH)
- `agent_runner` — Runs a sub-agent as middleware (MANUAL)

### Execution Pipeline

```
User Query ("build a REST API")
       │
       ▼
┌──────────────────┐
│  PROMPT_MODIFY   │  ← prompt_enhancer restructures query
│    (PRE)         │     with context, objectives, guidelines
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Department     │  ← Injects ROLE + specialist list
│   (optional)     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Company        │  ← Adds organizational context
│   (optional)     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Specialist     │  ← Injects CONTEXT() + PRE_LAUNCH
│   Selected       │     Final system prompt assembled
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│    LLM (AI)      │  ← Response generation
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  OUTPUT_MODIFY   │  ← code_quality, summarizer, text_compressor
│    (POST)        │     analyze, compress, summarize
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  POST_LAUNCH     │  ← Save files, generate artifacts
└────────┬─────────┘
         │
         ▼
   Final Output
```

### Cross-Plugin Composition

Plugins gain extraordinary power when combined:

```bash
# Specialist + 2 middlewares
myc agent-specialist backend_dev -o prompt_enhancer -o code_quality "implement JWT auth"

# Company sub-agent + middleware
myc agent-company dev_agency dev_frontend -o code_quality "build admin dashboard"

# Department + company context + middleware
myc agent-department dev_backend -c dev_agency -o prompt_enhancer "refactor API"

# Company without sub-agent (lists available)
myc agent-company dev_agency
```

## Installation & Plugin Lifecycle

### Bundle Installation

```bash
# Install all specialist bundles
myc agent bundle-install --all

# Install specific bundle
myc agent bundle-install fullstack

# List available bundles
myc agent bundle-list
```

### Auto-Installation

When a company, department, or company is first used, its plugins are auto-copied from the built-in `plugins/` directory to `~/.myc/agents/`.

### Plugin Creation Wizards

```bash
myc agent plugin-add        # Create a specialist plugin
myc agent company-add       # Create a company plugin
myc agent department-add    # Create a department
```

## Configuration Files

| File | Location | Purpose |
|------|----------|---------|
| `config.json` | `~/.myc/config.json` | Routine definitions |
| `agents.json` | `~/.myc/agents/agents.json` | Agent profiles |
| `history.json` | `~/.myc/agents/history.json` | Launch history |
| `plugin_registry.json` | `~/.myc/agents/plugin_registry.json` | Plugin registry |

### Directory Structure

```
~/.myc/
├── config.json
├── bin/                        # Generated shortcuts
│   ├── estudar.bat
│   ├── estudar.ps1
│   └── ...
└── agents/
    ├── agents.json
    ├── history.json
    ├── plugins/                # Installed specialists
    ├── companies/              # Installed companies
    ├── departments/            # Installed departments
    └── middlewares/            # Installed middlewares
```
