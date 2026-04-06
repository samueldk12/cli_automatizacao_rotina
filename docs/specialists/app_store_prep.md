# Especialista: App Store Prep
**ID:** `app_store_prep`
**Department:** Mobile
**Arquivo:** `plugins/specialists/app_store_prep.py`

## Descricao

Especialista em preparacao para lojas de apps — icones, metadata, screenshots, politicas de privacidade, revisao e distribuicao beta.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_APP_STORE_PREP=active`

### Contexto Injetado

- **Icones:** Resolucoes obrigatorias iOS (1024x1024, 180x180, etc.) e Android (512x512, 192x192, etc.), adaptive icons (Android), arredondados (iOS)
- **Splash screens:** iOS Storyboard, SplashScreen API Android 12+
- **Metadata ASO:** Titulo, descricao, keywords, categoria, localizacao
- **Screenshots:** 6.7", 5.5", 12.9" iPad, storytelling visual sequencial
- **Privacidade e conformidade:** GDPR, LGPD, CCPA, ATT framework do iOS
- **In-app purchase:** App Store Connect, Google Play Console, tipos de produto, validacao server-side
- **Diretrizes de revisao:** Apple Review Guidelines, Google Play Policy, motivos comuns de rejeicao
- **Distribuicao beta:** TestFlight, Google Play testing tracks, Firebase App Distribution

## Uso

```bash
myc agent add-plugin meu_agente app_store_prep
```

## Especialistas Relacionados
- [Mobile Architect](mobile_architect.md) — Arquitetura mobile
- [Native Bridge](native_bridge.md) — Integracao nativa
- [UI Mobile](ui_mobile.md) — Design mobile

## Parte do Department
Mobile
