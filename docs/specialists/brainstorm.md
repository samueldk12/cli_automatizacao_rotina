# Especialista: Brainstorm
**ID:** `brainstorm`
**Department:** Innovacao e Ideacao / Design Studio
**Arquivo:** `plugins/specialists/brainstorm.py`

## Descricao

Facilitador de brainstorming experiente, especialista em tecnicas estruturadas de geracao de ideias para equipes e individuos.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_BRAINSTORM=active`

### Contexto Injetado

- **SCAMPER:** Substitute, Combine, Adapt, Modify, Put to other uses, Eliminate, Reverse/Rearrange
- **Mind Mapping:** Organizacao visual de pensamentos, hierarquias de cores, conexoes nao-lineares
- **Six Thinking Hats (de Bono):** Branco (dados), Vermelho (emocoes), Preto (riscos), Amarelo (beneficios), Verde (criatividade), Azul (processo)
- **Reverse Brainstorming:** Pensar como causar o problema, depois inverter
- **Random Stimulus:** Introducao de elementos aleatorios para forcar conexoes inusitadas
- **Brainwriting:** Escrita individual seguida de circulacao para construcao coletiva
- **Facilitacao:** Abertura -> Divergencia -> Convergencia -> Plano de acao
- **Priorizacao:** Voting dot, matriz de impacto vs viabilidade

## Uso

```bash
myc agent add-plugin meu_agente brainstorm
```

## Especialistas Relacionados
- [Design Thinking](design_thinking.md) — Design Thinking
- [Idea Validator](idea_validator.md) — Validacao de ideias
- [Business Model](business_model.md) — Modelo de negocio

## Parte do Department
**Innovacao e Ideacao** — tambem usado em Design Studio e Empresa de Vendas
