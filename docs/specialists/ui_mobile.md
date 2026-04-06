# Especialista: UI Mobile
**ID:** `ui_mobile`
**Department:** Mobile / Frontend Development / Game Design
**Arquivo:** `plugins/specialists/ui_mobile.py`

## Descricao

UI/UX Designer mobile especialista em Material Design 3, Human Interface Guidelines, layouts responsivos, gestos, animacoes e acessibilidade.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_UI_MOBILE=active`

### Contexto Injetado

- **Diretrizes por plataforma:** Material Design 3 (Android), Human Interface Guidelines (iOS)
- **Layouts responsivos:** Smartphones, tablets, foldables, different aspect ratios
- **Gestos:** Swipe, pinch-to-zoom, long press, drag and drop, pull-to-refresh, haptics
- **Animacao:** Duracao 200-300ms, spring physics, 60/120fps, hero transitions
- **Acessibilidade:** VoiceOver, TalkBack, toque minimo 44x44pt/dp, contraste WCAG 2.2 AA, dark mode
- **Dark mode:** Tokens de cores, adaptacao de imagens, transicoes suaves
- **Design system:** Componentes consistentes, tokens reutilizaveis
- **Micro-interacoes:** Loading states, skeleton screens, empty states, error states, success confirmations

## Uso

```bash
myc agent add-plugin meu_agente ui_mobile
```

## Especialistas Relacionados
- [Mobile Architect](mobile_architect.md) — Arquitetura mobile
- [Frontend Dev](frontend_dev.md) — Frontend web
- [Game UX](game_ux.md) — UX de jogos

## Parte do Department
**Frontend Development** — tambem utilizado em Game Design
