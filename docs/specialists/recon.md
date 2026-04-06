# Especialista: Recon
**ID:** `recon`
**Department:** Bug Bounty
**Arquivo:** `plugins/specialists/recon.py`

## Descricao

Especialista em metodologia de reconnaissance para bug bounty, mapeando superficies de ataque de forma metodica e abrangente.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_RECON=active`

### Contexto Injetado

- **Enumeracao de subdominios:** Passiva (CT logs, mecanismos de busca, PassiveTotal) e ativa (Subfinder, Amass, brute force)
- **Scanning de portas:** TCP completo, identificacao de servicos, UDP scanning, service version detection
- **Identificacao de tecnologias:** Wappalyzer, fingerprinting de frameworks, deteccao CDN/WAF
- **Descoberta de endpoints:** Crawling, fuzzing de diretorios (SecLists, FFUF, Gobuster), robots.txt, sitemap.xml
- **Descoberta de parametros:** Arjun, x8, JS files, formulários
- **Endpoints ocultos:** JS files, apps mobile, backups, configuracoes expostas
- **Analise de JS:** URLs, API keys, tokens, rotas, chamadas a APIs externas
- **APIs:** Swagger/OpenAPI, GraphQL introspection, WebSockets, SSE
- **Assets em cloud:** S3 buckets, blob storage, GCS, Lambda

## Uso

```bash
myc agent add-plugin meu_agente recon
```

## Especialistas Relacionados
- [OSINT Collector](osint_collector.md) — Coleta OSINT
- [Bounty Recon](bounty_recon.md) — Recon avancado para bug bounty
- [Network Analyzer](network_analyzer.md) — Analise de redes
- [Digital Footprint](digital_footprint.md) — Pegada digital

## Parte do Department
**Empresa de Bug Bounty** — Department de Reconhecimento
