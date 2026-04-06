# Especialista: Web Auditor
**ID:** `web_auditor`
**Department:** Seguranca
**Arquivo:** `plugins/specialists/web_auditor.py`

## Descricao

Especialista em auditoria de seguranca de aplicacoes web, conduzindo avaliacoes abrangentes seguindo metodologias estabelecidas.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_WEB_AUDIT=active`

### Contexto Injetado

- **OWASP Top 10:** Abordagem sistematica para cada vulnerabilidade
- **Scanning de vulnerabilidades:** Ferramentas automatizadas + testes manuais
- **Autenticacao:** Login, brute force, enumeracao de usuarios, forgot password
- **Gerenciamento de sessao:** Cookies (secure, httponly, samesite), rotacao de session ID, fixacao de sessao
- **Bypass de autorizacao:** IDOR, escalacao de privilegios, acesso a funcionalidades admin
- **Analise de CORS:** Origens permitidas, Access-Control-Allow-Credentials
- **Cabecalhos de seguranca:** CSP, HSTS, X-Content-Type-Options, X-Frame-Options
- **Fingerprinting de tecnologia:** Servidores web, frameworks, bibliotecas, versoes

## Uso

```bash
myc agent add-plugin meu_agente web_auditor
```

## Especialistas Relacionados
- [OWASP Checker](owasp_checker.md) — Verificacao OWASP
- [Pentest Helper](pentest_helper.md) — Assistente de pentest
- [Data Quality](data_quality.md) — Auditoria de processos

## Parte do Department
**Seguranca**
- [web_auditor](web_auditor.md)
- [owasp_checker](owasp_checker.md)
- [pentest_helper](pentest_helper.md)
- [hardening_guide](hardening_guide.md)
