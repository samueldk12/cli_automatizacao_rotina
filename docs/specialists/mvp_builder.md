# Especialista: MVP Builder
**ID:** `mvp_builder`
**Department:** Innovacao e Ideacao
**Arquivo:** `plugins/specialists/mvp_builder.py`

## Descricao

Construtor de MVP, especialista em transformar ideias de produto em versoes minimas testaveis no menor tempo e custo possivel.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_MVP_BUILDER=active`

### Contexto Injetado

- **Priorizacao MoSCoW:** Must have, Should have, Could have, Won't have
- **Rapid Prototyping:** Paper prototypes, wireframes (Balsamiq), prototipos clicaveis (Figma, InVision), video prototypes
- **Ferramentas No-Code/Low-Code:** Bubble, Webflow, Glide, Softr, Zapier, Make, FlutterFlow, Xano, Airtable, Notion, Carrd, Framer, Adalo
- **Landing Page Validation:** Copy persuasivo, metricas alvo (CTR >5%, conversao >20%, tempo >1.5min), heatmaps (Hotjar)
- **Concierge MVP:** Servico manual entregando valor antes de automatizar
- **Wizard of Oz Testing:** Interface que parece funcional mas humanos executam por tras
- **Roadmap Pos-MVP:** Iteracoes baseadas em feedback, pivot vs perseverar

## Uso

```bash
myc agent add-plugin meu_agente mvp_builder
```

## Especialistas Relacionados
- [Idea Validator](idea_validator.md) — Validacao de ideias
- [Design Thinking](design_thinking.md) — Design Thinking
- [Frontend Dev](frontend_dev.md) — Implementacao frontend

## Parte do Department
**Innovacao e Ideacao**
