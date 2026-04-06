# Arquitetura de Plugins MYC

## Visao Geral

O sistema MYC utiliza uma arquitetura de plugins modular com 4 tipos de componentes que podem ser combinados hierarquicamente para criar agentes de IA especializados com comportamento altamente customizavel.

### Os 4 Tipos de Plugin

1. **Especialistas** (`plugins/specialists/`) -- 65 agentes especialistas individuais, cada um com conhecimento profundo em uma area especifica. Sao a unidade basica do sistema; todos os outros tipos de plugin os reutilizam.
2. **Empresas** (`plugins/companies/`) -- 14 empresas multi-agente que agrupam especialistas sob uma identidade organizacional, com sub-agentes que delegam tarefas aos especialistas apropriados.
3. **Departamentos** (`plugins/departments/`) -- 13 equipes tematicas que podem existir de forma independente ou como parte de uma empresa. Cada departamento coordena um grupo de especialistas para resolver problemas de um dominio.
4. **Middlewares** (`plugins/middlewares/`) -- 5 modificadores de prompt/saida que podem ser anexados a qualquer nivel (especialista, empresa ou departamento) para alterar o comportamento de entrada ou saida.

## Estrutura de Diretorios

```
plugins/
|-- specialists/          # 65 agentes especialistas individuais
|   |-- social_media.py
|   |-- seo_analyst.py
|   |-- copywriter.py
|   |-- frontend_dev.py
|   |-- backend_dev.py
|   |-- database_designer.py
|   |-- devops_deploy.py
|   |-- web_auditor.py
|   |-- pentest_helper.py
|   |-- legislacao_br.py
|   |-- contratos_br.py
|   |-- ... (65 no total)
|
|-- companies/            # 14 empresas multi-agente
|   |-- dev_agency.py
|   |-- ...
|
|-- departments/          # 13 departamentos tematicos
|   |-- marketing.py          # 4 especialistas
|   |-- dev_frontend.py       # 2 especialistas
|   |-- dev_backend.py        # 3 especialistas
|   |-- security.py           # 4 especialistas
|   |-- law_brazil.py         # 4 especialistas
|   |-- journalism.py         # 4 especialistas
|   |-- game_design.py        # 4 especialistas
|   |-- sales.py              # 4 especialistas
|   |-- data_eng.py           # 4 especialistas
|   |-- software_eng.py       # 4 especialistas
|   |-- devops.py             # 4 especialistas
|   |-- education.py          # 4 especialistas
|   |-- osint.py              # 4 especialistas
|
|-- middlewares/          # 5 middlewares
|   |-- prompt_enhancer.py      # prompt_modifier (pre)
|   |-- text_compressor.py      # output_modifier (post)
|   |-- security_checker.py     # content_filter (both)
|   |-- code_quality.py         # output_modifier (post)
|   |-- summarizer.py           # output_modifier (post)
|
|-- bundles/              # Pacotes de plugins para instalacao em lote
|
docs/
|-- departments/          # Documentacao de cada departamento
|   |-- marketing.md
|   |-- dev_frontend.md
|   |-- dev_backend.md
|   |-- security.md
|   |-- law_brazil.md
|   |-- journalism.md
|   |-- game_design.md
|   |-- sales.md
|   |-- data_eng.md
|   |-- software_eng.md
|   |-- devops.md
|   |-- education.md
|   |-- osint.md
|
|-- middlewares/          # Documentacao de cada middleware
|   |-- prompt_enhancer.md
|   |-- text_compressor.md
|   |-- security_checker.md
|   |-- code_quality.md
|   |-- summarizer.md
|
|-- ARCHITECTURE.md       # Este arquivo
```

## Interface de Plugins

### Especialistas

Cada especialista e um modulo Python que exportas as seguintes variaveis:

| Campo | Tipo | Descricao |
|---|---|---|
| `NAME` | str | Nome legivel do especialista |
| `DESCRIPTION` | str | Breve descricao da especialidade |
| `ROLE` | str | Descricao detalhada do papel usado como system prompt |
| `PRE_LAUNCH` | str | Instrucoes executadas antes do agente iniciar (opcional) |
| `POST_LAUNCH` | str | Instrucoes processadas apos a resposta do agente (opcional) |
| `CONTEXT()` | callable | Funcao que retorna contexto dinamico (opcional) |

**Hooks de ciclo de vida:**
- `PRE_LAUNCH`: Texto injetado no prompt antes da chamada ao agente. Usado para preparar contexto, carregar arquivos ou definir parametros.
- `POST_LAUNCH`: Texto processado apos a resposta do agente. Usado para formatar saida, salvar arquivos ou gerar artefatos.
- `CONTEXT()`: Funcao executada em tempo de execucao que pode retornar contexto dinamico baseado no estado atual (arquivos no disco, variaveis de ambiente, etc.).

