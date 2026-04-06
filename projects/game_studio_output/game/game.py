"""
Tower Defense Game - MYC Game Studio
A complete 2D tower defense game built with Pygame.

Features:
- 3 tower types: Archer, Cannon, Mage
- 4 enemy types: Normal, Fast, Armored, Boss
- Wave-based spawning with increasing difficulty
- Currency system (gold) for buying/upgrading towers
- Score and lives tracking
- Start screen, gameplay, and game over screen
"""

import pygame
import math
import random
import sys

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 720
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_BG = (18, 18, 24)
PANEL_BG = (28, 28, 36)
GREEN = (46, 196, 83)
RED = (220, 53, 69)
YELLOW = (255, 193, 7)
BLUE = (13, 110, 253)
CYAN = (0, 210, 211)
PURPLE = (165, 94, 234)
ORANGE = (253, 126, 20)
GRAY = (108, 117, 125)
LIGHT_GRAY = (200, 200, 210)
GOLD = (255, 215, 0)

# Game states
STATE_START = 0
STATE_PLAYING = 1
STATE_GAMEOVER = 2
STATE_WAVE_TRANSITION = 3

# ==========================================
# AUDIO (placeholder sound effects)
# ==========================================
class SoundManager:
    """Manages placeholder sound effects."""
    def __init__(self):
        self.sounds = {}
        self.enabled = True
        try:
            # Create simple beep sounds for feedback
            self._init_sound_system()
        except Exception:
            self.enabled = False

    def _init_sound_system(self):
        self.enabled = False  # No real sound files; visual feedback only

    def play(self, name):
        """Play a placeholder sound (no-op, visual feedback used instead)."""
        pass

# ==========================================
# PATH DEFINITION
# ==========================================
class Path:
    """Defines the enemy path as a series of waypoints."""
    def __init__(self):
        self.waypoints = [
            (-30, 140),
            (120, 140),
            (120, 280),
            (300, 280),
            (300, 100),
            (500, 100),
            (500, 350),
            (250, 350),
            (250, 500),
            (500, 500),
            (500, 620),
            (700, 620),
            (700, 450),
            (850, 450),
            (850, 280),
            (950, 280),
            (950, 550),
            (1080, 550),
        ]
        self._compute_segments()

    def _compute_segments(self):
        self.segments = []
        self.total_length = 0
        for i in range(len(self.waypoints) - 1):
            p1 = self.waypoints[i]
            p2 = self.waypoints[i + 1]
            length = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
            self.segments.append((p1, p2, length, self.total_length))
            self.total_length += length

    def get_position(self, distance):
        """Get (x, y) at a given distance along the path."""
        remaining = distance
        for p1, p2, length, seg_start in self.segments:
            if remaining <= length:
                t = remaining / length if length > 0 else 0
                return (p1[0] + (p2[0] - p1[0]) * t,
                        p1[1] + (p2[1] - p1[1]) * t)
            remaining -= length
        return self.waypoints[-1]

    def draw(self, surface):
        """Draw the path on the surface."""
        if len(self.waypoints) < 2:
            return
        # Path background
        pygame.draw.lines(surface, (35, 35, 45), False, self.waypoints, 44)
        # Path center line
        pygame.draw.lines(surface, (55, 55, 65), False, self.waypoints, 36)
        # Dashed center line
        for i in range(len(self.waypoints) - 1):
            p1 = self.waypoints[i]
            p2 = self.waypoints[i + 1]
            length = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
            if length == 0:
                continue
            dx = (p2[0] - p1[0]) / length
            dy = (p2[1] - p1[1]) / length
            dash_len = 10
            gap_len = 10
            d = 0
            while d < length:
                start = (p1[0] + dx * d, p1[1] + dy * d)
                end_d = min(d + dash_len, length)
                end = (p1[0] + dx * end_d, p1[1] + dy * end_d)
                pygame.draw.line(surface, (70, 70, 80), start, end, 2)
                d += dash_len + gap_len

