# Especialista: Pipeline Designer
**ID:** `pipeline_designer`
**Department:** Engenharia de Dados / Vendas
**Arquivo:** `plugins/specialists/pipeline_designer.py`

## Descricao

Arquiteto de pipelines de dados — batch vs streaming, Apache Spark, Delta Lake, orquestracao e data lake architecture.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_PIPELINE_DESIGNER=active`

### Contexto Injetado

- **Batch vs Streaming:** Batch diario/semanal, micro-batch, streaming puro (Flink, Kafka Streams), watermarks, exactly-once semantics
- **Spark optimization:** DataFrame API, Catalyst optimizer, broadcast joins, salting, partition pruning, AQE
- **Formatos de tabela open-source:** Delta Lake, Apache Iceberg, Apache Hudi — criterios de selecao
- **Data Lake Architecture:** Medallion architecture (bronze, silver, gold), metadata catalog, zoneamento
- **Orquestracao:** Apache Airflow, Dagster, Prefect — selecao baseada em complexidade
- **Contratos de dados:** Schema esperado, tipos, constraints, data product ownership, SLAs
- **Evolucao de schema:** Safe operations, periodo de transicao, versionamento, schema registry
- **Monitoramento:** Tracking de execucao, alertas, lineage de dados (Apache Atlas, OpenLineage)
- **Otimizacao de custos:** Right-sizing, spot instances, auto-scaling, storage lifecycle

## Uso

```bash
myc agent add-plugin meu_agente pipeline_designer
```

## Especialistas Relacionados
- [ETL Builder](etl_builder.md) — Pipelines ETL
- [Data Quality](data_quality.md) — Qualidade
- [Warehouse Architect](warehouse_architect.md) — Warehouse

## Parte do Department
**Engenharia de Dados** — tambem utilizado em Vendas
