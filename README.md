# MYC — My Commands

CLI para cadastrar e executar atalhos de sites e aplicativos diretamente do terminal, com suporte a **multi-monitor**, organização por **dia da semana** e **agentes de IA com 96 plugins modulares**.

---

## Funcionalidades

- Cadastrar grupos de comandos (ex: `estudar`, `trabalhar`)
- Cada comando abre URLs e/ou aplicativos em monitores específicos
- Filtro por dia da semana (`segunda`, `terca`, `quarta`, `quinta`, `sexta`, `sabado`, `domingo`)
- Navegação visual interativa (TUI) com setas
- Scripts de atalho gerados automaticamente no PATH
- Reposicionamento de janelas via Win32 API
- **Sistema de plugins de IA com 4 tipos:**
  - **64 Specialists** — agentes especialistas individuais
  - **14 Companies** — empresas com múltiplos sub-agentes que reutilizam specialists
  - **13 Departments** — equipes independentes ou vinculadas a empresas
  - **5 Middlewares** — modificadores de prompt/output anexáveis em qualquer nível

---

## Instalação

### Pré-requisitos

- Python 3.9+
- Windows 10 ou 11

### Via PowerShell

```powershell
git clone https://github.com/samueldk12/cli_automatizacao_rotina.git
cd cli_automatizacao_rotina
.\install.ps1
```

### Manual

```powershell
pip install -e .
myc setup --auto   # adiciona ~/.myc/bin ao PATH
# reinicie o terminal
```

---

## Uso rápido

### Comandos de rotina

```
myc add                       # wizard para criar comando
myc tui                       # navegação visual
myc list                      # lista todos os comandos
<grupo> <subcomando>          # executa (ex: estudar visao-computacional)
<grupo> <dia> <subcomando>    # com filtro de dia
```

### Agentes de IA

```powershell
# Setup inicial
myc install openclaude        # instala e configura OpenClaude

# Especialista individual
myc agent-specialist social_media "crie calendário editorial para Instagram"
myc agent-specialist frontend_dev -o prompt_enhancer "crie componente de login com React"

# Empresa com múltiplos sub-agentes
myc agent-company dev_agency           # lista sub-agentes da empresa
myc agent-company dev_agency tech_lead "crie arquitetura de microserviços"
myc agent-company bounty_company recon_specialist -o security_checker "investigue dominio alvo.com"

# Departamento independente
myc agent-department marketing "crie campanha de vendas para Black Friday"
myc agent-department dev_backend -c dev_agency "refatore API REST para GraphQL"
myc agent-department --list            # lista todos os departamentos

# Middlewares (aplicados em especialistas, empresas ou departamentos)
myc agent-specialist backend_dev -o prompt_enhancer -o security_checker "implemente auth JWT"
myc agent-company security_company web_security -o code_quality "revise código de API"
myc agent-department osint -o summarizer "investigue pessoa X"
```

---

## Comandos disponíveis

| Comando | Descrição |
|---------|-----------|
| `myc add` | Cadastra novo comando (wizard interativo) |
| `myc list` | Lista todos os comandos |
| `myc list -g estudar` | Lista comandos de um grupo |
| `myc run <grupo> <cmd>` | Executa um comando |
| `myc run <grupo> <dia> <cmd>` | Executa com filtro de dia |
| `myc tui` | Navegação visual interativa |
| `myc tui --group estudar` | TUI direto em um grupo |
| `myc edit <grupo> <cmd>` | Edita um comando existente |
| `myc delete <grupo> <cmd>` | Remove um subcomando |
| `myc delete <grupo>` | Remove um grupo inteiro |
| `myc monitors` | Lista monitores detectados |
| `myc setup` | Gera scripts de atalho |
| `myc setup --auto` | Gera scripts e adiciona ao PATH |
| `myc config` | Configura caminho do Chrome |
| `myc config-html` | Abre dashboard web de configuração |
| `myc install openclaude` | Instala e configura OpenClaude |
| | |
| `myc agent add` | Cria perfil de agente de IA (wizard) |
| `myc agent list` | Lista agentes configurados |
| `myc agent launch <nome>` | Lanca agente no diretorio atual |
| `myc agent delete <nome>` | Remove agente |
| `myc agent history` | Historico de lancamentos |
| `myc agent plugins` | Lista plugins instalados |
| `myc agent plugin-add` | Cria plugin customizado |
| `myc agent company-add` | Cria empresa com sub-agentes |
| `myc agent department-add` | Cria departamento/equipe |
| `myc agent bundle-install --all` | Instala todos os bundles de specialists |
| `myc agent bundle-install <id>` | Instala bundle especifico |
| `myc agent bundle-install --company --all` | Instala todas as companies |
| `myc agent bundle-list` | Lista bundles de specialists |
| `myc agent bundle-list --company` | Lista bundles de companies |
| `myc agent middleware --list` | Lista middlewares disponibili |
| `myc automate <agente> --group X` | Lanca agente com contexto MYC |
| | |
| `myc agent-specialist <name> [-o mw...] "query"` | Lança especialista com consulta |
| `myc agent-company <company> [sub] [-o mw...] "query"` | Lança empresa/sub-agente |
| `myc agent-department <dept> [-o mw...] [-c comp] "query"` | Lança departamento |