# ==========================================
# TOWER DEFINITIONS
# ==========================================
TOWER_TYPES = {
    "archer": {
        "name": "Archer",
        "cost": 50,
        "damage": 10,
        "range": 120,
        "fire_rate": 0.8,
        "color": GREEN,
        "projectile_color": (144, 238, 144),
        "projectile_speed": 300,
        "upgrade_costs": [75, 125],
        "upgrade_damage": [15, 25],
        "upgrade_range": [135, 155],
        "description": "Fast attacks, single target",
    },
    "cannon": {
        "name": "Cannon",
        "cost": 100,
        "damage": 30,
        "range": 100,
        "fire_rate": 2.0,
        "color": ORANGE,
        "projectile_color": (255, 140, 0),
        "projectile_speed": 200,
        "splash_radius": 50,
        "upgrade_costs": [150, 225],
        "upgrade_damage": [45, 70],
        "upgrade_range": [115, 135],
        "description": "Slow attacks, splash damage",
    },
    "mage": {
        "name": "Mage",
        "cost": 150,
        "damage": 5,
        "range": 150,
        "fire_rate": 0.1,
        "color": PURPLE,
        "projectile_color": CYAN,
        "projectile_speed": 250,
        "slow_factor": 0.5,
        "slow_duration": 2.0,
        "upgrade_costs": [200, 300],
        "upgrade_damage": [8, 15],
        "upgrade_range": [170, 200],
        "description": "Slows enemies, continuous beam",
    },
}

# ==========================================
# ENEMY DEFINITIONS
# ==========================================
ENEMY_TYPES = {
    "normal": {
        "name": "Normal",
        "hp": 50,
        "speed": 80,
        "reward": 10,
        "color": RED,
        "size": 10,
    },
    "fast": {
        "name": "Fast",
        "hp": 30,
        "speed": 140,
        "reward": 12,
        "color": YELLOW,
        "size": 8,
    },
    "armored": {
        "name": "Armored",
        "hp": 150,
        "speed": 50,
        "reward": 25,
        "color": (150, 150, 160),
        "size": 14,
        "armor": 0.3,
    },
    "boss": {
        "name": "Boss",
        "hp": 500,
        "speed": 35,
        "reward": 100,
        "color": (180, 0, 0),
        "size": 20,
        "armor": 0.2,
    },
}

# ==========================================
# WAVE DEFINITIONS
# ==========================================
def generate_waves():
    """Generate wave compositions with increasing difficulty."""
    waves = []
    # Wave 1
    waves.append({"normal": 8})
    # Wave 2
    waves.append({"normal": 10, "fast": 3})
    # Wave 3
    waves.append({"normal": 8, "fast": 8})
    # Wave 4
    waves.append({"fast": 15, "armored": 2})
    # Wave 5
    waves.append({"normal": 15, "armored": 5})
    # Wave 6
    waves.append({"fast": 12, "armored": 8})
    # Wave 7 - Boss wave
    waves.append({"normal": 10, "fast": 10, "armored": 5, "boss": 1})
    # Wave 8
    waves.append({"fast": 20, "armored": 10, "boss": 2})
    # Wave 9
    waves.append({"normal": 25, "armored": 15, "boss": 3})
    # Wave 10 - Final
    waves.append({"fast": 30, "armored": 20, "boss": 5})
    return waves

