# Especialista: Bounty Report
**ID:** `bounty_report`
**Department:** Bug Bounty
**Arquivo:** `plugins/specialists/bounty_report.py`

## Descricao

Especialista em redacao de relatorios de vulnerabilidades para plataformas de bug bounty, transformando achados tecnicos em relatorios claros e persuasivos.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_BOUNTY_REPORT=active`

### Contexto Injetado

- **Estruturacao de relatorios:** Titulo descritivo, sumario executivo, secao tecnica, avaliacao de severidade
- **Sumarios executivos:** Impacto de negocio, contextualizacao, prioridade de correcao
- **Descricoes tecnicas:** Mecanismo da vulnerabilidade, diagramas, referencias (OWASP, CWE, CVE)
- **Declaracoes de impacto:** Dano potencial, cenario de ataque, quantificacao
- **Recomendacoes de remediacao:** Solucoes especificas, codigo de exemplo, mitigacao imediata vs correcao longo prazo
- **PoC para HackerOne/Bugcrowd:** Passos numerados, prerequisitos, output esperado, screenshots anotados
- **Evitacao de duplicatas:** Pesquisa previa, aspectos unicos, diferenciacao de achados similares
- **Comunicacao com triagers:** Tom profissional, respostas rapidas, disposicao colaborativa

## Uso

```bash
myc agent add-plugin meu_agente bounty_report
```

## Especialistas Relacionados
- [Vuln Triage](vuln_triage.md) — Triagem antes do reporte
- [Pentest Helper](pentest_helper.md) — Documentacao de pentest
- [Copywriter](copywriter.md) — Comunicacao clara

## Parte do Department
**Empresa de Bug Bounty** — Department de Documentacao
