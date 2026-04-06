# Especialista: ETL Builder
**ID:** `etl_builder`
**Department:** Engenharia de Dados
**Arquivo:** `plugins/specialists/etl_builder.py`

## Descricao

Engenheiro de pipeline ETL, especialista em projetar e implementar pipelines robustos de extracao, transformacao e carga de dados.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_ETL_BUILDER=active`

### Contexto Injetado

- **Extracao:** APIs REST com paginacao, webhooks, CDC com Debezium, arquivos (CSV, JSON, Parquet), web scraping
- **Transformacao:** Limpeza, parsing de datas, normalizacao, agregacoes, joins, UDFs, validacao de schema
- **Carga:** Upssert, CDC, bulk insert, particionamento, incremental vs full refresh
- **Tratamento de erros:** Retry com exponential backoff, circuit breaker, dead letter queues, alertas
- **Idempotencia:** Execucoes reentrantes, chaves naturais, watermark tracking, transacoes atomicas
- **Apache Airflow DAGs:** Operadores, sensores, XComs, branching, retry, SLAs, backfill
- **Modelos dbt:** SQL + Jinja, testes integrados, macros, exposures, docs
- **Processamento incremental:** Timestamp de atualizacao, hash de conteudo, window-based, checkpoint state

## Uso

```bash
myc agent add-plugin meu_agente etl_builder
```

## Especialistas Relacionados
- [Pipeline Designer](pipeline_designer.md) — Pipelines de dados
- [Data Quality](data_quality.md) — Qualidade de dados
- [Warehouse Architect](warehouse_architect.md) — Data warehouse

## Parte do Department
**Engenharia de Dados**
