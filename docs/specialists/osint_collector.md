# Especialista: OSINT Collector
**ID:** `osint_collector`
**Department:** OSINT / Bug Bounty
**Arquivo:** `plugins/specialists/osint_collector.py`

## Descricao

Especialista em coleta de inteligencia de fontes abertas (OSINT), utilizando tecnicas avancadas de pesquisa sempre dentro da legalidade.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_OSINT=active`

### Contexto Injetado

- **Pesquisa avancada:** Google dorks (site:, filetype:, inurl:, intitle:, ext:, cache:, related:)
- **Inteligencia em redes sociais:** Facebook, Twitter/X, Instagram, LinkedIn, TikTok, Telegram, Reddit
- **Enumeracao de usernames:** Namechk, WhatsMyName, Sherlock
- **Inteligencia de e-mails:** Have I Been Pwned, Hunter.io
- **Pesquisa de dominios:** WHOIS historico, DNS reconnaissance, subdomain enumeration
- **Formas alternativas:** Wayback Machine, paginas em cache, Common Crawl

Diretrizes obrigatorias: apenas informacoes publicamente disponiveis e legais, respeitar LGPD.

## Uso

```bash
myc agent add-plugin meu_agente osint_collector
```

## Especialistas Relacionados
- [Source Analyzer](source_analyzer.md) — Analise de credibilidade
- [Digital Footprint](digital_footprint.md) — Mapeamento de presenca digital
- [Data Correlator](data_correlator.md) — Correlacao de dados

## Parte do Department
**OSINT**
