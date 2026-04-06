# Getting Started with MYC

## What is MYC?

MYC (My Commands) is a CLI toolkit that solves two problems:

1. **Routine Automation** — Register groups of apps, URLs, and browser tabs organized by day of the week, launch them with a single command, and position windows across multiple monitors.
2. **AI Agent System** — Deploy a modular plugin system with 65 specialists, 27 companies, 13 departments, and 8 middlewares that turn an LLM into a team of specialized agents.

## Installation

### Prerequisites

- Python 3.9+
- Windows 10 or 11
- npm (for OpenClaude agent platform, optional)

### Quick Install

```powershell
git clone https://github.com/samueldk12/cli_automatizacao_rotina.git
cd cli_automatizacao_rotina
.\install.ps1
```

### Manual Install

```powershell
pip install -e .
myc setup --auto   # adds ~/.myc/bin to PATH
# restart your terminal
```

## Configuration

### Step 1: Set Up OpenClaude (AI Platform)

```powershell
myc install openclaude
```

This guides you through:
1. Installing OpenClaude via npm (if not present)
2. Entering your OpenRouter API key
3. Selecting a model (default: `qwen/qwen3.6-plus:free`)

> Don't have an OpenRouter key? Get one at [openrouter.ai](https://openrouter.ai/)

### Step 2: Install Plugin Bundles

```powershell
# Install all specialist bundles (65 plugins)
myc agent bundle-install --all

# Install a specific bundle
myc agent bundle-install fullstack
myc agent bundle-install marketing
myc agent bundle-install professor
```

### Step 3: Verify Installation

```powershell
# List configured agents
myc agent list

# List available companies
myc agent-company dev_agency

# List available middlewares
myc agent middleware --list

# Launch your agent
myc agent launch default
```

## Your First Routine

```powershell
# Create a new command group
myc add

# The wizard will ask:
# 1. Group name (e.g., "trabalhar")
# 2. Subcommand name (e.g., "daily")
# 3. Days of the week
# 4. Actions (URLs to open, apps to launch)

# Execute the routine
trabalhar daily

# Or via TUI
myc tui
```

## Your First AI Agent Query

```powershell
# Query a specialist directly
myc agent-specialist frontend_dev "create a responsive dashboard component"

# Use a company (multi-agent organization)
myc agent-company dev_agency tech_lead "architect a microservices backend"

# Add middlewares for enhanced output
myc agent-specialist backend_dev -o prompt_enhancer -o code_quality "implement JWT authentication"
```

## Command Quick Reference

| Command | Description |
|---------|-------------|
| `myc add` | Create a new routine command |
| `myc list` | List all registered commands |
| `myc tui` | Open visual terminal navigation |
| `myc monitors` | List detected monitors |
| `myc setup --auto` | Generate shortcuts and add to PATH |
| `myc config-html` | Open web dashboard (localhost:8787) |
| `myc install openclaude` | Install and configure AI agent platform |
| `myc agent add` | Create an agent profile |
| `myc agent list` | List configured agents |
| `myc agent launch <name>` | Launch an agent |
| `myc agent-specialist <name> "query"` | Query a specialist |
| `myc agent-company <company> [sub] "query"` | Query a company sub-agent |
| `myc agent-department <dept> "query"` | Query a department |
| `myc agent middleware --list` | List available middlewares |
| `myc agent bundle-install --all` | Install all specialist bundles |

## Linguistics Department

The `linguistics` department manages professional translation across 5 language pairs:

```bash
# Use the full translation team
myc agent-department linguistics "translate this README to Spanish, French, and Japanese"

# Individual translator specialists
myc agent-specialist pt_en_translator "translate contract from PT to EN"
myc agent-specialist en_es_translator "translate user guide to Spanish"
myc agent-specialist en_zh_translator "translate spec to Simplified Chinese"
myc agent-specialist en_fr_translator "translate press release to French"
myc agent-specialist en_ja_translator "translate onboarding guide to Japanese"
```

Language pairs: PT↔EN, EN↔ES, EN↔ZH, EN↔FR, EN↔JA

## Next Steps

- Read the full architecture: [ARCHITECTURE.md](../ARCHITECTURE.md)
- Browse the plugin reference: [../plugins/README.md](../plugins/README.md)
- See real-world use cases: [use_cases.md](./use_cases.md)
