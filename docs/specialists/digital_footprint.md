# Especialista: Digital Footprint
**ID:** `digital_footprint`
**Department:** OSINT / Bug Bounty
**Arquivo:** `plugins/specialists/digital_footprint.py`

## Descricao

Especialista em mapeamento de presenca digital e identificacao de identidades online, conectando fragmentos de informacao dispersos pela internet.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_DIGITAL_FOOTPRINT=active`

### Contexto Injetado

- **Mapeamento multi-plataforma:** Redes sociais, foruns, blogs, plataformas de codigo, portfolios, jogos
- **Conexao de usernames a identidades:** Correlacao de usernames reutilizados, variacoes e padroes
- **Mapeamento de conexoes sociais:** Seguidores, interacoes frequentes, redes de contato, conexoes ocultas
- **Padroes de comportamento:** Horarios de publicacao, topicos recorrentes, estilo de escrita
- **Identificacao de exposicao em breaches:** Have I Been Pwned, DeHashed, avaliacao de risco
- **Analise de referencias em databases vazados:** Padroes de senhas reutilizadas, evolucao de dados pessoais

## Uso

```bash
myc agent add-plugin meu_agente digital_footprint
```

## Especialistas Relacionados
- [OSINT Collector](osint_collector.md) — Coleta de dados
- [Source Analyzer](source_analyzer.md) — Analise de credibilidade
- [Data Correlator](data_correlator.md) — Correlacao

## Parte do Department
**OSINT**