### Empresas

Cada empresa agrega sub-agentes e especialistas sob uma identidade organizacional:

| Campo | Tipo | Descricao |
|---|---|---|
| `NAME` | str | Nome legivel da empresa |
| `DESCRIPTION` | str | Descricao do escopo da empresa |
| `SUB_AGENTS` | dict[str, dict] | Mapeamento de sub-agentes com seus papeis |
| `SPECIALISTS` | list[str] | Lista de IDs de especialistas disponiveis |
| `COMPANY_CONTEXT()` | callable | Retorna o contexto da empresa |
| `ROLE` | str | System prompt da empresa |

### Departamentos

Cada departamento coordena um grupo de especialistas de um dominio tematico:

| Campo | Tipo | Descricao |
|---|---|---|
| `NAME` | str | Nome legivel do departamento |
| `DESCRIPTION` | str | Descricao do escopo do departamento |
| `SPECIALISTS` | list[str] | Lista de IDs de especialistas que o departamento utiliza |
| `MIDDLEWARES` | list[str] | Lista de IDs de middlewares padrao do departamento |
| `PARENT_COMPANY` | str ou None | Empresa a qual este departamento pertence (None = independente) |
| `ROLE` | str | System prompt completo do departamento |
| `DEPARTMENT_CONTEXT()` | callable | Retorna contexto dinamico do departamento |

Departamentos podem existir de forma independente (`PARENT_COMPANY = None`) ou como parte de uma empresa. Quando vinculados a uma empresa, herdam o contexto e os sub-agentes da empresa pai.

### Middlewares

Middlewares sao modificadores que interceptam o fluxo de dados em diferentes pontos:

| Campo | Tipo | Descricao |
|---|---|---|
| `NAME` | str | Nome legivel do middleware |
| `DESCRIPTION` | str | Descricao do que o middleware faz |
| `MIDDLEWARE_TYPE` | str | Tipo: `prompt_modifier`, `output_modifier`, `content_filter` ou `agent_runner` |
| `RUNS_WHEN` | str | Quando executa: `pre` (antes), `post` (depois), `both` (ambos) ou `manual` (sob demanda) |
| `PROMPT_MODIFY(text, profile)` | callable | Modifica o texto do prompt antes do envio (obrigatorio para `prompt_modifier` e `content_filter`) |
| `OUTPUT_MODIFY(text, profile)` | callable | Modifica a saida do agente antes de exibir (obrigatorio para `output_modifier` e `content_filter`) |

**Tipos de Middleware:**
- `prompt_modifier` -- Altera o prompt de entrada. Sempre executa na fase `pre`. Ex: Prompt Enhancer.
- `output_modifier` -- Altera a saida do agente. Sempre executa na fase `post`. Ex: Text Compressor, Code Quality, Summarizer.
- `content_filter` -- Opera em ambas as fases, podendo modificar entrada e filtrar saida. Ex: Security Checker.
- `agent_runner` -- Executa um sub-agente interno como middleware (tipo avancado).

## Comandos CLI

Todos os comandos sao acessados via `myc agent`:

```bash
# Executar um especialista individual com middlewares opcionais
myc agent-specialist <nome> [-o middleware...] "query"

# Executar uma empresa, opcionalmente especificando um sub-agente
myc agent-company <empresa> [sub_agente] [-o middleware...] "query"

# Executar um departamento, opcionalmente vinculado a uma empresa
myc agent-department <dept> [-o middleware...] [-c empresa] "query"

# Instalar bundles de plugins
myc agent bundle-install --all
myc agent bundle-install <bundle_nome>
myc agent bundle-install <bundle_nome> --company

# Listar middlewares disponiveis
myc agent middleware --list

# Adicionar novo departamento
myc agent department-add

# Adicionar nova empresa
myc agent company-add
```

### Flags

| Flag | Comando | Descricao |
|---|---|---|
| `-o <middleware>` | specialist, company, department | Adiciona middleware ao pipeline de execucao. Pode ser usado multiplas vezes. |
| `-c <empresa>` | department | Vincula o departamento a uma empresa, herdando seu contexto. |
| `--list` | middleware | Lista todos os middlewares disponiveis com descricao. |
| `--list` | department | Lista todos os departamentos disponiveis. |
| `--list -c <empresa>` | department | Lista departamentos de uma empresa especifica. |
| `--all` | bundle-install | Instala todos os bundles disponiveis. |
| `--company` | bundle-install | Instala bundles de empresas em vez de departamentos. |

