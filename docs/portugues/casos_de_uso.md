# Casos de Uso — Cenarios Reais

Este documento demonstra como o sistema de agentes do MYC resolve problemas reais atraves de plugins compostos.

---

## Caso de Uso 1: Uma Empresa IA Documenta o Codebase

**Cenario:** A `ai_company` foi implantada para documentar o sistema de plugins do MYC. Veja como funcionou:

### O que Aconteceu

Um agente da AI Company foi lancado com a tarefa: *"Analise a arquitetura de plugins deste projeto e produza documentacao abrangente."*

A estrutura da empresa inclui:

| Sub-agente | Papel | Specialists Usados |
|------------|-------|-------------------|
| Tech Writer | Escreve documentacao tecnica | frontend_dev (estrutura), brainstorm |
| Content Strategist | Organiza estrategia de conteudo | content_creator_edu, design_thinking |
| Documentation Architect | Planeja estrutura da documentacao | software_architect, lesson_planner |
| Technical Reviewer | Revisa por precisao | code_reviewer, fact_checker |

### Processo

1. **Tech Writer** — Analisou cada arquivo de plugin em `plugins/specialists/`, `plugins/companies/`, `plugins/departments/` e `plugins/middlewares/`, extraindo NAME, DESCRIPTION, SPECIALISTS e hooks exportados.

2. **Content Strategist** — Organizou os dados brutos em hierarquia de conteudo: visao geral do README → Arquitetura → Paginas Individuais de Plugin → Casos de Uso.

3. **Documentation Architect** — Projetou a estrutura de diretorios, tabelas de referencia cruzada e formato de matriz para mapeamentos specialist-para-departamento.

4. **Technical Reviewer** — Verificou que todas as contagens batem com arquivos reais, todos os comandos funcionam contra o codebase CLI, e os exemplos sao precisos.

### Resultado

- `README.md` atualizado com contagens completas de plugins (65 specialists, 27 companies, 13 departments, 8 middlewares)
- Documentacao bilingue criada (`docs/ingles/` e `docs/portugues/`)
- Demonstracoes de casos de uso mostrando composicao multi-plugin

**Licao principal:** Ao compor multiplos specialists atraves de uma empresa, a qualidade da documentacao superou qualquer specialist individual. O Tech Writer coletou dados, o Strategist organizou, o Architect projetou a estrutura, e o Reviewer validou a precisao.

---

## Caso de Uso 2: Construir um SaaS do Zero

**Fase 1 — Ideacao:**
```bash
myc agent bundle-install ideias
myc agent-specialist brainstorm "gere ideias de SaaS para automacao de pequenas empresas"
myc agent-specialist idea_validator "avalie viabilidade de mercado de SaaS de faturamento automatizado"
```

**Fase 2 — Arquitetura:**
```bash
myc agent-specialist software_architect "desenhe arquitetura de microservicos para SaaS de faturamento"
myc agent-specialist database_designer "desenhe schema de banco multi-tenant"
```

**Fase 3 — Desenvolvimento:**
```bash
myc agent-company dev_agency tech_lead "crie plano de sprint semana 1-4"
myc agent-company dev_agency dev_backend "construa API de registro e autenticacao"
myc agent-company dev_agency dev_frontend "construa dashboard de onboarding"
myc agent-company dev_agency devops "configure CI/CD com GitHub Actions"
```

**Fase 4 — Marketing e Lancamento:**
```bash
myc agent-company marketing_agency company "crie estrategia de mercado"
myc agent-specialist copywriter "escreva copy da landing page"
myc agent-specialist seo_analyst "analise oportunidades de palavras-chave"
```

---

## Caso de Uso 3: Pipeline de Auditoria de Seguranca

```bash
# Reconhecimento
myc agent-company bounty_company recon_specialist "mapeie superficie de ataque de exemplo.com"

# Auditoria
myc agent-specialist web_auditor -o security_checker "audite exemplo.com/webapp"

# Verificacao OWASP
myc agent-specialist owasp_checker "teste contra OWASP Top 10"

# Relatorio Profissional
myc agent-company bounty_company report_writer "gere relatorio pronto para HackerOne"
```

---

## Caso de Uso 4: Criacao de Conteudo Educacional

