# Especialista: Vuln Triage
**ID:** `vuln_triage`
**Department:** Bug Bounty / Seguranca / DevOps
**Arquivo:** `plugins/specialists/vuln_triage.py`

## Descricao

Especialista em triagem e validacao de vulnerabilidades, confirmando achados, avaliando impacto real e eliminando falsos positivos.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_VULN_TRIAGE=active`

### Contexto Injetado

- **Confirmacao de achados:** Reproducao independente, consistencia, documentacao de validacao
- **Avaliacao de impacto real:** Diferenciacao teorica vs explotavel, pre-requisitos realistas, barreiras existentes
- **Encadeamento de vulnerabilidades:** Construcao de cadeias de exploracao, impacto cumulativo
- **Identificacao de falsos positivos:** Comportamento esperado vs vulnerabilidade, ruído de scanners
- **Verificacao de escopo:** In-scope vs out-of-scope vs wildcard, politicas do programa
- **Deteccao de duplicatas:** Relatorios publicos, patches recentes, CVEs similares
- **Vulnerabilidades de logica de negocio:** Inconsistencias cliente-servidor, bypass de limitacoes
- **Escalacao de privilegios:** Horizontal, vertical, JWT manipulation
- **Rate limiting:** Bypass via rotacao IP, manipulacao de headers

## Uso

```bash
myc agent add-plugin meu_agente vuln_triage
```

## Especialistas Relacionados
- [Bounty Report](bounty_report.md) — Reporte de bugs validados
- [Pentest Helper](pentest_helper.md) — Metodologia de pentest
- [Hardening Guide](hardening_guide.md) — Correcao de vulnerabilidades

## Parte do Department
**Empresa de Bug Bounty** — Documentacao; tambem usado em DevOps (security ops) e Seguranca (incident responder)
