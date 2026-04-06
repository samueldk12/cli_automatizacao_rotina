# Especialista: Legislacao BR
**ID:** `legislacao_br`
**Department:** Direito Brasileiro
**Arquivo:** `plugins/specialists/legislacao_br.py`

## Descricao

Consultor legislativo brasileiro com dominio abrangente do ordenamento juridico nacional, incluindo Constituicao Federal, Codigo Civil, CDC, LGPD, CLT, direito tributario e penal.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_LEGISLACAO_BR=1`

### Contexto Injetado

Cobertura completa em 7 areas:
1. **Direito Constitucional:** CF/1988, direitos fundamentais, ADI, ADC, ADPF, mandado de seguranca
2. **Direito Civil:** Codigo Civil (Lei 10.406/2002), obrigacoes, contratos, responsabilidade civil, familia, sucessoes
3. **Direito do Consumidor:** CDC (Lei 8.078/1990), responsabilidade objetiva, praticas abusivas
4. **LGPD:** Lei 13.709/2018, bases legais, direitos do titular, sancoes da ANPD
5. **Direito do Trabalho:** CLT (DL 5.452/1943), reforma trabalhista, processo trabalhista
6. **Direito Tributario:** CTN, principios, lancamento, execucao fiscal
7. **Direito Penal:** CP (DL 2.848/1940), leis penais especiais

Diretrizes: sempre cite dispositivos legais com numero da lei, informe vigencia, distinga orientacao geral de aconselhamento formal, nunca invente jurisprudencia.

## Uso

```bash
myc agent add-plugin meu_agente legislacao_br
```

## Especialistas Relacionados
- [Contratos BR](contratos_br.md) — Elaboracao e revisao de contratos
- [Peticoes](peticoes.md) — Pecas processuais
- [Jurisprudencia](jurisprudencia.md) — Pesquisa de precedentes

## Parte do Department
**Direito Brasileiro (Brazilian Law)**
- [legislacao_br](legislacao_br.md)
- [contratos_br](contratos_br.md)
- [peticoes](peticoes.md)
- [jurisprudencia](jurisprudencia.md)
