# Especialista: OWASP Checker
**ID:** `owasp_checker`
**Department:** Seguranca
**Arquivo:** `plugins/specialists/owasp_checker.py`

## Descricao

Especialista no OWASP Top 10 2021, dominando mecanismos de exploracao, tecnicas de deteccao e estrategias de remediacao para cada categoria.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_OWASP_CHECK=active`

### Contexto Injetado

O OWASP Top 10 2021 coberto em detalhe:
1. **A01 Broken Access Control:** IDOR, bypass de controles, escalacao de privilegios
2. **A02 Cryptographic Failures:** Algoritmos fracos (MD5, SHA1, DES), chaves hardcoded, TLS
3. **A03 Injection:** SQLi, command injection, XXE, SSTI, deserialization
4. **A04 Insecure Design:** Falhas arquiteturais, ausencia de threat modeling
5. **A05 Security Misconfiguration:** Configuracao padrao, headers ausentes, servicos expostos
6. **A06 Vulnerable and Outdated Components:** CVEs conhecidos, dependencias transitivas
7. **A07 Identification and Authentication Failures:** Credential stuffing, brute force, JWT
8. **A08 Software and Data Integrity Failures:** CI/CD comprometido, desserializacao, SSRF
9. **A09 Security Logging and Monitoring Failures:** Ausencia de logs, deteccao tardia
10. **A10 Server-Side Request Forgery:** SSRF basico e blind, bypass de filtros, metadados cloud

## Uso

```bash
myc agent add-plugin meu_agente owasp_checker
```

## Especialistas Relacionados
- [Web Auditor](web_auditor.md) — Auditoria web
- [Pentest Helper](pentest_helper.md) — Pentest
- [Hardening Guide](hardening_guide.md) — Hardening

## Parte do Department
**Seguranca**
