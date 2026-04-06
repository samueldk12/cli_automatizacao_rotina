# Use Cases — Real-World Scenarios

This document demonstrates how MYC's agent system solves real-world problems through composed plugins.

---

## Use Case 1: A AI Company Documents a Codebase

**Scenario:** The `ai_company` was deployed to document the MYC plugin system. Here's how it works:

### What Happened

An AI Company agent was launched with the task: *"Analyze this project's plugin architecture and produce comprehensive documentation."*

The company structure includes:

| Sub-agent | Role | Specialists Used |
|-----------|------|-----------------|
| Tech Writer | Writes technical documentation | frontend_dev (for structure), brainstorm |
| Content Strategist | Organizes content strategy | content_creator_edu, design_thinking |
| Documentation Architect | Plans documentation structure | software_architect, lesson_planner |
| Technical Reviewer | Reviews for accuracy | code_reviewer, fact_checker |

### Process

1. **Tech Writer** — Analyzed each plugin file in `plugins/specialists/`, `plugins/companies/`, `plugins/departments/`, and `plugins/middlewares/`, extracting NAME, DESCRIPTION, SPECIALISTS, and exported hooks.

2. **Content Strategist** — Organized the raw data into a content hierarchy: README overview → Architecture → Individual Plugin Pages → Use Cases.

3. **Documentation Architect** — Designed the directory structure, cross-referencing tables, and matrix format for specialist-to-department mappings.

4. **Technical Reviewer** — Verified that all counts match actual files, all commands work against the CLI codebase, and examples are accurate.

### Output

- Updated `README.md` with complete plugin counts (65 specialists, 27 companies, 13 departments, 8 middlewares)
- Created bilingual documentation (`docs/ingles/` and `docs/portugues/`)
- Generated use case demonstrations showing multi-plugin composition

**Key insight:** By composing multiple specialists through a company, the documentation quality exceeded what any single specialist could produce. The Tech Writer gathered raw data, the Strategist organized it, the Architect designed the structure, and the Reviewer validated accuracy.

---

## Use Case 2: Build a SaaS from Scratch

**Phase 1 — Ideation:**
```bash
myc agent bundle-install ideias
myc agent-specialist brainstorm "generate SaaS ideas for small business automation"
myc agent-specialist idea_validator "assess market viability of automated invoicing SaaS"
```

**Phase 2 — Architecture:**
```bash
myc agent-specialist software_architect "design microservices architecture for invoicing SaaS"
myc agent-specialist database_designer "design multi-tenant database schema"
```

**Phase 3 — Development:**
```bash
myc agent-company dev_agency tech_lead "create sprint plan week 1-4"
myc agent-company dev_agency dev_backend "build user registration and auth API"
myc agent-company dev_agency dev_frontend "build onboarding dashboard"
myc agent-company dev_agency devops "set up CI/CD with GitHub Actions"
```

**Phase 4 — Marketing & Launch:**
```bash
myc agent-company marketing_agency Company "create go-to-market strategy"
myc agent-specialist copywriter "write landing page copy"
myc agent-specialist seo_analyst "analyze keyword opportunities"
```

---

## Use Case 3: Security Audit Pipeline

```bash
# Recon
myc agent-company bounty_company recon_specialist "map attack surface of example.com"

# Audit
myc agent-specialist web_auditor -o security_checker "audit example.com/webapp"

# OWASP Check
myc agent-specialist owasp_checker "test against OWASP Top 10"

# Professional Report
myc agent-company bounty_company report_writer "generate HackerOne-ready report"
```

---

## Use Case 4: Educational Content Creation

```bash
# Course Planning
myc agent-specialist lesson_planner "create 12-week Python course for beginners"

# Content Creation
myc agent-specialist content_creator_edu "generate slide deck for Python variables lesson"

# Assessment
myc agent-specialist exam_creator "create midterm exam with 30 questions and rubric"

# Teaching Strategy
myc agent-specialist didatica "suggest active learning techniques for large lecture (80 students)"
```

---

## Use Case 5: Brazilian Legal Workflow