---

## Arquitetura de Plugins

### Visão geral

```
plugins/
├── specialists/        # 64 agentes especialistas individuais
│   ├── social_media.py
│   ├── frontend_dev.py
│   └── ... (64 arquivos)
│
├── companies/          # 14 empresas com sub-agentes
│   ├── dev_agency.py           (4 sub-agentes)
│   ├── game_studio_company.py  (4 sub-agentes)
│   ├── bounty_company.py       (4 sub-agentes)
│   └── ... (14 arquivos)
│
├── departments/        # 13 departamentos/equipes
│   ├── marketing.py
│   ├── dev_backend.py
│   └── ... (13 arquivos)
│
└── middlewares/        # 5 modificadores de prompt/output
    ├── prompt_enhancer.py      (pre-prompt)
    ├── text_compressor.py      (post-output)
    ├── security_checker.py     (ambos)
    ├── code_quality.py         (post-output)
    └── summarizer.py           (post-output)
```

### 1. Specialists (64 plugins)

Cada specialist é um agente individualmente especializado em um tema.

```python
# Interface do plugin specialist
NAME = "Nome Display"
DESCRIPTION = "Descricao curta"

def PRE_LAUNCH(profile):
    profile["env"]["MYC_PLUGIN_X"] = "1"

def CONTEXT(profile) -> str:
    return "Prompt completo que injeta no Claude.md ... "
```

#### Bundles de Specialists (16 bundles × 4 plugins = 64)

| Bundle | ID | Plugins | Uso |
|--------|-----|---------|-----|
| Agencia de Marketing | `marketing` | social_media, seo_analyst, copywriter, campaign_manager | Redes sociais, SEO, copy |
| Estudio de Game Design | `gamedesign` | level_designer, game_narrative, mechanics_balancer, game_ux | Games |
| Escritorio de Advocacia (BR) | `advocacia` | legislacao_br, contratos_br, peticoes, jurisprudencia | Direito brasileiro |
| Redacao Jornalistica | `jornalismo` | pauta_journal, fact_checker, redacao_news, editorial | Jornalismo |
| Inteligencia OSINT | `osint` | osint_collector, source_analyzer, digital_footprint, data_correlator | Investigacao |
| Seguranca Web | `seguranca_web` | web_auditor, owasp_checker, pentest_helper, hardening_guide | Seguranca |
| Bug Bounty Hunter | `bugbounty` | recon, exploit_writer, bounty_report, vuln_triage | Bug bounty |
| Eng. Visao Computacional | `visao_computacional` | cv_architect, dataset_builder, model_trainer, cv_deployer | Visao comput. |
| Desenvolvimento Full Stack | `fullstack` | frontend_dev, backend_dev, database_designer, devops_deploy | Full stack |
| Desenvolvimento App Mobile | `app_mobile` | mobile_architect, ui_mobile, native_bridge, app_store_prep | Mobile |
| Gerador de Ideias | `ideias` | brainstorm, design_thinking, idea_validator, mvp_builder | Ideias/MVP |
| Vendas e Empreendedorismo | `vendas` | sales_pitch, sales_funnel, business_model, growth_hacker | Vendas |
| Engenharia de Dados | `data_engineering` | etl_builder, pipeline_designer, data_quality, warehouse_architect | Dados |
| Engenharia de Software | `software_engineering` | software_architect, code_reviewer, test_engineer, ci_cd_expert | Software |
| Engenharia da Computacao | `computer_engineering` | embedded_dev, iot_engineer, network_analyzer, os_internals | Computacao |
| Professor / Educador | `professor` | lesson_planner, exam_creator, didatica, content_creator_edu | Educacao |

### 2. Companies (14 empresas)

Cada empresa é um conjunto de 3-4 sub-agentes especializados, onde cada sub-agente pode **reutilizar specialists** existentes e ter **middlewares próprios**.

