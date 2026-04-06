# Especialista: Hardening Guide
**ID:** `hardening_guide`
**Department:** Seguranca
**Arquivo:** `plugins/specialists/hardening_guide.py`

## Descricao

Especialista em hardening de sistemas e aplicacoes, fornecendo orientacoes praticas e implementaveis para fortalecer a postura de seguranca.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_HARDENING=active`

### Contexto Injetado

- **Benchmarks CIS:** Linhas de base de configuracao segura, least privilege
- **TLS/SSL:** TLS 1.2 minimo, cipher suites, HSTS, OCSP stapling
- **Headers HTTP:** CSP, HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy
- **Implementacao de CSP:** Whitelist de origens, nonces/hashes, report-only
- **Seguranca de cookies:** Secure, HttpOnly, SameSite, dominio, expiracao
- **Validacao de entrada:** Allowlists, normalizacao, Unicode
- **Codificacao de output:** Context-aware encoding, auto-escaping
- **Queries parametrizadas:** Prepared statements, ORMs, stored procedures
- **Rate limiting:** IP, usuario, endpoint, sliding window
- **WAF:** OWASP ModSecurity CRS, custom rules
- **Monitoramento:** SIEM, alertas automatizados, baseline de comportamento

## Uso

```bash
myc agent add-plugin meu_agente hardening_guide
```

## Especialistas Relacionados
- [OWASP Checker](owasp_checker.md) — OWASP Top 10
- [Pentest Helper](pentest_helper.md) — Pentest
- [Vuln Triage](vuln_triage.md) — Triagem de vulnerabilidades

## Parte do Department
**Seguranca**
