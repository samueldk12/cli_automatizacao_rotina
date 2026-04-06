# Game Design Document

## Siege of the Crystal Keep

**Version:** 1.0
**Date:** 2025-01-15
**Studio:** MYC Game Studio
**Target Platform:** PC (Steam)
**Engine:** Python/Pygame (prototype) -> Godot 4 (production)
**Genre:** Tower Defense
**Target Rating:** Everyone 10+

---

## 1. Game Concept

**Elevator Pitch:** A visually striking 2D tower defense game where the battlefield itself evolves. Defend your Crystal Keep against waves of increasingly dangerous enemies by strategically placing towers on a dynamic map that changes with each wave.

**Core Fantasy:** The strategist commander who must adapt their defenses as the battlefield itself shifts and transforms.

**Target Audience:**
- Fans of Kingdom Rush, Bloons TD 6, and GemCraft
- Casual to mid-core players seeking strategic depth
- Players who enjoy pixel art and polished 2D aesthetics
- Ages 12+, all genders, global audience

---

## 2. Core Mechanics

### 2.1 Tower System

| Tower Type | Role | Cost | Damage Profile | Special |
|------------|------|------|----------------|---------|
| **Archer** | DPS | 50g | Fast single-target | Critical hits (10% for 3x damage) |
| **Cannon** | AoE | 100g | Slow splash damage | Area denial, terrain destruction |
| **Mage** | Support | 150g | Continuous slow beam | Freezes enemies briefly |
| **Fire Mage** | DPS/AoE | 200g | Medium burn damage | Damage over time effect |
| **Sniper** | Burst | 175g | Very slow, massive single hit | Ignores armor |

**Upgrade System:**
- Each tower has 3 levels
- Upgrade cost = 1.5x base cost per level
- Max level towers glow with special effects
- Towers can be sold for 70% of invested gold

### 2.2 Enemy Types

| Enemy | HP | Speed | Special | Wave Introduced |
|-------|----|-------|---------|----------------|
| Goblin Scout | 30 | Fast | None | 1 |
| Orc Grunt | 80 | Normal | Small armor | 2 |
| Wolf Pack | 25 | Very Fast | Spawns in groups of 3 | 3 |
| Troll | 200 | Slow | Regenerates HP | 4 |
| Siege Golem | 500 | Very Slow | Destroys nearby towers | 7 |
| Shadow Assassin | 40 | Fast | Invisible to 2 types of towers | 5 |
| Dragon | 1000 | Medium | Flies over some terrain | 8 |
| Crystal Sentinel | 400 | Slow | Reflects 50% damage | 9 |
| Final Boss | 5000 | Very Slow | Phase changes | 10 |

### 2.3 Wave System

- **10 main waves** in the campaign
- Between waves: 30-second preparation phase
- Wave completion bonus: 25 + (wave_number * 10) gold
- **Dynamic map:** After each wave, the terrain changes:
  - Rivers may appear (creating new paths)
  - Forests may grow (blocking tower placement areas)
  - Crystal deposits appear (bonus gold sources)
- **Endless mode** unlocked after campaign completion

### 2.4 Economy

| Source | Gold |
|--------|------|
| Enemy kill (basic) | 10-25 |
| Boss kill | 100+ |
| Wave bonus | 25-125 |
| Crystal deposit (per wave) | 50-100 |
| Achievements | 50-200 |

Starting gold: 200
Lives: 20

---

## 3. Art Direction

### 3.1 Visual Style
- **Art Style:** Hand-drawn pixel art with modern lighting
- **Resolution:** 1024x718 game area, 1024x720 total
- **Color Palette:** Rich, saturated colors with clear team distinction
- **Animation:** 4-directional character sprites, 8-12 frame walking cycles

### 3.2 UI/UX
- Clean, modern interface inspired by mobile TD games
- Dark theme for panels (reduces eye strain during long sessions)
- Color-coded information at a glance (green = good, red = danger, gold = economy)
- Tooltips for all game elements
- Sound on/off and music volume controls

### 3.3 VFX
- Particle effects for kills (burst, scatter)
- Tower projectile trails with distinct visual signatures
- Screen shake on cannon explosions
- Glow effects for upgraded towers
- Health bars always visible above enemies

---

## 4. Level Design

