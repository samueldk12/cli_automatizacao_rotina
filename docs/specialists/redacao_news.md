# Especialista: Redacao News
**ID:** `redacao_news`
**Department:** Jornalismo
**Arquivo:** `plugins/specialists/redacao_news.py`

## Descricao

Redator de noticias profissional com dominio das tecnicas de jornalismo objetivo, estilo AP e narracao informativa clara e precisa.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_REDACAO_NEWS=1`

### Contexto Injetado

- **Piramide Invertida:** Lead (5Ws+1H em 30-40 palavras), corpo (detalhes), background (contexto historico)
- **5Ws+1H:** Quem, O Que, Quando, Onde, Por Que, Como
- **Estilo AP:** Voz ativa, regras de numeros, citacoes, nomes, titulos, siglas, paragrafos curtos
- **Tipos de noticias:** Hard news, soft news, perfil, reportagem especial, noticia de servico, nota
- **Tecnicas de redacao:** Lead cenario, lead citacao, lead composto
- **Checklist de verificacao final:** 5Ws respondidos, fontes citadas, nomes/datas corretos, objetivos, titulo correspondente, ordem de importancia

## Uso

```bash
myc agent add-plugin meu_agente redacao_news
```

## Especialistas Relacionados
- [Pauta Journal](pauta_journal.md) — Definicao de pautas
- [Fact Checker](fact_checker.md) — Verificacao de fatos
- [Editorial](editorial.md) — Edicao de conteudo
- [Copywriter](copywriter.md) — Textos persuasivos

## Parte do Department
**Jornalismo**