# ==========================================
# GAME CLASSES
# ==========================================
class Enemy:
    """Enemy unit that follows the path."""
    def __init__(self, enemy_type, wave_scale=1.0):
        self.type_name = enemy_type
        data = ENEMY_TYPES[enemy_type]
        self.max_hp = int(data["hp"] * wave_scale)
        self.hp = self.max_hp
        self.base_speed = data["speed"]
        self.speed = self.base_speed
        self.reward = int(data["reward"] * (1 + (wave_scale - 1) * 0.5))
        self.color = data["color"]
        self.size = data["size"]
        self.armor = data.get("armor", 0)
        self.distance = 0
        self.x, self.y = 0, 0
        self.alive = True
        self.reached_end = False
        self.slow_timer = 0
        self.slow_factor = 1.0
        self.hit_flash = 0

    def update(self, dt, path):
        """Move enemy along the path."""
        if not self.alive:
            return
        # Update slow timer
        if self.slow_timer > 0:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.slow_factor = 1.0
        else:
            self.slow_factor = 1.0

        self.speed = self.base_speed * self.slow_factor
        self.distance += self.speed * dt

        # Update position
        self.x, self.y = path.get_position(self.distance)

        # Check if reached end
        if self.distance >= path.total_length:
            self.reached_end = True
            self.alive = False

        if self.hit_flash > 0:
            self.hit_flash -= dt * 5

    def take_damage(self, amount):
        """Apply damage considering armor."""
        actual = amount * (1 - self.armor)
        self.hp -= actual
        self.hit_flash = 1.0
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            return True
        return False

    def apply_slow(self, factor, duration):
        """Apply slow debuff."""
        self.slow_factor = min(self.slow_factor, factor)
        self.slow_timer = max(self.slow_timer, duration)

    def draw(self, surface):
        """Draw the enemy."""
        if not self.alive:
            return
        draw_color = WHITE if self.hit_flash > 0 else self.color
        if self.slow_factor < 1:
            # Blue tint when slowed
            draw_color = (min(draw_color[0], 100),
                         min(draw_color[1], 150),
                         min(draw_color[2] + 100, 255))
        pygame.draw.circle(surface, draw_color, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), self.size, 2)

        # Health bar
        bar_width = self.size * 2
        bar_height = 4
        bar_x = int(self.x) - bar_width // 2
        bar_y = int(self.y) - self.size - 8
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        hp_color = GREEN if hp_ratio > 0.5 else (YELLOW if hp_ratio > 0.25 else RED)
        pygame.draw.rect(surface, hp_color, (bar_x, bar_y, int(bar_width * hp_ratio), bar_height))


class Tower:
    """Tower that shoots at enemies."""
    def __init__(self, tower_type, grid_x, grid_y):
        self.type_name = tower_type
        self.level = 0
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.x = grid_x * 40 + 20
        self.y = grid_y * 40 + 20
        self._apply_stats()

    def _apply_stats(self):
        data = TOWER_TYPES[self.type_name]
        self.damage = data["damage"]
        self.range = data["range"]
        self.fire_rate = data["fire_rate"]
        self.cooldown = 0
        self.color = data["color"]
        self.projectile_color = data["projectile_color"]
        self.projectile_speed = data["projectile_speed"]
        self.splash_radius = data.get("splash_radius", 0)
        self.slow_factor = data.get("slow_factor", 0)
        self.slow_duration = data.get("slow_duration", 0)
        self.total_invested = data["cost"]

    def upgrade(self):
        """Upgrade the tower."""
        data = TOWER_TYPES[self.type_name]
        if self.level >= len(data["upgrade_costs"]):
            return False
        cost = data["upgrade_costs"][self.level]
        self.damage = data["upgrade_damage"][self.level]
        self.range = data["upgrade_range"][self.level]
        self.total_invested += cost
        self.level += 1
        return True

    def upgrade_cost(self):
        """Get cost of next upgrade."""
        data = TOWER_TYPES[self.type_name]
        if self.level < len(data["upgrade_costs"]):
            return data["upgrade_costs"][self.level]
        return None

    def is_max_level(self):
        """Check if tower is at max level."""
        data = TOWER_TYPES[self.type_name]
        return self.level >= len(data["upgrade_costs"])

    def find_target(self, enemies):
        """Find the closest enemy in range."""
        best = None
        best_dist = float('inf')
        for e in enemies:
            if not e.alive:
                continue
            dist = math.sqrt((e.x - self.x)**2 + (e.y - self.y)**2)
            if dist <= self.range and dist < best_dist:
                best = e
                best_dist = dist
        return best

    def shoot(self, target):
        """Create a projectile toward the target."""
        return Projectile(self.x, self.y, target, self)

    def draw(self, surface, show_range=False):
        """Draw the tower."""
        tower_rect = pygame.Rect(self.x - 16, self.y - 16, 32, 32)
        pygame.draw.rect(surface, self.color, tower_rect, border_radius=4)
        pygame.draw.rect(surface, BLACK, tower_rect, 2, border_radius=4)

        # Level indicator
        for i in range(self.level + 1):
            dot_x = self.x - 8 + i * 8
            pygame.draw.circle(surface, GOLD, (dot_x, self.y + 10), 3)

        if show_range:
            pygame.draw.circle(surface, (255, 255, 255, 50),
                             (int(self.x), int(self.y)), self.range, 1)