```python
# Interface do plugin company
NAME = "Nome da Empresa"
DESCRIPTION = "Descricao"
SPECIALISTS = [
    {
        "id": "sub_agent_id",
        "name": "Nome do Sub-agente",
        "role": "Papel detalhado (prompt base do sub-agente)",
        "specialists": ["specialist_id_1", "specialist_id_2"],  # reusa specialists
        "department": "nome_do_departamento",
    },
    # ... 3+ sub-agentes no minimo ...
]

def COMPANY_CONTEXT():
    return "Contexto geral da empresa"
```

#### Empresas Disponíveis

| Empresa | ID | Sub-agentes | Foco |
|---------|-----|-------------|------|
| Agencia de Software | `dev_agency` | tech_lead, dev_frontend, dev_backend, devops | Desenvolvimento completo |
| Estudio de Games | `game_studio_company` | level_designer, narrative_writer, mechanic_designer, ux_designer | Game design |
| Bug Bounty Enterprise | `bounty_company` | recon_specialist, pentest_engineer, exploit_developer, report_writer | Bug bounty |
| Agencia de Marketing | `marketing_agency_company` | social_strategist, seo_expert, copy_lead, campaign_owner | Marketing completo |
| DevOps Company | `devops_company` | infra_architect, pipeline_eng, security_ops, monitoring | DevOps |
| Empresa de Seguranca | `security_company` | web_sec, app_sec, infra_sec, incident_resp | Seguranca |
| Studio de Design | `design_studio` | ui_designer, product_designer, brand_spec | Design |
| Escritorio de Advocacia | `law_firm` | advogado_legislacao, advogado_contratos, advogado_peticoes, pesquisador | Direito BR |
| Empresa de Vendas | `sales_company` | pitch_specialist, funnel_manager, growth_lead | Vendas |
| Empresa de Noticias | `news_media_company` | reporter, editor, fact_checker, digital_publisher | Midia/Noticias |
| Empresa de Contabilidade | `accounting_firm` | tax_accountant, financial_auditor, compliance_specialist | Contabilidade |
| Empresa Esportiva | `sports_company` | sports_analyst, fitness_coach, nutritionist | Esportes |
| Empresa de Consultoria | `consulting_firm` | strategy_consultant, process_analyst, change_manager | Consultoria |
| Studio de Arte Digital | `art_studio` | art_director, illustrator, motion_designer | Arte digital |

### 3. Departments (13 departamentos/equipes)

Departamentos podem existir de forma independente OU dentro de uma empresa.

```bash
# Departamento independente
myc agent-department marketing "crie campanha de vendas"

# Dentro de uma empresa
myc agent-department dev_frontend -c dev_agency "crie dashboard admin"

# Com middleware
myc agent-department security -o prompt_enhancer -o security_checker "audite servidor"

# Listar todos
myc agent-department --list
```

| Departamento | ID | Specialists | Standalone? |
|-------------|-----|------------|------------|
| Marketing | `marketing` | social_media, seo_analyst, copywriter, campaign_manager | Sim |
| Frontend Dev | `dev_frontend` | frontend_dev, ui_mobile | Sim |
| Backend Dev | `dev_backend` | backend_dev, database_designer, devops_deploy | Sim |
| Seguranca | `security` | web_auditor, owasp_checker, pentest_helper, hardening_guide | Sim |
| Advocacia BR | `law_brazil` | legislacao_br, contratos_br, peticoes, jurisprudencia | Sim |
| Jornalismo | `journalism` | pauta_journal, fact_checker, redacao_news, editorial | Sim |
| Game Design | `game_design` | level_designer, game_narrative, mechanics_balancer, game_ux | Sim |
| Vendas | `sales` | sales_pitch, sales_funnel, business_model, growth_hacker | Sim |
| Data Eng | `data_eng` | etl_builder, pipeline_designer, data_quality, warehouse_architect | Sim |
| Software Eng | `software_eng` | software_architect, code_reviewer, test_engineer, ci_cd_expert | Sim |
| DevOps | `devops` | devops_deploy, ci_cd_expert, network_analyzer, os_internals | Sim |
| Educacao | `education` | lesson_planner, exam_creator, didatica, content_creator_edu | Sim |
| OSINT | `osint` | osint_collector, source_analyzer, digital_footprint, data_correlator | Sim |

### 4. Middlewares (5 plugins)

Middlewares podem ser anexados a **qualquer nível**: specialist, sub-agente de empresa, departamento, ou empresa inteira.

