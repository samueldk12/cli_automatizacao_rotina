# Especialista: Data Correlator
**ID:** `data_correlator`
**Department:** OSINT / Marketing / Seguranca
**Arquivo:** `plugins/specialists/data_correlator.py`

## Descricao

Especialista em correlacao de dados e analise de conexoes para investigacoes de inteligencia, conectando pecas dispersas para gerar insights.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_DATA_CORRELATION=active`

### Contexto Injetado

- **Conexao de informacoes dispares:** Pontos de ligacao por IPs, e-mails, telefones, nomes, datas
- **Reconstrucao de linhas do tempo:** Organizacao cronologica, deteccao de lacunas, relacoes causa-efeito
- **Mapeamento de relacionamento:** Grafos de conexoes entre pessoas, organizacoes, dominios, infraestrutura
- **Conceitos de analise de grafos:** Centralidade, intermedizacao, proximidade, deteccao de comunidades
- **Reconhecimento de padroes:** Comportamentos padronizados, anomalias, correlacao entre plataformas
- **Geracao de relatorios:** Estruturacao clara, cadeias de raciocinio, avaliacao de confianca, fatos vs inferencias
- **Identificacao de lacunas:** Areas com informacao insuficiente, hipoteses, recomendacoes

## Uso

```bash
myc agent add-plugin meu_agente data_correlator
```

## Especialistas Relacionados
- [OSINT Collector](osint_collector.md) — Coleta de dados
- [Pipeline Designer](pipeline_designer.md) — Design de pipelines
- [Source Analyzer](source_analyzer.md) — Analise de fontes

## Parte do Department
**OSINT**