### World Map: Crystal Keep Campaign

The game features a single, evolving battlefield that the player must defend:

1. **Plains of Beginning** (Waves 1-3): Open, flat terrain. Good for learning.
2. **Misty Forest** (Waves 4-6): Trees appear, creating choke points.
3. **Crystal Caverns** (Waves 7-8): Underground section with branching paths.
4. **The Keep** (Waves 9-10): Final stand with complex multi-path assault.

Each wave modifies the map, requiring players to adapt their strategy rather than relying on a static defense.

---

## 5. Progression System

### Campaign
- 10 waves with increasing difficulty
- 3-star rating per wave:
  - 1 star: Complete the wave
  - 2 stars: Complete with 10+ lives remaining
  - 3 stars: Complete with 15+ lives AND under par time

### Unlocks
- New tower types become available as campaign progresses
- Endless mode after 3-star completion
- Challenge maps (limited towers, bonus enemies, speed runs)

### Achievements (12 total)
- First Victory
- Perfect Wave (no enemies leak)
- Rich Commander (accumulate 1000 gold)
- Max All Towers
- Speed Runner (complete in under 15 min)
- Flawless Victory (3-star all waves)
- And 6 more...

---

## 6. Audio Design

| Audio Element | Description |
|---------------|-------------|
| Background Music | Orchestral fantasy, dynamic intensity |
| SFX: Tower Shots | Distinct per tower type |
| SFX: Enemy Death | Satisfying pop/crumble effects |
| SFX: UI | Clean, subtle clicks |
| SFX: Wave Start | Fanfare / drum roll |
| SFX: Game Over | Melancholic melody |
| SFX: Victory | Triumphant brass theme |

---

## 7. UI Screens

### 7.1 Main Menu
- New Game
- Continue
- Endless Mode
- Settings
- Credits

### 7.2 Game Screen
```
[Top Bar: Wave | Gold | Lives | Score]
[Game Area: 820px wide] | [Right Panel: Build Menu]
```

### 7.3 Game Over / Victory
- Statistics summary
- Retry / Main Menu buttons
- Achievement notifications

---

## 8. Technical Specifications

### Engine & Tools
- **Prototype:** Python 3.8+ with Pygame 2.0+
- **Production:** Godot 4.x
- **Art:** Aseprite / pixel art pipeline
- **Audio:** FMOD or Godot Audio

### System Requirements (Minimum)
- OS: Windows 7 / macOS 10.13 / Ubuntu 18.04
- Processor: 1.5 GHz Dual Core
- Memory: 2 GB RAM
- Graphics: OpenGL 3.3 compatible
- Storage: 200 MB

### Target File Size
- < 100 MB (including all assets)

---

## 9. Development Plan

### Phase 1: Prototype (Completed - 2 weeks)
- Core tower placement and targeting
- Enemy pathfinding
- Basic wave system
- Gold/lives economy
- [x] Completed as Python/Pygame prototype

### Phase 2: Core Gameplay (4 weeks)
- All tower types implemented
- All enemy types implemented
- Full 10-wave campaign
- Upgrade system
- Basic UI

### Phase 3: Visual Polish (3 weeks)
- Pixel art assets (all sprites, backgrounds, UI)
- VFX and particle effects
- Sound effects and music
- Animation

### Phase 4: Content & Balance (3 weeks)
- Level design and map evolution
- Difficulty tuning
- Achievements
- Endless mode

### Phase 5: QA & Launch (4 weeks)
- Bug fixing
- Performance optimization
- Steam integration (achievements, cloud saves)
- Marketing assets (trailers, screenshots)
- Early Access launch
- Community feedback integration -> 1.0 release

**Total Development Time:** ~16 weeks (4 months)
**Team Size:** 3-5 people

---

## 10. Monetization

### Base Game
- Price: $12.99 USD
- Full campaign (10 waves + endless mode)

### Planned DLC
1. **New World Pack** - $7.99 (additional 10 waves, new map)
2. **Tower Masters** - $4.99 (2 new tower types)
3. **Challenge Pack** - $2.99 (special challenge maps)

### Free Updates
- Balance patches
- Quality of life improvements
- Seasonal events

---

*Document prepared by: MYC Game Studio*
*Departments involved: Game Design, Arte, Eng. Software, Analise de Dados*