```bash
# Planejamento do Curso
myc agent-specialist lesson_planner "crie curso de Python de 12 semanas para iniciantes"

# Criacao de Conteudo
myc agent-specialist content_creator_edu "gere apresentacao para aula de variaveis Python"

# Avaliacao
myc agent-specialist exam_creator "crie prova intermediaria com 30 questoes e rubrica"

# Estrategia de Ensino
myc agent-specialist didatica "sugira tecnicas de aprendizagem ativa para aula magna (80 alunos)"
```

---

## Caso de Uso 5: Workflow Juridico Brasileiro

```bash
# Pesquisa Legislativa
myc agent-specialist legislacao_br "encontre disposicoes atuais da CLT sobre trabalho remoto"

# Redacao de Contrato
myc agent-specialist contratos_br "redija contrato de servicos de desenvolvimento de software"

# Peticao
myc agent-specialist peticoes "redija acao de protecao ao consumidor (produto defeituoso)"

# Jurisprudencia
myc agent-specialist jurisprudencia "encontre precedentes do STJ sobre danos morais por acidente de trabalho"
```

---

## Caso de Uso 6: Pipeline de Game Design

```bash
# Conceito
myc agent-company game_studio_company level_designer "desenhe 10 fases para um platforma 2D"

# Narrativa
myc agent-company game_studio_company narrative_writer "crie historia ramificada com 3 finais"

# Balanceamento
myc agent-specialist mechanics_balancer "balanceie formulas de dano e curva de progresso"

# UX
myc agent-specialist game_ux "desenhe fluxo de onboarding para jogadores casuais mobile"
```

---

## Caso de Uso 7: Investigacao OSINT

```bash
# Investigacao de Entidade
myc agent-department osint "crie workflow de investigacao para due diligence corporativa"

# Correlacao
myc agent-specialist data_correlator "correlacione dados de multiplos fontes publicas"

# Pegada Digital
myc agent-specialist digital_footprint "mapeie presenca digital da entidade alvo"
```

---

## Caso de Uso 8: Arquitetura de Pipeline de Dados

```bash
# Arquitetura
myc agent-specialist warehouse_architect "desenhe arquitetura de medalhao para plataforma de varejo"

# ETL
myc agent-specialist etl_builder "construa DAG Airflow para ingestao salesforce + stripe"

# Qualidade
myc agent-specialist data_quality "implemente regras de validacao e deteccao de anomalias"

# Tempo Real
myc agent-specialist pipeline_designer "desenhe pipeline streaming para analise de clickstream"
```

---

## Composicoes Multi-Bundle

Cenarios de maior impacto combinam specialists de multiplos bundles:

### Serie de Jornalismo Investigativo
| Bundle | Specialist | Acao |
|--------|-----------|------|
| `osint` | osint_collector | Coletar inteligencia |
| `osint` | data_correlator | Conectar pontos |
| `jornalismo` | pauta_journal | Planejar cobertura |
| `jornalismo` | redacao_news | Escrever materias |
| `jornalismo` | fact_checker | Verificar alegacoes |
| `marketing` | social_media | Promover nas redes |

### Transformacao Digital de Fabrica Inteligente
| Bundle | Specialist | Acao |
|--------|-----------|------|
| `computer_engineering` | iot_engineer | Projetar rede de sensores |
| `computer_engineering` | embedded_dev | Escrever firmware |
| `data_engineering` | pipeline_designer | Construir ingestao streaming |
| `data_engineering` | etl_builder | Criar pipelines ETL |
| `software_engineering` | software_architect | Projetar sistema de monitoramento |
| `fullstack` | frontend_dev | Construir dashboard |
| `linguistics` | pt_en_translator | Traduzir documentacao tecnico-cientifica PT↔EN |
| `linguistics` | en_es_translator | Traduzir comunicacao com stakeholders ES |

---

## Auto-Atribuicao de Plugins por Papel

Ao criar um agente com um papel especifico, o MYC auto-atribui bundles relevantes:

| Papel do Agente | Bundles Auto-Attribuidos |
|-----------------|-------------------------|
| `dev` | fullstack, software_engineering, computer_engineering, data_engineering |
| `artist` | gamedesign |
| `writer` | jornalismo, advocacia |
| `researcher` | osint, bugbounty, seguranca_web |
| `educator` | professor |
| `business` | vendas, ideias, marketing |
