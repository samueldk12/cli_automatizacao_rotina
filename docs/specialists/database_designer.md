# Especialista: Database Designer
**ID:** `database_designer`
**Department:** Backend Development
**Arquivo:** `plugins/specialists/database_designer.py`

## Descricao

Arquiteto de banco de dados especialista em modelagem, otimizacao e administracao de sistemas de dados relacionais e NoSQL.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_DATABASE_DESIGNER=active`

### Contexto Injetado

- **Schema relacional:** Normalizacao (1FN ate BCNF), desnormalizacao estrategica, modelagem ER
- **Indexacao:** B-tree, hash, GIN, GiST, BRIN, cobertura parcial, multi-coluna
- **Otimizacao de queries:** EXPLAIN ANALYZE, eliminacao de full table scans, N+1 prevention
- **Bancos relacionais:** PostgreSQL (JSONB, PostGIS), MySQL/MariaDB
- **Bancos NoSQL:** MongoDB, Redis, DynamoDB (single-table design)
- **Migracoes:** Flyway, Alembic, Prisma Migrate, zero-downtime migrations
- **Connection pooling:** PgBouncer, connection multiplexing
- **Backup e recovery:** Full, incremental, differential, PITR
- **Replicacao:** Master-slave, master-master, read replicas, failover

## Uso

```bash
myc agent add-plugin meu_agente database_designer
```

## Especialistas Relacionados
- [Backend Dev](backend_dev.md) — Desenvolvimento backend
- [Warehouse Architect](warehouse_architect.md) — Data warehouse
- [DevOps Deploy](devops_deploy.md) — Infraestrutura

## Parte do Department
**Backend Development**
