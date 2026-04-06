# Space Shooter — game_studio_company Output

Jogo completo de Space Shooter em pygame gerado pelo plugin **game_studio_company** do MYC.

## Como os 4 sub-agentes contribuíram

| Sub-agente | Papel |
|-----------|-------|
| level_designer_lead | Progressão de níveis infinitos com dificuldade crescente, boss fights |
| narrative_designer | Tema de guerra espacial, lore dos inimigos |
| mechanic_designer | 3 níveis de weapon upgrade, sistema de shield, invincibilidade, padrões de inimigo |
| game_ux_designer | Partículas, HUD, tela de título/pause/game over |

## Como rodar

```bash
cd projects/game_pygame
pip install pygame
python game.py
```

## Controles

| Tecla | Ação |
|-------|------|
| Setas / WASD | Mover nave |
| Espaço | Atirar |
| P | Pause |
| ENTER | Iniciar / Reiniciar |
| ESC | Sair |

## Inimigos

| Tipo | HP | Comportamento |
|------|----|---------------|
| Scout | 1 | Rápido, senoidal |
| Drone | 2 | Atira periodicamente |
| Cruiser | 5+ | Lento, blindado |
| Boss | 50+ | Spread + tiros direcionados |

---

*Plugin: myc agent-company game_studio_company — [repo](https://github.com/samueldk12/cli_automatizacao_rotina)*
