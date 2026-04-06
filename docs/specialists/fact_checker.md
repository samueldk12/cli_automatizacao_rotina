# Especialista: Fact Checker
**ID:** `fact_checker`
**Department:** Jornalismo / OSINT
**Arquivo:** `plugins/specialists/fact_checker.py`

## Descricao

Verificador de fatos profissional com expertise em verificacao de informacoes, deteccao de desinformacao e analise de credibilidade de fontes.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_FACT_CHECKER=1`

### Contexto Injetado

- **Principios da checagem:** Verificabilidade, transparencia, neutralidade, proporcionalidade, justica
- **Metodologia:** Identificacao da claim, categorizacao, busca de evidencia primaria, avaliacao de fontes, cruzamento, verificacao de contexto, classificacao final
- **Classificacoes:** Verdadeiro, Verdadeiro Sem Contexto, Em Analise, Falso, Enganoso, Exagerado, Impossivel de Verificar
- **Deteccao de desinformacao:** Fake news, conteudo manipulado, forjado, impostor, fabricado, falsa conexao, contexto falso, satira/parodia
- **Tecnicas de verificacao:** Reverse image search, video verification, metadados, geolocalizacao, verificacao temporal, dados e estatisticas
- **Ferramentas:** Agencia Lupa, Aos Fatos, Snopes, Politifact, InVID, FotoForensics, Archive.org

## Uso

```bash
myc agent add-plugin meu_agente fact_checker
```

## Especialistas Relacionados
- [OSINT Collector](osint_collector.md) — Coleta de inteligencia
- [Source Analyzer](source_analyzer.md) — Analise de fontes
- [Digital Footprint](digital_footprint.md) — Pegada digital

## Parte do Department
**Jornalismo**