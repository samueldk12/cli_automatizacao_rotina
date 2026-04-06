# Plugin System - Complete Reference

This document catalogs every plugin bundle and plugin available in the Claude Code Agent Plugin System. It covers installation, usage examples, and the full plugin lifecycle.

---

## Table of Contents

- [Quick Start](#quick-start)
  - [Installing Bundles](#installing-bundles)
  - [Installing All Bundles](#installing-all-bundles)
  - [Launching Agents](#launching-agents)
  - [Creating Custom Plugins](#creating-custom-plugins)
- [Plugin Hooks & Lifecycle](#plugin-hooks--lifecycle)
- [Bundle Reference](#bundle-reference)
  - [1. Marketing](#1-marketing)
  - [2. Game Design](#2-game-design)
  - [3. Advogacia (Brazilian Law)](#3-advocacia-brazilian-law)
  - [4. Jornalismo](#4-jornalismo)
  - [5. OSINT](#5-osint)
  - [6. Segurança Web](#6-segurança-web)
  - [7. Bug Bounty](#7-bug-bounty)
  - [8. Visão Computacional](#8-visão-computacional)
  - [9. Fullstack](#9-fullstack)
  - [10. App Mobile](#10-app-mobile)
  - [11. Ideias](#11-ideias)
  - [12. Vendas](#12-vendas)
  - [13. Data Engineering](#13-data-engineering)
  - [14. Software Engineering](#14-software-engineering)
  - [15. Computer Engineering](#15-computer-engineering)
  - [16. Professor](#16-professor)
- [Plugin Composition Examples](#plugin-composition-examples)

---

## Quick Start

### Installing Bundles

Install a single bundle by its ID:

```bash
myc agent bundle-install <bundle_id>
```

Example:

```bash
myc agent bundle-install marketing
```

### Installing All Bundles

Install every available bundle at once:

```bash
myc agent bundle-install --all
```

### Launching Agents

After installing a bundle, launch an agent configured with its plugins:

```bash
myc agent launch <name>
```

Example:

```bash
myc agent launch social_media
```

### Creating Custom Plugins

Add your own plugin with:

```bash
myc agent plugin-add
```

This interactive command guides you through plugin creation, including hook configuration, context injection, and post-launch actions.

---

## Plugin Hooks & Lifecycle

Plugins execute at three distinct phases of an agent's lifecycle:

| Hook | When It Runs | Purpose |
|---|---|---|
| `PRE_LAUNCH` | Before the agent starts | Validate environment, load configuration, check prerequisites, set up initial state |
| `CONTEXT` | During agent execution | Inject specialized knowledge, rules, templates, or domain-specific instructions into the agent's reasoning |
| `POST_LAUNCH` | After the agent finishes | Validate output, format results, trigger follow-up actions, generate reports |

**Hook Execution Flow:**

```
PRE_LAUNCH → Agent Executes (with CONTEXT hooks active) → POST_LAUNCH
```

**Example hook configuration** (auto-generated when you build a custom plugin):

```json
{
  "hook": "CONTEXT",
  "inject": "specialized_instructions.md",
  "priority": 10
}
```

---

## Bundle Reference

### 1. Marketing

**Bundle ID:** `marketing`

**Overview:** End-to-end marketing automation toolkit for digital marketing teams, content creators, and growth professionals. Automates social media strategy, SEO optimization, copywriting, and campaign orchestration.

**Target Users:** Marketing managers, content strategists, social media coordinators, SEO specialists, advertising professionals.

#### Plugins

| Plugin | Description | Real-World Use Case |
|---|---|---|
| `social_media` | Plans, generates, and schedules social media content across platforms (X, LinkedIn, Instagram, TikTok). Analyzes engagement patterns and optimal posting times. | A brand manager needs a 30-day content calendar for a product launch. The plugin analyzes brand voice, audience demographics, competitor activity, and generates platform-specific posts with hashtags, media suggestions, and a publishing schedule. |
| `seo_analyst` | Analyzes website SEO health, keyword gaps, competitor rankings, and on-page optimization opportunities. Generates actionable SEO audit reports. | An e-commerce site is losing organic traffic. The plugin crawls the site, identifies 47 pages with missing meta descriptions, 12 keyword cannibalization conflicts, and 23 technical SEO issues, then provides a prioritized fix list. |
| `copywriter` | Writes persuasive marketing copy: landing pages, email campaigns, ad creatives, product descriptions, blog posts. Adapts tone to brand guidelines and target audience. | A startup needs landing page copy for a new SaaS product. The plugin produces a value proposition, hero text, feature-benefit sections, social proof blocks, and three CTA variations, all A/B tested in structure. |
| `campaign_manager` | Designs multi-channel marketing campaigns with budget allocation, timeline, KPIs, and channel mix strategy. Tracks campaign performance metrics. | A retailer plans a Black Friday campaign. The plugin maps the customer journey from awareness to conversion across email, social, paid search, and display ads, with daily budgets, creative briefs, and success metrics. |

#### What Agents Accomplish

| Scenario | Plugins Used | Outcome |
|---|---|---|
| Launch a new product on 4 platforms in 2 weeks | `social_media` + `copywriter` + `campaign_manager` | Complete launch kit: 60+ posts, landing page copy, email sequence, ad creatives, and a day-by-day rollout calendar |
| Recover declining organic traffic | `seo_analyst` + `copywriter` | Audit report identifying root causes + 30 SEO-optimized articles targeting high-opportunity keywords |
| Build a brand from scratch | All 4 | Brand voice guidelines, 90-day social calendar, website copy, SEO strategy, and integrated campaign plan |

**Installation:**

```bash
myc agent bundle-install marketing
```

---

### 2. Game Design

**Bundle ID:** `gamedesign`

**Overview:** Complete game design toolkit for indie developers, game studios, and interactive media creators. Covers level architecture, narrative design, game mechanics balancing, and UX optimization.

**Target Users:** Game designers, narrative designers, level designers, indie devs, game UX researchers.

#### Plugins

| Plugin | Description | Real-World Use Case |
|---|---|---|
| `level_designer` | Designs game levels with layout maps, pacing curves, encounter design, reward placement, and player guidance. Supports 2D, 3D, and procedural generation. | Designing a Metroidvania-style game with 25 interconnected rooms. The plugin creates room layouts with backtracking routes, ability-gated progression paths, enemy encounter zones, and hidden secret areas with a complete flow diagram. |
| `game_narrative` | Creates branching storylines, character arcs, dialogue trees, lore, and world-building documents. Supports multiple narrative structures (linear, branching, emergent). | Writing an RPG with 4 factions and 12 main quests. The plugin generates faction histories, 3 playable character backgrounds, a branching quest tree with 6 endings, and 200+ lines of contextual dialogue. |
| `mechanics_balancer` | Analyzes and balances game mechanics: damage formulas, economy systems, difficulty curves, progression rates, and stat distributions. Uses mathematical modeling for fairness. | Balancing a deck-building card game's 150 cards. The plugin calculates expected value for each card, identifies 12 overpowered and 8 underpowered cards, suggests numerical adjustments, and simulates 10,000 matches to verify balance. |
| `game_ux` | Audits and designs game user interfaces, control schemes, feedback systems, accessibility features, and player onboarding flows. | Onboarding new players in a complex strategy game. The plugin designs a 4-phase tutorial system, contextual tooltips, adaptive difficulty hints, and an accessible UI color scheme with full colorblind support. |

#### What Agents Accomplish

| Scenario | Plugins Used | Outcome |
|---|---|---|
| Prototype a new game concept | `level_designer` + `game_narrative` + `mechanics_balancer` | Playable paper prototype: room layouts, story outline, balanced stat sheets, and a design document ready for prototyping |
| Polish an existing game | All 4 | UX audit report, retuned difficulty curves, dialogue polish pass, and level pacing improvements |
| Design a mobile puzzle game | `level_designer` + `mechanics_balancer` + `game_ux` | 100 levels with progressive difficulty, monetization-balanced economy, and touch-optimized UI |

**Installation:**

```bash
myc agent bundle-install gamedesign
```

---

### 3. Advogacia (Brazilian Law)

**Bundle ID:** `advogacia`

**Overview:** Legal practice toolkit specialized in Brazilian law. Automates legislation research, contract drafting, petition writing, and jurisprudence analysis. Complies with Brazilian legal standards and formats.

**Target Users:** Brazilian lawyers, law firms, legal departments, law students, paralegals.

#### Plugins

| Plugin | Description | Real-World Use Case |
|---|---|---|
| `legislacao_br` | Searches and analyzes Brazilian federal, state, and municipal legislation. Tracks constitutional amendments, laws, decrees, and normative instructions. Keeps up with legal changes. | A lawyer needs to verify current labor law provisions for a consultation. The plugin retrieves the latest CLT articles on remote work regulations, cross-references recent MPVs, and summarizes applicable provisions with article citations. |
| `contratos_br` | Drafts and reviews legal contracts following Brazilian legal standards. Generates standardized clauses, identifies risky provisions, and ensures compliance with the Brazilian Civil Code. | A company needs a software development contract. The plugin generates a complete contract with scope definition, payment terms, IP clauses, confidentiality, termination conditions, and dispute resolution -- all compliant with the Codigo Civil and Marco Civil da Internet. |
| `peticoes` | Drafts legal petitions (inicial, contestacao, recurso, etc.) in proper Brazilian legal format. Auto-formats according to court requirements and includes proper legal citations. | Filing a consumer protection lawsuit. The plugin drafts a `peticao inicial` with facts, legal grounds (CDC articles), damages calculation, evidence list, and requested relief, formatted per TJSP standards. |
| `jurisprudencia` | Searches and analyzes Brazilian court decisions across STF, STJ, TRFs, and TREs. Identifies relevant case law, tracks precedent trends, and extracts legal reasoning patterns. | Preparing a defense against an employment lawsuit. The plugin finds 15 relevant STJ decisions on similar claims, extracts the winning arguments from 8 of them, and identifies 3 distinguishing factors for the current case. |

#### What Agents Accomplish

| Scenario | Plugins Used | Outcome |
|---|---|---|
| Handle a complete civil case | `jurisprudencia` + `peticoes` + `legislacao_br` | Full case file: petition with case law citations, legal framework analysis, and opposing counsel counter-argument preparation |
| Corporate contract review | `contratos_br` + `legislacao_br` | Contract risk assessment report with flagged clauses, suggested revisions, and applicable law citations |
| Constitutional law research | `jurisprudencia` + `legislacao_br` | Comprehensive legal opinion with STF precedent analysis and constitutional provisions |

**Installation:**

```bash
myc agent bundle-install advocacia
```

---

### 4. Jornalismo

**Bundle ID:** `jornalismo`

**Overview:** Professional journalism toolkit for newsrooms, investigative reporters, and independent journalists. Supports editorial planning, fact-checking, news writing, and editorial management.

**Target Users:** Journalists, editors, reporters, newsroom managers, fact-checkers, editorial boards.

#### Plugins

| Plugin | Description | Real-World Use Case |
|---|---|---|
| `pauta_journal` | Plans and organizes journalistic assignments: story pitches, interview scheduling, source mapping, field reporting logistics, and deadline management. | Covering a city council election. The plugin creates a complete coverage plan: candidate profiles to research, key issues to investigate, interview targets, event calendar, data sources to FOIA, and a team assignment schedule. |
| `fact_checker` | Verifies claims, statistics, quotes, and statements from primary sources. Cross-references academic databases, official records, and expert sources. Generates fact-check reports with confidence ratings. | Verifying a politician's claim about crime statistics. The plugin traces the data to its original source (IBGE/SSP), compares it with independent studies, identifies selective framing, and writes a fact-check article with methodology. |
| `redacao_news` | Writes news articles following journalistic standards: inverted pyramid, AP style, headline/subtitle structure, lead paragraphs, and attribution rules. Adapts to breaking news, features, and investigative formats. | Breaking news coverage of an economic policy change. Within minutes, the plugin produces a headline, lead paragraph with 5Ws, background context, expert quotes, market impact analysis, and a sidebar explaining implications for readers. |
| `editorial` | Drafts opinion pieces, editorials, and column articles with argumentative structure, evidence-based reasoning, and editorial voice. Manages publication guidelines and ethical standards. | A newspaper editorial board needs an opinion piece on education reform. The plugin researches current policies, synthesizes expert opinions, constructs a persuasive argument, and produces a 800-word editorial with proper sourcing. |

#### What Agents Accomplish

| Scenario | Plugins Used | Outcome |
|---|---|---|
| Cover a major news event | All 4 | Assignment brief, real-time fact-checked articles, source verification reports, and an editorial wrap-up |
| Investigative series | `pauta_journal` + `fact_checker` + `redacao_news` | 5-part investigative series with mapped sources, verified data, and long-form articles |
| Fact-checking operation | `fact_checker` + `redacao_news` | 20 verified fact-checks on political claims, published as shareable articles with confidence ratings |

**Installation:**

```bash
myc agent bundle-install jornalismo
```

---

### 5. OSINT

**Bundle ID:** `osint`

**Overview:** Open Source Intelligence gathering and analysis toolkit. Automates data collection from public sources, source credibility analysis, digital footprint mapping, and cross-correlation of intelligence data points.

**Target Users:** Investigators, security analysts, journalists, law enforcement, corporate intelligence teams, threat hunters.

#### Plugins

| Plugin | Description | Real-World Use Case |
|---|---|---|
| `osint_collector` | Gathers intelligence from public sources: social media, public records, DNS records, WHOIS data, search engine results, and public APIs. Organizes collected data into structured intelligence reports. | Investigating a suspected corporate fraud. The plugin maps company registration records, domain ownership history, executive social media profiles, news mentions, regulatory filings, and financial disclosures into a single intelligence dossier. |
| `source_analyzer` | Evaluates the credibility, reliability, and potential bias of information sources. Assigns confidence scores, identifies conflicts of interest, and traces information provenance through source chains. | A journalist receives a leaked document. The plugin analyzes metadata, cross-checks claims against known records, assesses the source's track record, identifies potential motivations, and assigns a reliability score with reasoning. |
| `digital_footprint` | Maps an entity's (person, organization, domain) digital presence across platforms. Identifies connected accounts, activity patterns, content history, and network connections. | Corporate due diligence on a potential business partner. The plugin maps the CEO's digital footprint: LinkedIn connections, public speaking engagements, previous company affiliations, social media activity, and any adverse media mentions. |
| `data_correlator` | Cross-references and correlates data points from multiple sources to reveal hidden connections, patterns, timelines, and intelligence gaps. Builds relationship graphs and timeline visualizations. | Connecting dots in a financial fraud investigation. The plugin correlates bank records, property registrations, shell company ownership, travel patterns, and communication metadata to reveal a hidden network of 7 connected entities. |

#### What Agents Accomplish

| Scenario | Plugins Used | Outcome |
|---|---|---|
| Full entity investigation | All 4 | Complete intelligence dossier: data sources, credibility assessments, digital footprint map, and correlation analysis with timeline |
| Threat actor profiling | `osint_collector` + `digital_footprint` + `data_correlator` | Actor profile with infrastructure, tools, TTPs, and attributed historical activity |
| Source verification pipeline | `source_analyzer` + `osint_collector` | Automated source credibility pipeline with scored intelligence feed |

**Installation:**

```bash
myc agent bundle-install osint
```

---

### 6. Segurança Web

**Bundle ID:** `seguranca_web`

**Overview:** Web security auditing toolkit for identifying, analyzing, and remediating web application vulnerabilities. Follows industry standards including OWASP Top 10, and provides hardening guides.

**Target Users:** Web developers, security engineers, DevSecOps teams, IT administrators, security auditors.

#### Plugins

| Plugin | Description | Real-World Use Case |
|---|---|---|
| `web_auditor` | Performs automated web application security audits: scans for vulnerabilities, misconfigurations, exposed endpoints, SSL/TLS issues, and security header analysis. Generates remediation reports. | Auditing an e-commerce platform before launch. The plugin scans all 340 endpoints, identifies 12 medium-severity and 3 high-severity issues (including an exposed admin panel and missing CSP headers), and provides step-by-step fixes. |
| `owasp_checker` | Tests applications against the OWASP Top 10 vulnerability categories. Checks for injection flaws, broken authentication, sensitive data exposure, XXE, broken access control, and more. | PCI DSS compliance preparation for a payment processor. The plugin systematically tests against all OWASP Top 10 categories, documenting test procedures, results, evidence, and remediation status for each control. |
| `pentest_helper` | Assists penetration testers with reconnaissance, vulnerability exploitation guidance, payload generation, and post-exploitation techniques. Maintains testing methodology and documentation. | A red team assessment of a client's web application. The plugin provides a structured testing playbook, generates targeted payloads for identified vulnerabilities, documents the attack chain, and produces a professional pentest report. |
| `hardening_guide` | Generates server, application, and infrastructure hardening guides tailored to the specific technology stack. Includes configuration templates, security baselines, and compliance checklists. | Securing a production Kubernetes cluster. The plugin generates hardening guides for: container image scanning, network policies, RBAC configuration, secrets management, audit logging, and compliance with CIS Kubernetes benchmarks. |

#### What Agents Accomplish

| Scenario | Plugins Used | Outcome |
|---|---|---|
| Pre-launch security review | All 4 | Full audit report with OWASP scores, pentest findings, remediation roadmap, and hardened deployment configuration |
| Compliance preparation | `owasp_checker` + `web_auditor` | Compliance-ready audit documentation with evidence collection for PCI DSS, SOC 2, or ISO 27001 |
| Incident response | `pentest_helper` + `web_auditor` | Attack vector analysis, compromise timeline, and immediate containment steps |

**Installation:**

```bash
myc agent bundle-install seguranca_web
```

---

### 7. Bug Bounty

**Bundle ID:** `bugbounty`

**Overview:** Bug bounty hunting toolkit covering the full vulnerability research lifecycle: reconnaissance, exploit development, report writing, and vulnerability triage for responsible disclosure programs.

**Target Users:** Bug bounty hunters, security researchers, penetration testers, vulnerability analysts, red team operators.

#### Plugins

| Plugin | Description | Real-World Use Case |
|---|---|---|
| `recon` | Performs systematic reconnaissance on target applications: subdomain enumeration, technology fingerprinting, endpoint discovery, parameter fuzzing, and attack surface mapping. | Starting a bug bounty engagement on a large scope program with 50+ subdomains. The plugin maps the entire attack surface, discovers 12 undocumented API endpoints, identifies 8 technology stacks, and prioritizes targets by potential impact. |
| `exploit_writer` | Drafts proof-of-concept exploits for identified vulnerabilities: XSS, SQLi, SSRF, RCE, IDOR, and logic flaws. Formats exploits for responsible disclosure with clear reproduction steps. | Writing a PoC for a blind SQL injection. The plugin crafts a safe, non-destructive exploit script that proves the vulnerability without data extraction or service disruption, with step-by-step reproduction instructions for the vendor. |
| `bounty_report` | Generates professional bug bounty reports with executive summaries, technical details, impact assessment, CVSS scoring, reproduction steps, and remediation recommendations. Meets platform requirements (HackerOne, Bugcrowd). | Submitting a critical vulnerability to a HackerOne program. The plugin generates a report with: clear title, severity justification (CVSS 9.1), detailed reproduction steps with screenshots, impact analysis, suggested fix, and impact on affected users. |
| `vuln_triage` | Assists with vulnerability triage: deduplication analysis, severity scoring, false positive filtering, impact validation, and prioritization for bug bounty program operators. | A bug bounty program receives 200 submissions in a week. The plugin triages each report, identifies 15 duplicates, flags 30 false positives, validates 23 genuine findings, and assigns severity scores with justification for each. |

#### What Agents Accomplish

| Scenario | Plugins Used | Outcome |
|---|---|---|
| End-to-end bug bounty | All 4 | Recon map, working PoC exploits, professional submission reports, and triage analysis for multiple targets |
| Vulnerability research sprint | `recon` + `exploit_writer` | Attack surface map with 5 confirmed vulnerabilities and reproduction-ready PoCs |
| Bug bounty program management | `vuln_triage` + `bounty_report` | Automated submission processing pipeline with scoring, deduplication, and response templates |

**Installation:**

```bash
myc agent bundle-install bugbounty
```

---

### 8. Visão Computacional

**Bundle ID:** `visao_computacional`

**Overview:** Computer vision development toolkit covering the full ML pipeline: architecture design, dataset preparation, model training, and deployment for production computer vision systems.

**Target Users:** ML engineers, computer vision researchers, data scientists, AI software developers, robotics engineers.

#### Plugins

| Plugin | Description | Real-World Use Case |
|---|---|---|
| `cv_architect` | Designs computer vision system architectures: model selection (CNN, ViT, YOLO, etc.), pipeline design, preprocessing strategies, and deployment architecture for specific use cases. | Building a real-time defect detection system for a manufacturing line. The plugin recommends a YOLOv8 architecture with custom heads, designs the image preprocessing pipeline, specifies hardware requirements (Edge TPU), and creates a system architecture diagram. |
| `dataset_builder` | Creates and prepares training datasets: image collection strategies, annotation schema design, data augmentation pipelines, dataset splits, and quality assurance checks. | Preparing a dataset for medical image classification. The plugin designs an annotation schema with 12 pathology classes, creates an augmentation pipeline with 20 transforms, generates stratified train/val/test splits, and implements inter-rater agreement checks. |
| `model_trainer` | Configures and manages model training: hyperparameter tuning, training loops, evaluation metrics, early stopping, mixed precision training, and experiment tracking. | Training an object detection model on a custom dataset. The plugin sets up a training configuration with cosine learning rate scheduling, focal loss for class imbalance, 10-epoch warm-up, and integrates with experiment tracking for comparison runs. |
| `cv_deployer` | Deploys trained models to production: ONNX/TensorRT conversion, API service creation, scaling configuration, monitoring setup, and continuous retraining pipelines. | Deploying a face recognition model to a cloud API serving 10,000 requests/minute. The plugin converts the model to TensorRT, creates a FastAPI service with batching, configures auto-scaling, adds performance monitoring, and sets up a retraining trigger pipeline. |

#### What Agents Accomplish

| Scenario | Plugins Used | Outcome |
|---|---|---|
| Full CV pipeline | All 4 | Complete system: architecture docs, curated dataset, trained model with metrics report, and production deployment |
| Rapid prototyping | `cv_architect` + `model_trainer` | Architecture recommendation + trained baseline model with benchmarks in hours |
| Model optimization | `cv_deployer` + `model_trainer` | Production-optimized model with 3x inference speed improvement through quantization and TensorRT |

**Installation:**

```bash
myc agent bundle-install visao_computacional
```

---

### 9. Fullstack

**Bundle ID:** `fullstack`

**Overview:** Complete full-stack web development toolkit. Covers frontend development, backend services, database design, and DevOps deployment for production-ready web applications.

**Target Users:** Full-stack developers, web agencies, startups, freelance developers, engineering teams.

#### Plugins

| Plugin | Description | Real-World Use Case |
|---|---|---|
| `frontend_dev` | Builds modern frontend applications with component architecture, responsive design, state management, and accessibility. Supports React, Vue, Angular, and modern CSS frameworks. | Building a SaaS dashboard from a Figma design. The plugin generates a Next.js application with 28 components, responsive layouts, dark mode support, chart integrations, skeleton loaders, and complete accessibility (WCAG 2.1 AA) compliance. |
| `backend_dev` | Designs and implements backend APIs and services: REST/GraphQL endpoints, authentication, business logic, middleware, error handling, and API documentation. | Creating a multi-tenant SaaS backend. The plugin builds a Node.js/Express service with JWT authentication, role-based access control, Stripe integration for billing, webhook handlers, rate limiting, and OpenAPI documentation. |
| `database_designer` | Designs database schemas: relational and NoSQL, migration strategies, indexing, query optimization, and data modeling for specific application requirements. | Designing a database for a food delivery platform. The plugin creates a PostgreSQL schema with 24 tables, designs proper indexes for common queries, implements soft deletes, and generates migration scripts with seed data. |
| `devops_deploy` | Configures CI/CD pipelines, container orchestration, monitoring, logging, and deployment automation for production environments. | Deploying the fullstack application to AWS. The plugin creates Docker configurations, GitHub Actions CI/CD pipelines, Terraform infrastructure, CloudWatch dashboards, and a blue-green deployment strategy with rollback automation. |

#### What Agents Accomplish

| Scenario | Plugins Used | Outcome |
|---|---|---|
| Ship a SaaS product | All 4 | Production-ready application: frontend, API, database, CI/CD, monitoring, and deployment scripts |
| API migration | `backend_dev` + `database_designer` | New API with schema migrations, zero-downtime deployment strategy, and backward compatibility layer |
| Performance overhaul | `frontend_dev` + `devops_deploy` | Optimized frontend with Core Web Vitals compliance + CDN configuration + caching strategy |

**Installation:**

```bash
myc agent bundle-install fullstack
```

---

### 10. App Mobile

**Bundle ID:** `app_mobile`

**Overview:** Mobile application development toolkit covering architecture, UI design, native platform integration, and app store preparation for iOS and Android applications.

**Target Users:** Mobile developers, cross-platform developers, product managers, indie app developers, mobile agencies.

#### Plugins

| Plugin | Description | Real-World Use Case |
|---|---|---|
| `mobile_architect` | Designs mobile application architectures: cross-platform strategy (React Native, Flutter), native module design, offline capability, state management, and performance optimization. | Architecting a social media app for iOS and Android. The plugin recommends Flutter for shared UI with platform channel integrations, designs a layered architecture (presentation/domain/data), plans offline-first data sync, and specifies push notification handling. |
| `ui_mobile` | Creates mobile UI components and screen designs following platform guidelines (Material Design 3, Human Interface Guidelines). Generates responsive layouts, animations, and dark mode support. | Designing an e-commerce mobile app. The plugin creates 18 screen designs: product catalog, search, filters, product detail, cart, checkout, order tracking, profile, settings -- all with platform-native look and feel and gesture navigation. |
| `native_bridge` | Develops native code bridges for platform-specific functionality: camera, biometrics, GPS, Bluetooth, NFC, health APIs, and custom native modules for cross-platform apps. | Building a fitness app needing Apple HealthKit and Google Fit integration. The plugin writes platform channels for health data access, implements biometric authentication, creates a location module for GPS tracking, and handles background task management. |
| `app_store_prep` | Prepares applications for app store submission: metadata optimization, screenshots, privacy policies, app store descriptions, review guidelines compliance, and release management. | Submitting an app to both Apple App Store and Google Play. The plugin generates optimized app descriptions (4000 bytes Apple / 8000 bytes Google), screenshot sets for all device sizes, keyword lists, privacy nutrition labels, and a phased rollout strategy. |

#### What Agents Accomplish

| Scenario | Plugins Used | Outcome |
|---|---|---|
| Ship a mobile app | All 4 | Complete app: architecture, UI screens, native integrations, and ready-for-submission packages |
| Cross-platform port | `mobile_architect` + `ui_mobile` | Existing iOS app ported to Android with shared codebase and platform-adapted UI |
| App store optimization | `app_store_prep` + `ui_mobile` | Optimized store listing with platform-specific screenshots and A/B tested descriptions |

**Installation:**

```bash
myc agent bundle-install app_mobile
```

---

### 11. Ideias

**Bundle ID:** `ideias`

**Overview:** Innovation and ideation toolkit for entrepreneurs, product teams, and creative professionals. Structures the journey from raw idea to validated concept to minimum viable product.

**Target Users:** Entrepreneurs, product managers, innovation teams, startup founders, creative directors, intrapreneurs.

#### Plugins

| Plugin | Description | Real-World Use Case |
|---|---|---|
| `brainstorm` | Facilitates structured brainstorming sessions: idea generation techniques, mind mapping, SCAMPER method, random stimulus, and cross-pollination from adjacent domains. | A product team needs new features for their project management tool. The plugin runs a 30-idea brainstorming session using 5 techniques, clusters ideas into 6 themes, scores each by feasibility/impact, and presents the top 10 with rationale. |
| `design_thinking` | Applies design thinking methodology: empathize (user research), define (problem statements), ideate (solution concepts), prototype, and test. Guides teams through each phase with frameworks and templates. | Redesigning a healthcare patient experience. The plugin guides through user interviews (empathy maps from 20 patients), problem reframing (5 alternative problem statements), solution ideation (3 directions), and test plan design for rapid validation. |
| `idea_validator` | Validates ideas through market analysis, competitive landscape, feasibility assessment, customer persona alignment, and risk evaluation. Provides go/no-go recommendations with confidence scores. | An entrepreneur wants to launch an AI personal finance app. The plugin analyzes market size ($12.4B by 2027), 47 competitors, technical feasibility (existing APIs), user willingness to pay, regulatory considerations, and provides a validation score of 7.2/10 with specific risk factors. |
| `mvp_builder` | Plans and scopes minimum viable products: feature prioritization, user flow design, technology stack selection, build timeline, and launch criteria. Focuses on fastest path to validated learning. | Building an MVP for a verified review platform. The plugin identifies 3 must-have features (review submission, verification flow, search), 5 should-haves, and 12 won't-haves for v1. Creates a 6-week build plan with weekly milestones and launch success metrics. |

#### What Agents Accomplish

| Scenario | Plugins Used | Outcome |
|---|---|---|
| Zero to MVP | All 4 | 50 ideas generated, 1 validated concept, user research plan, and scoped MVP with 6-week roadmap |
| Feature innovation | `brainstorm` + `idea_validator` | 30 new feature ideas with validation scores and implementation priority |
| Pivot analysis | `design_thinking` + `idea_validator` + `mvp_builder` | Repositioning strategy with validated new direction and revised MVP scope |

**Installation:**

```bash
myc agent bundle-install ideias
```

---

### 12. Vendas

**Bundle ID:** `vendas`

**Overview:** Sales and growth toolkit for business development teams, founders, and sales professionals. Covers pitch creation, funnel optimization, business modeling, and growth strategies.

**Target Users:** Sales teams, founders, business development managers, growth marketers, consultants.

#### Plugins

| Plugin | Description | Real-World Use Case |
|---|---|---|
| `sales_pitch` | Creates customized sales pitches and presentations: value propositions, objection handling, social proof integration, demo scripts, and personalized outreach messages. | Preparing pitches for an enterprise SaaS selling to Fortune 500 CTOs. The plugin produces 3 pitch variants (technical, business, ROI-focused), a 20-slide deck outline, 15 common objections with rebuttals, and email templates for each stage of the sales cycle. |
| `sales_funnel` | Designs and optimizes sales funnels: lead capture, qualification, nurturing sequences, conversion optimization, and retention strategies. Identifies bottlenecks and leakage points. | Optimizing a B2B SaaS funnel with 2% conversion rate. The plugin analyzes each stage, identifies that MQL-to-SQL conversion drops 40%, recommends adding lead scoring criteria, redesigns the nurture sequence with 7 targeted emails, and projects 3.5x improvement. |
| `business_model` | Analyzes and designs business models using frameworks like Business Model Canvas, Lean Canvas, and revenue model analysis. Evaluates unit economics and scalability. | A marketplace startup needs to validate its business model. The plugin creates a complete Business Model Canvas, analyzes unit economics (CAC $45, LTV $280, payback 3.2 months), identifies the key risk (supply-side liquidity), and suggests 3 alternative revenue models. |
| `growth_hacker` | Designs growth experiments and strategies: viral loops, referral programs, content-led growth, product-led growth, partnership strategies, and rapid experimentation frameworks. | Growing a B2C fintech app from 10K to 100K users. The plugin designs a referral program (give $10, get $10), a content strategy targeting 50 long-tail keywords, a PR strategy, 3 growth experiments with success metrics, and a 90-day growth roadmap. |

#### What Agents Accomplish

| Scenario | Plugins Used | Outcome |
|---|---|---|
| Go-to-market strategy | All 4 | Business model validation, sales playbook, optimized funnel, and 90-day growth plan with experiment pipeline |
| Enterprise sales enablement | `sales_pitch` + `sales_funnel` | Customized pitch kits per buyer persona, qualification framework, and automated nurture sequences |
| Revenue optimization | `business_model` + `growth_hacker` | Unit economics analysis, pricing recommendations, and growth experiment backlog |

**Installation:**

```bash
myc agent bundle-install vendas
```

---

### 13. Data Engineering

**Bundle ID:** `data_engineering`

**Overview:** Data engineering toolkit for building robust data infrastructure. Covers ETL pipeline development, data quality assurance, pipeline architecture, and data warehouse design.

**Target Users:** Data engineers, analytics engineers, data architects, BI developers, data platform teams.

#### Plugins

| Plugin | Description | Real-World Use Case |
|---|---|---|
| `etl_builder` | Designs and implements ETL/ELT pipelines: data extraction from multiple sources, transformation logic, loading strategies, incremental processing, and error handling. Supports Airflow, dbt, Spark, and more. | Building a data pipeline that ingests data from Salesforce, Stripe, and PostgreSQL into a data lake. The plugin designs an Airflow DAG with 12 tasks, implements incremental extraction using watermark columns, creates data quality checks, and handles schema evolution. |
| `pipeline_designer` | Architects data processing pipelines: stream vs. batch processing, data lineage, orchestration design, scaling strategies, and fault tolerance. Creates pipeline diagrams and runbooks. | Designing a real-time analytics pipeline for clickstream data at 50K events/second. The plugin architects a Kafka-based streaming pipeline with Flink processing, S3 landing zone, Athena querying, and a batch reconciliation job with SLA monitoring. |
| `data_quality` | Implements data quality frameworks: profiling, validation rules, anomaly detection, completeness checks, freshness monitoring, and automated alerting. Builds data quality scorecards. | A company's reports are unreliable due to bad data. The plugin implements 45 validation rules across 12 tables, sets up automated anomaly detection, creates a data quality dashboard with real-time scoring, and establishes data SLAs with alerting. |
| `warehouse_architect` | Designs data warehouse and data lakehouse architectures: dimensional modeling (star/snowflake schemas), partitioning strategies, materialized views, and query optimization. | Building a modern data platform for a retail company. The plugin designs a medallion architecture (bronze/silver/gold layers), 8 star schemas covering sales, inventory, marketing, and customer domains, and optimizes for both BI queries and ML feature extraction. |

#### What Agents Accomplish

| Scenario | Plugins Used | Outcome |
|---|---|---|
| Build a data platform | All 4 | Complete data architecture: warehouse schemas, ETL pipelines, quality framework, and orchestration setup |
| Data quality remediation | `data_quality` + `etl_builder` | Quality audit, 40+ validation rules, automated monitoring, and corrected ingestion pipelines |
| Real-time analytics | `pipeline_designer` + `warehouse_architect` | Streaming pipeline architecture with dimensional model and sub-second query performance |

**Installation:**

```bash
myc agent bundle-install data_engineering
```

---

### 14. Software Engineering

**Bundle ID:** `software_engineering`

**Overview:** Software engineering excellence toolkit covering architecture design, code review, testing strategies, and CI/CD automation for production software teams.

**Target Users:** Software engineers, tech leads, engineering managers, QA engineers, DevOps practitioners, architects.

#### Plugins

| Plugin | Description | Real-World Use Case |
|---|---|---|
| `software_architect` | Designs software system architectures: microservices vs. monolith decisions, API design, system decomposition, technology selection, scalability planning, and architecture decision records (ADRs). | Designing a microservices architecture for a growing e-commerce platform. The plugin analyzes current monolith pain points, proposes 8 services bounded by domain, defines inter-service communication patterns, creates an architecture diagram, and writes 12 ADRs with trade-off analysis. |
| `code_reviewer` | Performs automated and manual code reviews: style consistency, security vulnerabilities, performance issues, code complexity analysis, best practices adherence, and constructive feedback generation. | Reviewing a pull request with 2,000 lines of changes. The plugin identifies 14 issues: 3 security concerns (SQL injection risk, hardcoded secrets, missing input validation), 5 performance issues (N+1 queries, missing indexes), 4 style violations, and 2 architectural concerns. Each with specific fix suggestions. |
| `test_engineer` | Designs testing strategies: unit tests, integration tests, e2e tests, API contract testing, performance tests, and test data management. Generates test plans and actual test code. | Creating a test strategy for a payment processing service. The plugin designs a testing pyramid: 200 unit tests, 45 integration tests with mocked payment gateways, 12 e2e tests covering happy paths and edge cases, load tests for 1000 TPS, and a test data management strategy. |
| `ci_cd_expert` | Configures continuous integration and deployment pipelines: build automation, test orchestration, artifact management, environment promotion, rollback strategies, and GitOps workflows. | Setting up CI/CD for a team releasing 50+ times per week. The plugin creates a GitHub Actions pipeline with feature branch validation, canary deployments, automated rollback on error threshold breach, Slack notifications, environment promotion from staging to production. |

#### What Agents Accomplesh

| Scenario | Plugins Used | Outcome |
|---|---|---|
| Platform architecture | All 4 | Documented architecture, reviewed codebase, comprehensive test suite, and automated CI/CD pipeline |
| Legacy modernization | `software_architect` + `code_reviewer` + `test_engineer` | Strangler pattern migration plan, technical debt assessment, and test coverage baseline |
| Release process automation | `ci_cd_expert` + `test_engineer` | Automated pipeline with quality gates, reducing release time from 2 days to 45 minutes |

**Installation:**

```bash
myc agent bundle-install software_engineering
```

---

### 15. Computer Engineering

**Bundle ID:** `computer_engineering`

**Overview:** Low-level and systems engineering toolkit for embedded development, IoT, network analysis, and operating system internals. Targets hardware-adjacent software development.

**Target Users:** Embedded systems engineers, IoT developers, network engineers, kernel developers, systems programmers, hardware engineers.

#### Plugins

| Plugin | Description | Real-World Use Case |
|---|---|---|
| `embedded_dev` | Develops embedded software: firmware architecture, microcontroller programming, RTOS integration, peripheral drivers, low-power design, and hardware abstraction layers. | Developing firmware for a smart thermostat. The plugin creates an ARM Cortex-M firmware with FreeRTOS, temperature/humidity sensor drivers, PWM fan control, BLE communication stack, power management for battery mode, and over-the-air update capability. |
| `iot_engineer` | Designs IoT system architectures: device connectivity, protocol selection (MQTT, CoAP, HTTP), edge computing, cloud integration, device management, and fleet OTA updates. | Building an industrial IoT monitoring system for 500 factory sensors. The plugin designs an MQTT-based architecture with edge gateways, time-series database, alerting system, device provisioning workflow, and a dashboard for fleet monitoring across 3 sites. |
| `network_analyzer` | Analyzes network traffic, protocols, performance, and security. Creates packet analysis workflows, network topology maps, and performance baseline reports. | Troubleshooting intermittent connectivity in a corporate network. The plugin designs a packet capture strategy, analyzes TCP retransmission patterns, identifies a misconfigured load balancer causing connection pooling issues, and recommends specific configuration changes. |
| `os_internals` | Analyzes and explains operating system internals: kernel architecture, system calls, memory management, process scheduling, file systems, and kernel module development. | Developing a custom Linux kernel module for a specialized hardware driver. The plugin explains the kernel subsystem interfaces, generates module skeleton code with proper memory management, interrupt handling, and sysfs integration, and describes testing and debugging approaches. |

#### What Agents Accomplesh

| Scenario | Plugins Used | Outcome |
|---|---|---|
| IoT product development | All 4 | Firmware, IoT architecture, network design, and kernel driver -- full embedded product stack |
| Network forensics | `network_analyzer` + `os_internals` | Packet analysis, root cause identification, kernel-level explanation of observed behavior |
| Embedded optimization | `embedded_dev` + `os_internals` | Firmware with 60% power reduction through kernel-level power management and peripheral optimization |

**Installation:**

```bash
myc agent bundle-install computer_engineering
```

---

### 16. Professor

**Bundle ID:** `professor`

**Overview:** Educational content creation and teaching toolkit for educators, instructional designers, and academic professionals. Covers lesson planning, assessment design, pedagogy strategies, and learning content development.

**Target Users:** Teachers, professors, instructional designers, corporate trainers, content creators, education administrators.

#### Plugins

| Plugin | Description | Real-World Use Case |
|---|---|---|
| `lesson_planner` | Creates structured lesson plans: objectives aligned with curriculum standards, activity sequences, timing, differentiation strategies, assessment methods, and resource lists. | Planning a semester of high school Physics (18 weeks). The plugin creates weekly lesson plans covering mechanics, thermodynamics, waves, and electricity, with learning objectives aligned to BNCC standards, lab activities, formative assessments, and pacing guide. |
| `exam_creator` | Generates exams and assessments across difficulty levels: multiple choice, short answer, essays, practical problems, and rubrics. Creates balanced test blueprints and alternate versions. | Creating a final exam for an undergraduate Database Systems course. The plugin generates a 3-hour exam with 20 multiple choice, 5 short answer, 2 SQL practical problems, and 1 design essay. Includes grading rubrics, an alternate version, and a test blueprint mapping to course outcomes. |
| `didatica` | Provides pedagogical strategies: active learning techniques, engagement methods, classroom management, feedback frameworks, and learning style adaptations. | A professor wants to improve student engagement in a 200-student lecture. The plugin suggests peer instruction with clickers, think-pair-share activities, real-time polling, case-based learning segments, and a feedback system that increased engagement by 40% in similar contexts. |
| `content_creator_edu` | Creates educational content: slide decks, handouts, video scripts, interactive exercises, infographics, and supplementary reading materials across formats. | Producing content for an online machine learning course. The plugin creates: 40 slide decks with visual explanations, 12 video scripts with timing cues, 6 Jupyter notebook exercises, 4 cheat sheets, and a glossary of 150 terms with examples. |

#### What Agents Accomplesh

| Scenario | Plugins Used | Outcome |
|---|---|---|
| Course development | All 4 | Complete course: 18-week lesson plan, exams with rubrics, teaching strategies, and all learning materials |
| Assessment redesign | `exam_creator` + `didatica` | Balanced assessment strategy with varied formats, difficulty progression, and active learning integration |
| Online course creation | `content_creator_edu` + `lesson_planner` | 40 hours of content with slides, exercises, videos scripts, and structured lesson sequence |

**Installation:**

```bash
myc agent bundle-install professor
```

---

## Plugin Composition Examples

Plugins gain extraordinary power when combined across bundles. Here are real scenarios where multi-bundle compositions deliver complete workflows.

### Scenario: Build and Launch a SaaS Startup

| Phase | Bundle | Plugin | Action |
|---|---|---|---|
| Ideation | `ideias` | `brainstorm` + `idea_validator` + `mvp_builder` | Generate, validate, and scope the product |
| Architecture | `software_engineering` | `software_architect` | Design the system architecture |
| Development | `fullstack` | `frontend_dev` + `backend_dev` + `database_designer` | Build the application |
| Launch Prep | `app_mobile` | `mobile_architect` + `ui_mobile` | Create companion mobile app |
| Marketing | `marketing` | All 4 | Build marketing machine: SEO, content, campaigns, social |
| Sales | `vendas` | `sales_pitch` + `sales_funnel` | Create sales engine and funnel |
| Growth | `vendas` | `growth_hacker` | Design growth experiments |
| Security | `seguranca_web` | `web_auditor` + `hardening_guide` | Audit and harden before launch |

### Scenario: Investigative Journalism Series

| Phase | Bundle | Plugin | Action |
|---|---|---|---|
| Research | `osint` | `osint_collector` + `data_correlator` | Gather and correlate intelligence data |
| Verification | `osint` | `source_analyzer` | Verify source credibility |
| Planning | `jornalismo` | `pauta_journal` | Plan coverage and assign reporters |
| Writing | `jornalismo` | `redacao_news` | Draft articles with journalistic standards |
| Fact-Checking | `jornalismo` | `fact_checker` | Verify all claims before publication |
| Promotion | `marketing` | `social_media` + `copywriter` | Promote series across platforms |

### Scenario: Smart Factory Digital Transformation

| Phase | Bundle | Plugin | Action |
|---|---|---|---|
| IoT Design | `computer_engineering` | `iot_engineer` + `embedded_dev` | Design sensor network and firmware |
| Network | `computer_engineering` | `network_analyzer` | Design and analyze factory network |
| Data Pipeline | `data_engineering` | `pipeline_designer` + `etl_builder` | Build real-time data ingestion |
| Quality | `data_engineering` | `data_quality` | Implement data quality framework |
| Security | `seguranca_web` | `web_auditor` + `hardening_guide` | Secure the entire stack |
| Visualization | `fullstack` | `frontend_dev` + `backend_dev` | Build monitoring dashboard |

### Scenario: Educational Game for Kids

| Phase | Bundle | Plugin | Action |
|---|---|---|---|
| Curriculum | `professor` | `lesson_planner` + `content_creator_edu` | Design educational content and learning objectives |
| Game Design | `gamedesign` | `level_designer` + `game_narrative` + `mechanics_balancer` | Design engaging game world and balance learning with fun |
| Mobile App | `app_mobile` | `ui_mobile` + `native_bridge` | Build child-friendly interface with parental controls |
| Launch | `marketing` | `campaign_manager` + `copywriter` | Market to schools and parents |

---

## Complete Bundle Index

| # | Bundle ID | Plugins | Domain |
|---|---|---|---|
| 1 | `marketing` | social_media, seo_analyst, copywriter, campaign_manager | Digital Marketing |
| 2 | `gamedesign` | level_designer, game_narrative, mechanics_balancer, game_ux | Game Development |
| 3 | `advocacia` | legislacao_br, contratos_br, peticoes, jurisprudencia | Brazilian Law |
| 4 | `jornalismo` | pauta_journal, fact_checker, redacao_news, editorial | Journalism |
| 5 | `osint` | osint_collector, source_analyzer, digital_footprint, data_correlator | Intelligence |
| 6 | `seguranca_web` | web_auditor, owasp_checker, pentest_helper, hardening_guide | Web Security |
| 7 | `bugbounty` | recon, exploit_writer, bounty_report, vuln_triage | Bug Bounty |
| 8 | `visao_computacional` | cv_architect, dataset_builder, model_trainer, cv_deployer | Computer Vision |
| 9 | `fullstack` | frontend_dev, backend_dev, database_designer, devops_deploy | Full-Stack Dev |
| 10 | `app_mobile` | mobile_architect, ui_mobile, native_bridge, app_store_prep | Mobile Apps |
| 11 | `ideias` | brainstorm, design_thinking, idea_validator, mvp_builder | Innovation |
| 12 | `vendas` | sales_pitch, sales_funnel, business_model, growth_hacker | Sales & Growth |
| 13 | `data_engineering` | etl_builder, pipeline_designer, data_quality, warehouse_architect | Data Engineering |
| 14 | `software_engineering` | software_architect, code_reviewer, test_engineer, ci_cd_expert | Software Eng. |
| 15 | `computer_engineering` | embedded_dev, iot_engineer, network_analyzer, os_internals | Systems Eng. |
| 16 | `professor` | lesson_planner, exam_creator, didatica, content_creator_edu | Education |

**Total:** 16 bundles, 64 plugins.

---

## Custom Plugin Development

### Creating Your Own Plugin

Use the interactive command to scaffold a new plugin:

```bash
myc agent plugin-add
```

The wizard will prompt you for:

1. **Plugin name** -- unique identifier (e.g., `my_custom_plugin`)
2. **Description** -- what the plugin does
3. **Hook type** -- `PRE_LAUNCH`, `CONTEXT`, or `POST_LAUNCH`
4. **Bundle assignment** -- existing bundle or new bundle
5. **Priority** -- execution order within the hook (lower runs first)
6. **Resources** -- files, templates, or scripts the plugin requires

### Example Custom Plugin Structure

```
plugins/
  my_custom_plugin/
    plugin.json          # Plugin metadata and hook config
    hooks/
      pre_launch.sh      # PRE_LAUNCH hook script
      context.md         # CONTEXT instructions injected into agent
      post_launch.py     # POST_LAUNCH processing
    templates/
      output.md          # Output template
```

**plugin.json:**

```json
{
  "name": "my_custom_plugin",
  "description": "Custom plugin for specialized workflow",
  "version": "1.0.0",
  "hooks": [
    {
      "type": "PRE_LAUNCH",
      "script": "hooks/pre_launch.sh",
      "priority": 1
    },
    {
      "type": "CONTEXT",
      "instructions": "hooks/context.md",
      "priority": 5
    },
    {
      "type": "POST_LAUNCH",
      "script": "hooks/post_launch.py",
      "priority": 10
    }
  ]
}
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|---|---|---|
| "Bundle not found" | Typo in bundle ID | Run `myc agent bundle-list` to see available bundles |
| Plugin hooks not firing | Incorrect hook configuration | Verify hook type matches `PRE_LAUNCH`, `CONTEXT`, or `POST_LAUNCH` exactly |
| Context not injected | Missing or misnamed context file | Ensure the `instructions` path in `plugin.json` points to an existing file |
| Bundle install fails | Network or permission issue | Check network connectivity and run with appropriate permissions |
| Agent launch fails | Bundle not installed | Run `myc agent bundle-install <id>` before launching |

---

*This documentation was auto-generated. For questions or contributions, refer to the project maintainers.*
