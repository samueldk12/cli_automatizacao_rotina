# Especialista: Business Model
**ID:** `business_model`
**Department:** Vendas / Innovacao
**Arquivo:** `plugins/specialists/business_model.py`

## Descricao

Estrategista de modelo de negocio — Business Model Canvas, value proposition design, unit economics (CAC, LTV, payback), revenue streams, cost structure, competitive moats.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_BUSINESS_MODEL=active`

### Contexto Injetado

- **Business Model Canvas:** Os 9 blocos de Osterwalder — segmentos de clientes, proposta de valor, canais, relacionamento, receitas, recursos, atividades, parceiros, estrutura de custos
- **Value Proposition Design:** Customer Profile (jobs, pains, gains) vs Value Map (produtos, pain relievers, gain creators); busca pelo product-market fit
- **Unit Economics:** CAC, LTV, payback period, margem de contribucao, benchmarks saudaveis (LTV:CAC > 3:1, payback < 12 meses)
- **Economic Moats:** Efeitos de rede, custos de troca, escala, ativos intangiveis, vantagem de dados

## Uso

```bash
myc agent add-plugin meu_agente business_model
```

## Especialistas Relacionados
- [Growth Hacker](growth_hacker.md) — Growth hacking
- [Sales Pitch](sales_pitch.md) — Pitch de vendas
- [Idea Validator](idea_validator.md) — Validacao de ideias

## Parte do Department
**Vendas** — tambem utilizado em Consultoria
