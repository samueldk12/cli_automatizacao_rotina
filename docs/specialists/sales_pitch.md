# Especialista: Sales Pitch
**ID:** `sales_pitch`
**Department:** Vendas
**Arquivo:** `plugins/specialists/sales_pitch.py`

## Descricao

Especialista em pitch de vendas — Elevator pitch, scripts de demonstracao, tratamento de objecoes, SPIN selling, storytelling para vendas.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_SALES_PITCH=active`

### Contexto Injetado

- **Elevator Pitch (30-60s):** Gancho (5s), Problema, Solucao, Prova, Call to Action
- **SPIN Selling (Neil Rackham):** Situation (contexto minimo), Problem (insatisfacoes), Implication (consequencias amplificadas), Need-Payoff (cliente articula valor)
- **Storytelling para Vendas:** 5 atos (Contexto, Conflito, Busca, Resolucao, Resultado com metricas), tecnica PAS (Problem-Agitate-Solve)
- **Objection Handling:** Framework LAER (Listen, Acknowledge, Explore, Respond) e Feel-Felt-Found; objecoes comuns: preco, timing, confianca, autoridade, necessidade
- **Demo Scripts:** 70% ouvindo, 30% falando; dados customizados com contexto do prospect; estrutura: problema -> jornada -> "aha moments" -> impacto de negocio

## Uso

```bash
myc agent add-plugin meu_agente sales_pitch
```

## Especialistas Relacionados
- [Sales Funnel](sales_funnel.md) — Funil de vendas
- [Business Model](business_model.md) — Modelo de negocio
- [Brainstorm](brainstorm.md) — Geracao de ideias para pitches

## Parte do Department
**Vendas**
