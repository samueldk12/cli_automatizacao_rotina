# Especialista: Design Thinking
**ID:** `design_thinking`
**Department:** Innovacao e Ideacao / Design Studio
**Arquivo:** `plugins/specialists/design_thinking.py`

## Descricao

Especialista em Design Thinking — Empathize-Define-Ideate-Prototype-Test, journey maps, empathy maps, user personas, assumption mapping, rapid prototyping.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_DESIGN_THINKING=active`

### Contexto Injetado

- **5 Fases:** Empathize (entrevistas, observacao, shadowing), Define (affinity mapping, personas, problem statements), Ideate (brainstorm, crazy 8s, "how might we"), Prototype (baixa/media/alta fidelidade), Test (thinking aloud, iteracao)
- **User Journey Maps:** Fases, acoes, pensamentos, emocoes, pontos de contato, momentos de verdade
- **Empathy Maps:** Diz, pensa, faz, sente — discrepancias e motivacoes
- **Personas:** Baseadas em dados reais com demografia, comportamentos, objetivos, frustracoes
- **Assumption Mapping:** Lista e prioriza suposicoes por importancia e incerteza
- **Rapid Prototyping:** Figma, Miro, papel e caneta, service blueprints

## Uso

```bash
myc agent add-plugin meu_agente design_thinking
```

## Especialistas Relacionados
- [Brainstorm](brainstorm.md) — Geracao de ideias
- [Idea Validator](idea_validator.md) — Validacao de ideias
- [MVP Builder](mvp_builder.md) — Construcao de MVP
- [Didatica](didatica.md) — Metodologias de ensino

## Parte do Department
**Innovacao e Ideacao** — tambem usado em Design Studio
