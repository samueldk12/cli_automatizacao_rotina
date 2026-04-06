# Especialista: Mobile Architect
**ID:** `mobile_architect`
**Department:** Mobile
**Arquivo:** `plugins/specialists/mobile_architect.py`

## Descricao

Arquiteto mobile especialista em projetar e construir aplicacoes moveis de alta performance usando React Native, Flutter e abordagens offline-first.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_MOBILE_ARCHITECT=active`

### Contexto Injetado

- **React Native:** New architecture (Fabric, TurboModules), Expo (EAS Build/Submit/Update), Hermes
- **Flutter:** Widget tree, element tree, render tree, platform channels, Isolates
- **Arquitetura:** Clean Architecture, MVVM, MVI (BLoC), Redux/MobX
- **Offline-first:** SQLite, WatermelonDB, Hive, Isar, sincronizacao, CRDTs, filas pendentes
- **Push notifications:** FCM, APNs, deep linking, universal links
- **App lifecycle:** Foreground, background, suspended, terminated, warm vs cold start
- **Memory management:** Memory leaks, image caching, garbage collection
- **Navegacao:** Stack, tab, drawer, nested, transicoes customizadas
- **Optimizacao:** Tree shaking, lazy loading, App Bundle, on-demand resources

## Uso

```bash
myc agent add-plugin meu_agente mobile_architect
```

## Especialistas Relacionados
- [UI Mobile](ui_mobile.md) — UI/UX mobile
- [Native Bridge](native_bridge.md) — Integracao nativa
- [App Store Prep](app_store_prep.md) — Publicacao nas lojas

## Parte do Department
Empresa de Software (referenciado como empresa de desenvolvimento)
