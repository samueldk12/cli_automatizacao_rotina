# Especialista: Jurisprudencia
**ID:** `jurisprudencia`
**Department:** Direito Brasileiro
**Arquivo:** `plugins/specialists/jurisprudencia.py`

## Descricao

Analista de jurisprudencia brasileira com dominio dos entendimentos consolidados dos tribunais superiores (STF, STJ) e cortes regionais (TRFs, TJs).

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_JURISPRUDENCIA=1`

### Contexto Injetado

- **Tribunais superiores:** Competencia e papel do STF e do STJ
- **Sistema de precedentes vinculantes:** Sumulas vinculantes, IRDR, recursos repetitivos, repercussao geral
- **Metodologia de pesquisa:** Identificacao de temas, busca nos tribunais competentes, verificacao de teses vinculantes, analise do leading case
- **Jurisprudencia dos TRFs:** TRF1 a TRF6 com cobertura de regioes
- **Diretrizes de analise:** Citar numero do processo, relator, data, ementa; distinguir ratio decidendi; identificar distinguishing; nunca inventar numeros de processos

## Uso

```bash
myc agent add-plugin meu_agente jurisprudencia
```

## Especialistas Relacionados
- [Legislacao BR](legislacao_br.md) — Base legal
- [Peticoes](peticoes.md) — Aplicacao de jurisprudencia em pecas

## Parte do Department
**Direito Brasileiro**
