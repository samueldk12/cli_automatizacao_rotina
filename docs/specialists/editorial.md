# Especialista: Editorial
**ID:** `editorial`
**Department:** Jornalismo
**Arquivo:** `plugins/specialists/editorial.py`

## Descricao

Editor de conteudo jornalistico com experiencia em revisao, curadoria, adequacao a guias de estilo e analise de riscos legais em publicacoes.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_EDITORIAL=1`

### Contexto Injetado

- **Funcoes da edicao:** Texto, estilo, titulo/chamada, imagem/multimidia, secao
- **Manual de estilo:** Ortografia, numeros, datas, nomes proprios, cargos, siglas, citacoes, estrangeirismos, tratamento, horarios, monetario
- **Revisao de riscos legais:** Difamacao/calunia/injuria, direito a imagem e privacidade, segredo de justica, direito de resposta, direitos autorais, LGPD, propaganda subrepticia
- **Processo editorial:** Recepcao, primeira leitura, edicao de estrutura, edicao de conteudo, edicao de estilo, verificacao legal, titulo e chamada, selo de revisao
- **Feedback ao reporter:** Construtivo, objetivo, respeitoso

## Uso

```bash
myc agent add-plugin meu_agente editorial
```

## Especialistas Relacionados
- [Pauta Journal](pauta_journal.md) — Definicao de pautas
- [Redacao News](redacao_news.md) — Redacao de noticias
- [Fact Checker](fact_checker.md) — Verificacao de fatos

## Parte do Department
**Jornalismo**
