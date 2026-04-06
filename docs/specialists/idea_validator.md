# Especialista: Idea Validator
**ID:** `idea_validator`
**Department:** Innovacao e Ideacao / Game Design / Design Studio
**Arquivo:** `plugins/specialists/idea_validator.py`

## Descricao

Validador de ideias, especialista em transformar suposicoes em dados concretos usando metodologias lean — TAM/SAM/SOM, problem-solution fit, analise competitiva, risk assessment, entrevistas de validacao, escopo de MVP.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_IDEA_VALIDATOR=active`

### Contexto Injetado

- **TAM/SAM/SOM:** Dimensionamento de mercado (top-down e bottom-up)
- **Problem-Solution Fit:** Framework de Sean Ellis, metodo "The Mom Test", 20-30 entrevistas de validacao
- **Analise Competitiva:** Matrizes de posicionamento, SWOT, white spaces, reviews de concorrentes
- **Risk Assessment:** Matriz de riscos (mercado, tecnologia, operacoes, financas, competencia)
- **Validation Interview Guide:** Abertura, exploracao do problema, teste de disposicao a pagar, fechamento
- **MVP Scoping:** Build-Measure-Learn, MoSCoW, criterios de sucesso pre-definidos

## Uso

```bash
myc agent add-plugin meu_agente idea_validator
```

## Especialistas Relacionados
- [Brainstorm](brainstorm.md) — Geracao de ideias
- [MVP Builder](mvp_builder.md) — Construcao de MVP
- [Market Validator](market_validator.md) — Validacao de mercado

## Parte do Department
**Innovacao e Ideacao** — tambem usado em Game Design
