# Especialista: Contratos BR
**ID:** `contratos_br`
**Department:** Direito Brasileiro
**Arquivo:** `plugins/specialists/contratos_br.py`

## Descricao

Analista de contratos brasileiro, especialista na elaboracao, revisao e analise de instrumentos contratuais sob a legislacao brasileira.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_CONTRATOS_BR=1`

### Contexto Injetado

- **Referencias legais:** Codigo Civil arts. 421-480, CDC, Lei de Locacoes, LGPD, Marco Civil da Internet
- **Tipos de contratos:** Empresariais, de consumo, trabalhistas, imobiliarios, digitais, terceiro setor
- **Analise de riscos:** Validade formal e material, clausulas de responsabilidade, forca maior, penalidades, arbitragem, confidencialidade, propriedade intelectual, LGPD
- **Diretrizes de redacao:** Linguagem clara, definicoes, numeracao logica, elementos obrigatorios (partes, objeto, valor, prazo, rescisao, foro)

## Uso

```bash
myc agent add-plugin meu_agente contratos_br
```

## Especialistas Relacionados
- [Legislacao BR](legislacao_br.md) — Base legal dos contratos
- [Peticoes](peticoes.md) — Pecas judiciais

## Parte do Department
**Direito Brasileiro**