```bash
# Legislation Research
myc agent-specialist legislacao_br "find current CLT provisions on remote work"

# Contract Drafting
myc agent-specialist contratos_br "draft software development service contract"

# Petition Writing
myc agent-specialist peticoes "draft consumer protection lawsuit (defective product)"

# Case Law
myc agent-specialist jurisprudencia "find STJ precedents on moral damages from workplace accidents"
```

---

## Use Case 6: Game Design Pipeline

```bash
# Concept
myc agent-company game_studio_company level_designer "design 10 levels for a 2D platformer"

# Narrative
myc agent-company game_studio_company narrative_writer "create branching storyline with 3 endings"

# Balance
myc agent-specialist mechanics_balancer "balance damage formulas and progression curve"

# UX
myc agent-specialist game_ux "design onboarding flow for casual mobile players"
```

---

## Use Case 7: OSINT Investigation

```bash
# Entity Investigation
myc agent-department osint "create investigation workflow for corporate due diligence"

# Cross-reference
myc agent-specialist data_correlator "correlate data from multiple public sources"

# Digital Footprint
myc agent-specialist digital_footprint "map digital presence of target entity"
```

---

## Use Case 8: Data Pipeline Architecture

```bash
# Architecture
myc agent-specialist warehouse_architect "design medallion architecture for retail data platform"

# ETL
myc agent-specialist etl_builder "build Airflow DAG for salesforce + stripe ingestion"

# Quality
myc agent-specialist data_quality "implement validation rules and anomaly detection"

# Real-time
myc agent-specialist pipeline_designer "design streaming pipeline for clickstream analytics"
```

---

## Use Case 8: Translation & Localization Pipeline

**Scenario:** A software company needs to translate its technical documentation to 5 languages.

```bash
# Use the linguistics department as the coordinating team
myc agent-department linguistics "translate the API documentation to all supported language pairs"

# Individual translation specialists
myc agent-specialist pt_en_translator "translate contract from Portuguese to English"
myc agent-specialist en_es_translator "translate user manual to Spanish (Latin America)"
myc agent-specialist en_zh_translator "translate technical specs to Simplified Chinese"
myc agent-specialist en_fr_translator "translate press release to French"
myc agent-specialist en_ja_translator "translate onboarding guide to Japanese"
```

### Linguistics Department Flow

```
Source Text
    │
    ├── Identify language pair
    │
    ├─ PT↔EN ─→ pt_en_translator  [technical docs, contracts, emails]
    ├─ EN↔ES ─→ en_es_translator  [manuals, UI, communications]
    ├─ EN↔ZH ─→ en_zh_translator  [specs, UI, marketing]
    ├─ EN↔FR ─→ en_fr_translator  [press releases, legal docs]
    └─ EN↔JA ─→ en_ja_translator  [user guides, marketing, UI]
    │
    ▼
Idiomatic Translations + Translation Notes
```

---

## Multi-Bundle Compositions

The highest-impact scenarios combine specialists across multiple bundles:

### Smart Factory Digital Transformation
| Bundle | Specialist | Action |
|--------|-----------|--------|
| `computer_engineering` | iot_engineer | Design sensor network |
| `computer_engineering` | embedded_dev | Write firmware |
| `data_engineering` | pipeline_designer | Build streaming ingestion |
| `software_engineering` | software_architect | Design monitoring system |
| `fullstack` | frontend_dev | Build dashboard |
| `linguistics` | pt_en_translator | Translate documentation PT↔EN |
| `linguistics` | en_zh_translator | Translate specs EN↔ZH |

### Global SaaS Product
| Bundle | Specialist | Action |
|--------|-----------|--------|
| `ideias` | brainstorm, idea_validator | Validate product idea |
| `fullstack` | frontend_dev, backend_dev | Build the product |
| `marketing` | copywriter, seo_analyst | English marketing |
| `linguistics` | pt_en_translator, en_es_translator, en_ja_translator | Localize to 5 languages |

---

## Plugin Auto-Assignment by Role

When creating an agent with a specific role, MYC auto-assigns relevant bundles:

| Agent Role | Auto-Assigned Bundles |
|------------|----------------------|
| `dev` | fullstack, software_engineering, computer_engineering, data_engineering |
| `artist` | gamedesign |
| `writer` | jornalismo, advocacia |
| `researcher` | osint, bugbounty, seguranca_web |
| `educator` | professor |
| `business` | vendas, ideias, marketing |
