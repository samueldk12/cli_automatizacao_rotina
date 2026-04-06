# Tower Defense Game

A complete 2D tower defense game built with Pygame.

## Prerequisites

- Python 3.8+
- pip

## Installation

```bash
pip install -r requirements.txt
```

## Running the Game

```bash
python game.py
```

## Controls

| Key | Action |
|-----|--------|
| 1 | Select Archer tower (50g) |
| 2 | Select Cannon tower (100g) |
| 3 | Select Mage tower (150g) |
| S | Deselect tower |
| U | Upgrade selected tower |
| SPACE | Start next wave |
| ESC | Quit |
| Left-click | Place tower / Select |
| Right-click | Deselect |

## Tower Types

- **Archer** (50g): Fast attack rate, single target damage. Good against fast/light enemies.
- **Cannon** (100g): High damage with splash effect. Good against groups.
- **Mage** (150g): Slows enemies with beam attack. Great support tower.

## Enemy Types

- **Normal** (Red): Standard speed and HP
- **Fast** (Yellow): Quick but fragile
- **Armored** (Gray): High HP and damage reduction
- **Boss** (Dark Red): Massive HP, very slow

## Game Features

- 10 progressively harder waves
- Currency system - earn gold by defeating enemies
- Tower upgrades (2 levels each)
- Wave completion bonuses
- Particle effects on enemy kills
- Score tracking
- Lives system (20 lives)

---
*Built by MYC Game Studio - 2025*