## Fluxo de Dados

O diagrama abaixo mostra como a informacao flui atraves do sistema de plugins quando middlewares, especialistas, departamentos e empresas sao combinados:

```
Entrada do Usuario ("query")
         |
         v
   +------------------+
   |  Middlewares PRE  | <---- prompt_modifier, content_filter (fase pre)
   |  (encadeados)     |      Transformam o prompt antes do envio
   +--------+---------+
            |
            v
   +------------------+
   |  Departamento     | <---- Define quais especialistas usar
   |  (SPECIALISTS)    |      Injeta DEPARTMENT_CONTEXT() + ROLE
   +--------+---------+
            |
            v
   +------------------+
   |  Empresa (opc.)   | <---- Se -c foi usado
   |  COMPANY_CONTEXT  |      Adiciona contexto e sub-agentes da empresa
   +--------+---------+
            |
            v
   +------------------+
   |  Especialista     | <---- ROLE + PRE_LAUNCH + CONTEXT()
   |  Selecionado      |      System prompt final montado
   +--------+---------+
            |
            v
   +------------------+
   |  LLM (Claude)    | <---- Geracao da resposta
   +--------+---------+
            |
            v
   +------------------+
   |  Middlewares POST | <---- output_modifier, content_filter (fase post)
   |  (encadeados)     |      Comprimem, resumem, verificam codigo/seguranca
   +--------+---------+
            |
            v
   +------------------+
   |  POST_LAUNCH      | <---- Hook do especialista (se definido)
   +--------+---------+
            |
            v
      Saida Final (terminal)
```

### Exemplo de Fluxo Completo

```bash
myc agent-department dev_backend \
  -o prompt_enhancer \
  -o code_quality \
  -c dev_agency \
  "crie uma API REST com autenticacao JWT"
```

1. **prompt_enhancer (PRE):** Reestrutura a query em secoes com contexto, objetivo e diretrizes.
2. **Departamento dev_backend:** Injeta ROLE do departamento + lista de especialistas (backend_dev, database_designer, devops_deploy).
3. **Empresa dev_agency:** Adiciona contexto da empresa (se configurado).
4. **Especialista selecionado:** O sistema seleciona o especialista mais relevante e monta o system prompt.
5. **LLM gera a resposta** com o contexto completo.
6. **code_quality (POST):** Analisa blocos de codigo na resposta, identifica problemas e anexa relatorio.
7. **POST_LAUNCH:** Executa hooks finais do especialista (ex: salvar arquivos).
8. **Saida exibida** no terminal com o codigo revisado e o relatorio de qualidade.

### Matriz de Middlewares

| Middleware | Tipo | Quando | Modifica Prompt | Modifica Saida |
|---|---|---|---|---|
| `prompt_enhancer` | prompt_modifier | pre | Sim | Nao |
| `text_compressor` | output_modifier | post | Nao | Sim |
| `security_checker` | content_filter | both | Sim | Sim |
| `code_quality` | output_modifier | post | Nao | Sim |
| `summarizer` | output_modifier | post | Nao | Sim |

### Especialistas por Departamento

| Departamento | Especialistas | Qty |
|---|---|---|
| marketing | social_media, seo_analyst, copywriter, campaign_manager | 4 |
| dev_frontend | frontend_dev, ui_mobile | 2 |
| dev_backend | backend_dev, database_designer, devops_deploy | 3 |
| security | web_auditor, owasp_checker, pentest_helper, hardening_guide | 4 |
| law_brazil | legislacao_br, contratos_br, peticoes, jurisprudencia | 4 |
| journalism | pauta_journal, fact_checker, redacao_news, editorial | 4 |
| game_design | level_designer, game_narrative, mechanics_balancer, game_ux | 4 |
| sales | sales_pitch, sales_funnel, business_model, growth_hacker | 4 |
| data_eng | etl_builder, pipeline_designer, data_quality, warehouse_architect | 4 |
| software_eng | software_architect, code_reviewer, test_engineer, ci_cd_expert | 4 |
| devops | devops_deploy, ci_cd_expert, network_analyzer, os_internals | 4 |
| education | lesson_planner, exam_creator, didatica, content_creator_edu | 4 |
| osint | osint_collector, source_analyzer, digital_footprint, data_correlator | 4 |

Todos os 13 departamentos sao independentes (`PARENT_COMPANY = None`), podendo ser usados diretamente ou vinculados a qualquer empresa via flag `-c`.
