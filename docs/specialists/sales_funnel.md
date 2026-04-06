# Especialista: Sales Funnel
**ID:** `sales_funnel`
**Department:** Vendas
**Arquivo:** `plugins/specialists/sales_funnel.py`

## Descricao

Arquiteto de funil de vendas, especialista em jornadas de conversao TOFU/MOFU/BOFU, lead scoring, CRO, email nurturing, retargeting.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_SALES_FUNNEL=active`

### Contexto Injetado

- **TOFU (Atracao):** SEO informacional, iscas digitais (ebooks, templates, calculadoras), metricas: trafego, CTR, taxa de captura (2-5% baseline)
- **MOFU (Consideracao):** Comparativos, cases, webinars, trials, lead scoring quantitativo (pontos por comportamento e demographics), threshold MQL
- **BOFU (Decisao):** Trials guiados, demos personalizadas, propostas com ROI, ofertas de urgencia, garantias
- **Email Nurturing:** Sequencia de boas-vindas 5 emails/14 dias, nutricao continua semanal, segmentacao por estagio
- **Retargeting Strategy:** Google Ads, Meta Ads, segmentos estrategicos (precos, abandono, conteudo), frequencia ideal 3-5/semana
- **CRO:** A/B testing (uma variavel, 95% significancia), heatmaps, session recordings, reducao de friccao, velocidade de pagina

## Uso

```bash
myc agent add-plugin meu_agente sales_funnel
```

## Especialistas Relacionados
- [Sales Pitch](sales_pitch.md) — Pitch de vendas
- [Growth Hacker](growth_hacker.md) — Growth hacking
- [Pipeline Designer](pipeline_designer.md) — Design de pipelines

## Parte do Department
**Vendas**
