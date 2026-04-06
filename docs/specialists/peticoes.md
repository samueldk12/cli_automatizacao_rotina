# Especialista: Peticoes
**ID:** `peticoes`
**Department:** Direito Brasileiro
**Arquivo:** `plugins/specialists/peticoes.py`

## Descricao

Redator de peticoes judiciais brasileiras seguindo o CPC 2015 e normas processuais vigentes.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_PETICOES=1`

### Contexto Injetado

- **Estrutura da peticao inicial (art. 319 CPC):** Enderecamento, qualificacao, fatos, fundamentos juridicos, pedidos, valor da causa
- **Tutela provisoria (arts. 294-311):** Urgencia (fumus boni iuris + periculum in mora) e evidencia (art. 311)
- **Recursos:** Apelacao, agravo de instrumento, embargos de declaracao, REsp e RE — prazos e estrutura
- **Peticoes diversas:** Contestacao, reconvencao, cumprimento de sentenca, habilitacao
- **Diretrizes de redacao:** Linguagem formal mas acessivel, jurisprudencia do tribunal competente, formatacao adequada, tempestividade

## Uso

```bash
myc agent add-plugin meu_agente peticoes
```

## Especialistas Relacionados
- [Legislacao BR](legislacao_br.md) — Base legal
- [Jurisprudencia](jurisprudencia.md) — Precedentes para embasar peticoes

## Parte do Department
**Direito Brasileiro**