class Projectile:
    """Projectile fired by towers."""
    def __init__(self, x, y, target, tower):
        self.x = x
        self.y = y
        self.target = target
        self.tower = tower
        self.speed = tower.projectile_speed
        self.alive = True

    def update(self, dt):
        """Move projectile toward target."""
        if not self.alive or not self.target.alive:
            self.alive = False
            return
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < 10:
            self.hit()
            return
        nx, ny = dx/dist, dy/dist
        self.x += nx * self.speed * dt
        self.y += ny * self.speed * dt

    def hit(self):
        """Apply damage to target."""
        self.alive = False
        killed = self.target.take_damage(self.tower.damage)

        if self.tower.slow_factor > 0:
            self.target.apply_slow(self.tower.slow_factor, self.tower.slow_duration)

        if self.tower.splash_radius > 0:
            # Splash damage to nearby enemies (not target)
            for e in Game.enemies:
                if e != self.target and e.alive:
                    dist = math.sqrt((e.x - self.target.x)**2 + (e.y - self.target.y)**2)
                    if dist < self.tower.splash_radius:
                        e.take_damage(self.tower.damage * 0.5)

        return killed

    def draw(self, surface):
        """Draw the projectile."""
        if not self.alive:
            return
        pygame.draw.circle(surface, self.tower.projectile_color,
                         (int(self.x), int(self.y)), 4)


class Particle:
    """Visual particle effect."""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.life = 1.0
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(50, 150)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt * 2

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = max(0, self.life)
        size = max(1, int(4 * self.life))
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), size)