```bash
# Pre-prompt: melhora a entrada do usuario
myc agent-specialist backend_dev -o prompt_enhancer "crie API REST"

# Post-output: comprime a resposta
myc agent-company dev_agency dev_frontend -o text_compressor "crie dashboard completo"

# Ambos: analisa seguranca na entrada e saida
myc agent-department security -o security_checker "audite servidor web"

# Pos-processamento: qualidade de codigo
myc agent-specialist frontend_dev -o code_quality "crie componente auth"

# Pos-processamento: resume a saida
myc agent-company news_media_company reporter -o summarizer "investigue caso X"
```

| Middleware | ID | Tipo | Quando | Descrição |
|-----------|-----|------|--------|-----------|
| Prompt Enhancer | `prompt_enhancer` | prompt_modifier | pre | Reestrutura prompt com contexto e diretrizes |
| Text Compressor | `text_compressor` | output_modifier | post | Remove enchimento, resume saidas longas |
| Security Checker | `security_checker` | content_filter | both | Checklist de seguranca + detecção de vazamentos |
| Code Quality | `code_quality` | output_modifier | post | Analisa codigo em busca de anti-padroes |
| Summarizer | `summarizer` | output_modifier | post | Gera resumo executivo estruturado |

---

## Estrutura de configuração

```json
{
  "commands": {
    "estudar": {
      "description": "Comandos de estudo",
      "subcommands": {
        "visao-computacional": {
          "description": "Visão Computacional",
          "days": ["segunda", "quarta", "sexta"],
          "actions": [
            {"type": "browser", "url": "https://udemy.com/...", "monitor": 0, "new_window": true, "browser": "chrome"},
            {"type": "browser", "url": "https://colab.research.google.com", "monitor": 1, "new_window": true, "browser": "chrome"}
          ]
        }
      }
    }
  }
}
```

### Tipos de ação

| Tipo | Campos |
|------|--------|
| `browser` | `url`, `monitor` (0-based), `new_window`, `browser` |
| `app` | `path` (caminho do .exe), `args` (lista de argumentos) |

### Dias válidos

`segunda` · `terca` · `quarta` · `quinta` · `sexta` · `sabado` · `domingo`

> Lista vazia indica **todos os dias**.

---

## Scripts de atalho gerados

```
estudar                   →  myc tui --group estudar
estudar <subcomando>      →  myc run estudar <subcomando>
estudar <dia> <subcomando> →  myc run estudar <dia> <subcomando>
```

---

## Estrutura do projeto

```
cli_automatizacao_rotina/
├── myc/
│   ├── __init__.py
│   ├── __main__.py        # entry point
│   ├── cli.py             # comandos Click (com novos agent-*)
│   ├── config.py          # config.json
│   ├── monitor.py         # detecção de monitores
│   ├── runner.py          # execução de ações
│   ├── tui.py             # navegação visual
│   ├── agent.py           # ciclo de vida de agentes
│   ├── agent_plugins.py   # sistema de plugins (specialists + companies)
│   ├── department.py      # sistema de departamentos
│   ├── plugin_installer.py # instalação de plugins
│   ├── plugin_manager.py  # bundles de specialists e companies
│   └── html_dashboard.py  # dashboard web
│
├── plugins/
│   ├── specialists/       # 64 agentes especialistas individuais
│   ├── companies/         # 14 empresas com multi-agentes
│   ├── departments/       # 13 departamentos/equipes
│   └── middlewares/       # 5 modificadores de prompt/output
│
├── docs/                  # Documentação detalhada por tipo
│   ├── ARCHITECTURE.md    # Visão geral da arquitetura
│   ├── specialists/       # Docs de cada specialist (64)
│   ├── companies/         # Docs de cada company (14)
│   ├── departments/       # Docs de cada department (13)
│   └── middlewares/       # Docs de cada middleware (5)
│
├── pyproject.toml
├── requirements.txt
└── install.ps1
```

---

## Dependências

| Pacote | Uso |
|--------|-----|
| `click` | Framework CLI |
| `rich` | Output formatado e tabelas |
| `questionary` | Menus interativos |
| `screeninfo` | Detecção de monitores |
| `pyinstaller` | Build de executavel |

---

## Build

```powershell
python build_exe.py
# Gera: dist/myc.exe (~20MB)
```

---

## Dashboard Web

```powershell
myc config-html    # abre dashboard em localhost:8787
```

Mostra agentes, rotinas, plugins, historico e estatísticas em página web interativa.

---

## Licença

MIT
