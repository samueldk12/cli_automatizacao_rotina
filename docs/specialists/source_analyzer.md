# Especialista: Source Analyzer
**ID:** `source_analyzer`
**Department:** OSINT
**Arquivo:** `plugins/specialists/source_analyzer.py`

## Descricao

Especialista em avaliacao de credibilidade e analise de fontes de inteligencia, identificando manipulacao e desinformacao.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_SOURCE_ANALYSIS=active`

### Contexto Injetado

- **Avaliacao de confiabilidade:** Historico da fonte, reputacao, padrao de precisao, transparencia metodologica
- **Cruzamento e validacao:** Triangulacao com multiplas fontes, corroboracao por canais distintos
- **Identificacao de desinformacao:** Deteccao de contas bot, astroturfing, redes coordenadas de influencia
- **Avaliacao de vies:** Inclinacao politica, interesses comerciais, afiliacoes organizacionais
- **Verificacao de timestamps:** Metadados temporais, conteudo reutilizado fora de contexto
- **Analise de metadados:** EXIF de imagens, metadados de documentos, geolocalizacao
- **Busca reversa de imagens:** Google Reverse Image, TinEye, Yandex, deteccao de deepfakes
- **Geolocalizacao por imagens:** Marcos geograficos, placas, posicao do sol, elementos sazonais

## Uso

```bash
myc agent add-plugin meu_agente source_analyzer
```

## Especialistas Relacionados
- [OSINT Collector](osint_collector.md) — Coleta de dados
- [Fact Checker](fact_checker.md) — Verificacao de fatos
- [Digital Footprint](digital_footprint.md) — Pegada digital

## Parte do Department
**OSINT**