# ==========================================
# MAIN GAME CLASS
# ==========================================
class Game:
    """Main game controller."""
    enemies = []  # Class-level reference for splash damage

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tower Defense - MYC Game Studio")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20)
        self.font_big = pygame.font.SysFont("Arial", 36, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 16)
        self.state = STATE_START
        self.reset()

    def reset(self):
        """Reset game state."""
        self.path = Path()
        self.towers = []
        self.enemies = []
        self.projectiles = []
        self.particles = []
        self.gold = 200
        self.lives = 20
        self.score = 0
        self.wave = 0
        self.waves = generate_waves()
        self.wave_enemies_remaining = []
        self.wave_spawn_timer = 0
        self.wave_active = False
        self.wave_transition_timer = 0
        self.game_over_timer = 0
        self.selected_tower_type = None
        self.selected_tower = None
        self.hover_grid = None
        self.sound_manager = SoundManager()
        Game.enemies = self.enemies

    def start_wave(self):
        """Start the next wave."""
        if self.wave >= len(self.waves):
            return
        wave_composition = self.waves[self.wave]
        self.wave_enemies_remaining = []
        for etype, count in wave_composition.items():
            self.wave_enemies_remaining.extend([etype] * count)
        random.shuffle(self.wave_enemies_remaining)
        self.wave_spawn_timer = 0
        self.wave_active = True
        self.wave += 1

    def spawn_enemy(self):
        """Spawn an enemy from the wave queue."""
        if not self.wave_enemies_remaining:
            self.wave_active = False
            return
        etype = self.wave_enemies_remaining.pop(0)
        wave_scale = 1.0 + (self.wave - 1) * 0.15
        enemy = Enemy(etype, wave_scale)
        self.enemies.append(enemy)

    def handle_events(self):
        """Handle input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_SPACE and self.state == STATE_PLAYING:
                    if not self.wave_active and self.wave < len(self.waves):
                        self.start_wave()
                if event.key == pygame.K_1:
                    self.selected_tower_type = "archer"
                if event.key == pygame.K_2:
                    self.selected_tower_type = "cannon"
                if event.key == pygame.K_3:
                    self.selected_tower_type = "mage"
                if event.key == pygame.K_s:
                    self.selected_tower_type = None
                    self.selected_tower = None
                if event.key == pygame.K_u and self.selected_tower:
                    t = self.selected_tower
                    cost = t.upgrade_cost()
                    if cost and self.gold >= cost:
                        self.gold -= cost
                        t.upgrade()
                        self.sound_manager.play("upgrade")

            if event.type == pygame.MOUSEBUTTONDOWN and self.state == STATE_PREP:
                if event.button == 1:  # Left click
                    self.handle_click(event.pos)
                elif event.button == 3:  # Right click
                    self.selected_tower_type = None
                    self.selected_tower = None

        return True

    def handle_click(self, pos):
        """Handle mouse click for tower placement/interaction."""
        mx, my = pos

        # Check UI buttons
        if self.state == STATE_PREP:
            if mx >= 820 and mx <= 980:
                if my >= 600 and my <= 640:
                    self.start_wave()
                    return

        # Convert to grid coords
        grid_x = mx // 40
        grid_y = my // 40

        # Check if clicking on existing tower
        for t in self.towers:
            if t.grid_x == grid_x and t.grid_y == grid_y:
                self.selected_tower = t
                self.selected_tower_type = None
                return

        # Place tower
        if self.selected_tower_type:
            if self.can_place(grid_x, grid_y):
                tower_data = TOWER_TYPES[self.selected_tower_type]
                if self.gold >= tower_data["cost"]:
                    self.gold -= tower_data["cost"]
                    tower = Tower(self.selected_tower_type, grid_x, grid_y)
                    self.towers.append(tower)
                    self.sound_manager.play("place")

    def can_place(self, grid_x, grid_y):
        """Check if a tower can be placed at grid position."""
        # Check bounds
        if grid_x < 0 or grid_x >= 20 or grid_y < 0 or grid_y >= 17:
            return False

        # Check if occupied by another tower
        for t in self.towers:
            if t.grid_x == grid_x and t.grid_y == grid_y:
                return False

        # Check if on path
        for seg in self.path.segments:
            p1, p2 = seg[0], seg[1]
            # Check if grid cell is close to path segment
            cell_cx = grid_x * 40 + 20
            cell_cy = grid_y * 40 + 20
            dist = self._point_to_segment_dist(cell_cx, cell_cy, p1, p2)
            if dist < 25:
                return False

        return True

    def _point_to_segment_dist(self, px, py, p1, p2):
        """Distance from point to line segment."""
        x1, y1 = p1
        x2, y2 = p2
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0 and dy == 0:
            return math.sqrt((px - x1)**2 + (py - y1)**2)
        t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        return math.sqrt((px - closest_x)**2 + (py - closest_y)**2)

    def update(self, dt):
        """Update game state."""
        if self.state == STATE_PLAYING or self.state == STATE_PREP:
            self._update_gameplay(dt)

    def _update_gameplay(self, dt):
        """Core gameplay update."""
        # Spawn enemies
        if self.wave_active:
            self.wave_spawn_timer -= dt
            if self.wave_spawn_timer <= 0:
                self.spawn_enemy()
                self.wave_spawn_timer = 0.5  # Spawn interval

        # Update enemies
        for e in self.enemies:
            e.update(dt, self.path)
            if e.reached_end and e.alive:
                self.lives -= 1
                self.sound_manager.play("damage")
            if not e.alive and e.hp <= 0 and not hasattr(e, '_rewarded'):
                e._rewarded = True
                self.gold += e.reward
                self.score += e.reward * 5
                # Spawn particles
                for _ in range(8):
                    self.particles.append(Particle(e.x, e.y, e.color))

        # Remove dead enemies
        self.enemies = [e for e in self.enemies if e.alive]

        # Check wave completion
        if not self.wave_active and not self.wave_enemies_remaining and not self.enemies:
            if self.wave > 0 and self.lives > 0:
                if len(self.towers) == 0 or self.state != STATE_PREP:
                    self.state = STATE_PREP
                    self.wave_transition_timer = 2.0
                    # Wave completion bonus
                    bonus = 25 + self.wave * 10
                    self.gold += bonus

            # Check if won (all waves complete)
            if self.wave >= len(self.waves):
                self.score += 1000
                self.state = STATE_GAMEOVER
                self.game_over_timer = 300

        # Update towers
        for t in self.towers:
            t.cooldown -= dt
            if t.cooldown <= 0:
                target = t.find_target(self.enemies)
                if target:
                    proj = t.shoot(target)
                    self.projectiles.append(proj)
                    t.cooldown = t.fire_rate

        # Update projectiles
        for p in self.projectiles:
            p.update(dt)

        self.projectiles = [p for p in self.projectiles if p.alive]

        # Update particles
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.life > 0]

        # Check game over
        if self.lives <= 0:
            self.state = STATE_GAMEOVER
            self.game_over_timer = 300

    def draw(self):
        """Render everything."""
        self.screen.fill(DARK_BG)

        if self.state == STATE_START:
            self.draw_start_screen()
        elif self.state == STATE_PREP:
            self.draw_game_screen()
            self.draw_ui()
            self.draw_build_menu()
            if self.wave_transition_timer > 0:
                self.draw_wave_announcement()
        elif self.state == STATE_PLAYING:
            self.draw_game_screen()
            self.draw_ui()
            self.draw_build_menu()
        elif self.state == STATE_GAMEOVER:
            self.draw_game_screen()
            self.draw_ui()
            self.draw_game_over()

        pygame.display.flip()

    def draw_start_screen(self):
        """Draw the start/title screen."""
        # Title
        title_surf = self.font_big.render("TOWER DEFENSE", True, GOLD)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 180))
        self.screen.blit(title_surf, title_rect)

        subtitle = self.font.render("A MYC Game Studio Production", True, LIGHT_GRAY)
        sub_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 230))
        self.screen.blit(subtitle, sub_rect)

        # Instructions
        instructions = [
            "Press SPACE or click 'Start Wave' to begin",
            "Keys 1/2/3: Select Archer/Cannon/Mage tower",
            "S: Deselect  |  U: Upgrade selected tower",
            "Click on the grid to place towers",
            "Right-click to deselect",
            "",
            "Tower Types:",
            "[1] Archer  - Fast attacks, single target (50g)",
            "[2] Cannon  - Splash damage (100g)",
            "[3] Mage    - Slows enemies (150g)",
        ]
        for i, line in enumerate(instructions):
            color = YELLOW if i >= 7 else WHITE
            surf = self.font_small.render(line, True, color)
            self.screen.blit(surf, (SCREEN_WIDTH // 2 - 180, 310 + i * 24))

        # Start button
        mouse = pygame.mouse.get_pos()
        btn_color = GREEN if (SCREEN_WIDTH//2-100 <= mouse[0] <= SCREEN_WIDTH//2+100 and 580 <= mouse[1] <= 620) else (30, 130, 50)
        pygame.draw.rect(self.screen, btn_color, (SCREEN_WIDTH//2-100, 580, 200, 40), border_radius=8)
        text = self.font.render("CLICK TO START", True, WHITE)
        self.screen.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, 600)))

        # Version
        ver = self.font_small.render("v1.0 - MYC Game Studio 2025", True, GRAY)
        self.screen.blit(ver, ver.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)))

        # Handle start screen click
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if SCREEN_WIDTH//2-100 <= event.pos[0] <= SCREEN_WIDTH//2+100 and 580 <= event.pos[1] <= 620:
                    self.state = STATE_PREP
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.state = STATE_PREP

    def draw_wave_announcement(self):
        """Draw wave number announcement."""
        alpha = min(1.0, self.wave_transition_timer)
        wave_text = f"WAVE {self.wave} COMPLETE!"
        if self.wave >= len(self.waves):
            wave_text = "ALL WAVES COMPLETE!"
        bonus = 25 + self.wave * 10
        bonus_text = f"Bonus: +{bonus}g"
        surf = self.font_big.render(wave_text, True, GREEN)
        self.screen.blit(surf, surf.get_rect(center=(SCREEN_WIDTH // 2 - 80, 200)))
        surf2 = self.font.render(bonus_text, True, GOLD)
        self.screen.blit(surf2, surf2.get_rect(center=(SCREEN_WIDTH // 2 - 80, 240)))

    def draw_game_screen(self):
        """Draw the main game area."""
        # Draw path
        self.path.draw(self.screen)

        # Draw grid (subtle)
        for x in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(self.screen, (30, 30, 38), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(self.screen, (30, 30, 38), (0, y), (SCREEN_WIDTH, y))

        # Draw hover highlight
        mouse_x, mouse_y = pygame.mouse.get_pos()
        grid_x = mouse_x // 40
        grid_y = mouse_y // 40
        if self.selected_tower_type and 0 <= grid_x < 20 and 0 <= grid_y < 17:
            can_place = self.can_place(grid_x, grid_y)
            color = GREEN if can_place else RED
            pygame.draw.rect(self.screen, color,
                           (grid_x * 40, grid_y * 40, 40, 40), 2)

        # Draw towers
        for t in self.towers:
            show_range = (t == self.selected_tower)
            t.draw(self.screen, show_range)

        # Draw enemies
        for e in self.enemies:
            e.draw(self.screen)

        # Draw projectiles
        for p in self.projectiles:
            p.draw(self.screen)

        # Draw particles
        for p in self.particles:
            p.draw(self.screen)

        # Draw selected tower info
        if self.selected_tower:
            t = self.selected_tower
            info_y = 640
            data = TOWER_TYPES[t.type_name]
            texts = [
                f"{data['name']} Lv.{t.level + 1}",
                f"DMG: {t.damage} | Range: {t.range}",
                f"Rate: {t.fire_rate}s",
            ]
            if t.is_max_level():
                texts.append("MAX LEVEL")
            else:
                cost = t.upgrade_cost()
                texts.append(f"Upgrade: {cost}g (U)")
            for i, text in enumerate(texts):
                color = YELLOW if "MAX" in text else WHITE
                surf = self.font_small.render(text, True, color)
                self.screen.blit(surf, (820, info_y + i * 20))

    def draw_ui(self):
        """Draw the top UI bar."""
        pygame.draw.rect(self.screen, PANEL_BG, (0, 0, SCREEN_WIDTH, 50))
        pygame.draw.line(self.screen, (50, 50, 60), (0, 50), (SCREEN_WIDTH, 50))

        stats = [
            f"Wave: {self.wave}/{len(self.waves)}",
            f"Gold: {self.gold}",
            f"Lives: {self.lives}",
            f"Score: {self.score}",
        ]
        colors = [WHITE, GOLD, RED if self.lives <= 5 else GREEN, CYAN]
        for i, (text, color) in enumerate(zip(stats, colors)):
            surf = self.font.render(text, True, color)
            self.screen.blit(surf, (10 + i * 240, 13))

    def draw_build_menu(self):
        """Draw the build menu panel."""
        panel_x = 820
        panel_y = 55
        panel_w = 200
        panel_h = 300

        pygame.draw.rect(self.screen, PANEL_BG, (panel_x, panel_y, panel_w, panel_h))
        pygame.draw.rect(self.screen, (50, 50, 60), (panel_x, panel_y, panel_w, panel_h))

        title = self.font.render("Build", True, LIGHT_GRAY)
        self.screen.blit(title, (panel_x + 10, panel_y + 5))

        y = panel_y + 35
        for key in ["archer", "cannon", "mage"]:
            data = TOWER_TYPES[key]
            selected = self.selected_tower_type == key
            bg_color = (50, 50, 60) if selected else (40, 40, 50)
            pygame.draw.rect(self.screen, bg_color, (panel_x + 5, y, panel_w - 10, 55))

            if selected:
                pygame.draw.rect(self.screen, data["color"], (panel_x + 5, y, panel_w - 10, 55), 2)

            pygame.draw.rect(self.screen, data["color"], (panel_x + 10, y + 5, 16, 16))
            name_surf = self.font_small.render(f"{data['name']} [{key[0].upper()}]", True, WHITE)
            pos_surf = self.font_small.render(f"{data['cost']}g | DMG:{data['damage']}", True, GRAY)
            desc_surf = self.font_small.render(data['description'], True, GRAY)
            self.screen.blit(name_surf, (panel_x + 32, y + 3))
            self.screen.blit(pos_surf, (panel_x + 32, y + 20))
            self.screen.blit(desc_surf, (panel_x + 10, y + 38))
            y += 60

        # Start wave button
        btn_enabled = not self.wave_active and self.wave_enemies_remaining
        btn_color = GREEN if btn_enabled else GRAY
        pygame.draw.rect(self.screen, btn_color, (panel_x + 10, panel_y + 240, panel_w - 20, 40), border_radius=6)
        btn_text = "Start Wave" if self.wave < len(self.waves) else "No More Waves"
        text_surf = self.font.render(btn_text, True, WHITE)
        self.screen.blit(text_surf, text_surf.get_rect(center=(panel_x + panel_w // 2, panel_y + 260)))

    def draw_game_over(self):
        """Draw game over screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        self.screen.blit(overlay, (0, 0))

        won = self.lives > 0 and self.wave >= len(self.waves)
        title = "VICTORY!" if won else "GAME OVER"
        color = GREEN if won else RED

        title_surf = self.font_big.render(title, True, color)
        self.screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2 - 80, 150)))

        stats = [
            f"Final Score: {self.score}",
            f"Waves Survived: {self.wave}/{len(self.waves)}",
            f"Lives Remaining: {self.lives}",
            f"Towers Built: {len(self.towers)}",
        ]
        for i, text in enumerate(stats):
            surf = self.font.render(text, True, WHITE)
            self.screen.blit(surf, surf.get_rect(center=(SCREEN_WIDTH // 2 - 80, 230 + i * 35)))

        restart_text = self.font.render("Press ENTER to restart  |  ESC to quit", True, LIGHT_GRAY)
        self.screen.blit(restart_text, restart_text.get_rect(center=(SCREEN_WIDTH // 2 - 80, 400)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.reset()
                elif event.key == pygame.K_ESCAPE:
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.reset()

    def run(self):
        """Main game loop."""
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0

            # Handle wave transition timer
            if self.state == STATE_PREP and self.wave_transition_timer > 0:
                self.wave_transition_timer -= dt

            running = self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()


# ==========================================
# ENTRY POINT
# ==========================================
if __name__ == "__main__":
    game = Game()
    game.run()
