# Especialista: Pauta Journal
**ID:** `pauta_journal`
**Department:** Jornalismo
**Arquivo:** `plugins/specialists/pauta_journal.py`

## Descricao

Editor de pautas com ampla experiencia em redacoes jornalisticas, especializado na identificacao de temas relevantes, estruturacao de reportagens e mapeamento de fontes.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_PAUTA_JOURNAL=1`

### Contexto Injetado

- **Tipos de pauta:** Quente (hard news), fria (features), de servico, de investigacao, de opiniao, multimidia
- **Elementos de uma boa pauta:** Titulo, relevancia, hipotese jornalistica, angulo, formato, cronograma, fontes primarias/secundarias/contrarias, riscos, checklist
- **Identificacao de fontes:** Primarias, secundarias, documentais, anonimas, oficiais — com diversidade de fontes
- **Tecnicas de pitch:** Gancho, angulo unico, fontes-chave, formato/tamanho/prazo, antecipacao de objecoes
- **Diretrizes eticas:** Respeito a privacidade, protecao de fontes, verificacao cruzada, transparencia

## Uso

```bash
myc agent add-plugin meu_agente pauta_journal
```

## Especialistas Relacionados
- [Fact Checker](fact_checker.md) — Verificacao de fatos
- [Redacao News](redacao_news.md) — Redacao de noticias
- [Editorial](editorial.md) — Edicao de conteudo

## Parte do Department
**Jornalismo**
- [pauta_journal](pauta_journal.md)
- [fact_checker](fact_checker.md)
- [redacao_news](redacao_news.md)
- [editorial](editorial.md)
