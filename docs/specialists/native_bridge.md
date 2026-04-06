# Especialista: Native Bridge
**ID:** `native_bridge`
**Department:** Mobile
**Arquivo:** `plugins/specialists/native_bridge.py`

## Descricao

Especialista em integracao nativa mobile — modulos nativos para React Native, platform channels em Flutter, sensores e biometria.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_NATIVE_BRIDGE=active`

### Contexto Injetado

- **React Native Native Modules:** Kotlin (Android), Swift/Obj-C (iOS), TurboModules, callbacks async, promises, DeviceEventEmitter, Native UI Components
- **Flutter Platform Channels:** MethodChannel, EventChannel, BasicMessageChannel, StandardMessageCodec
- **Hardware nativo:** Camera (CameraX/AVFoundation), GPS, sensores (acelerometro, giroscopio), NFC, BLE
- **Biometria:** Face ID/Touch ID (LocalAuthentication framework), BiometricPrompt (Android)
- **Background tasks:** BGTaskScheduler (iOS), WorkManager (Android), geofencing
- **Performance nativa:** Grand Central Dispatch (iOS), Coroutines (Android), prevencao de ANRs
- **Linking de bibliotecas:** CocoaPods, SPM (iOS), Gradle (Android), autolinking

## Uso

```bash
myc agent add-plugin meu_agente native_bridge
```

## Especialistas Relacionados
- [Mobile Architect](mobile_architect.md) — Arquitetura mobile
- [UI Mobile](ui_mobile.md) — UI mobile
- [App Store Prep](app_store_prep.md) — Publicacao

## Parte do Department
Mobile
