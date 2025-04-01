import pygame
import math
import random

class LightningStaff:
    def __init__(self, x, y, size=40):
        # Position and basic properties
        self.x = x
        self.y = y
        self.size = size
        self.active = True
        self.zap_timer = 0
        self.current_targets = []
        self.mini_staffs = []  # [x, y, time_remaining]

        # Visual properties
        self.lightning_color = (0, 191, 255)
        self.lightning_width = 4
        self.glow_radius = size * 1.5

        # Simplified upgrade system - just track levels and values
        self.upgrades = {
            'targets': {'level': 0, 'max': 2, 'base': 3, 'increment': 1},
            'range': {'level': 0, 'max': 5, 'base': 200, 'increment': 50},
            'damage': {'level': 0, 'max': 5, 'base': 2, 'increment': 2},
            'mini_count': {'level': 0, 'max': 5, 'base': 3, 'increment': 1},
            'mini_chance': {'level': 0, 'max': 5, 'base': 0.3, 'increment': 0.15},
            'mini_damage': {'level': 0, 'max': 5, 'base': 0.5, 'increment': 0.2},
            'mini_duration': {'level': 0, 'max': 5, 'base': 360, 'increment': 120},
        }

        # Create staff visual
        self.create_visual()

    def create_visual(self):
        # Create staff surface with glow effect
        self.image = pygame.Surface((self.size * 3, self.size * 3), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 100, 255, 50), (self.size * 1.5, self.size * 1.5), self.glow_radius)
        pygame.draw.circle(self.image, (0, 150, 255, 100), (self.size * 1.5, self.size * 1.5), self.glow_radius * 0.7)
        pygame.draw.circle(self.image, (100, 200, 255), (self.size * 1.5, self.size * 1.5), self.size // 2)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def get_upgrade_value(self, upgrade_type):
        if upgrade_type in self.upgrades:
            upgrade = self.upgrades[upgrade_type]
            return upgrade['base'] + (upgrade['increment'] * upgrade['level'])
        return 0

    def current_damage(self):
        return self.get_upgrade_value('damage')

    def current_chain_count(self):
        return int(self.get_upgrade_value('targets'))

    def current_chain_range(self):
        return self.get_upgrade_value('range')

    def current_cooldown(self):
        return max(5, self.get_upgrade_value('cooldown'))

    def max_mini_staffs(self):
        return self.get_upgrade_value('mini_count')

    def mini_staff_spawn_chance(self):
        return self.get_upgrade_value('mini_chance')
        
    def mini_staff_damage_mult(self):
        return self.get_upgrade_value('mini_damage')
        
    def mini_staff_duration(self):
        return self.get_upgrade_value('mini_duration')

    def upgrade(self, upgrade_type):
        if upgrade_type in self.upgrades:
            upgrade = self.upgrades[upgrade_type]
            if upgrade['level'] < upgrade['max']:
                upgrade['level'] += 1
                return True
        return False

    def update(self, player_x, player_y, enemies):
        self.x = player_x
        self.y = player_y
        self.rect.center = (self.x, self.y)

        if self.zap_timer > 0:
            self.zap_timer -= 1
        elif len(self.current_targets) > 0:
            self.current_targets = []

        # Update mini-staffs
        for mini in self.mini_staffs[:]:
            mini[2] -= 1
            if mini[2] <= 0:
                self.mini_staffs.remove(mini)

    def check_collision(self, enemies):
        if not self.active or self.zap_timer > 0:
            return []

        collided_enemies = []
        
        targets = self.find_multiple_targets(enemies, (self.x, self.y))
        self.current_targets = targets
        self.zap_timer = self.current_cooldown()

        for enemy in targets:
            if enemy in enemies:
                if enemy.take_damage(self.current_damage()):
                    collided_enemies.append(enemy)
                    if len(self.mini_staffs) < self.max_mini_staffs() and random.random() < self.mini_staff_spawn_chance():
                        self.mini_staffs.append([enemy.x, enemy.y, self.mini_staff_duration()])

        # Mini-staffs damage and targets
        mini_staff_targets = {}
        for mini in self.mini_staffs:
            mini_targets = self.find_multiple_targets(enemies, (mini[0], mini[1]))
            mini_staff_targets[tuple(mini)] = mini_targets
            for enemy in mini_targets:
                if enemy in enemies:
                    if enemy.take_damage(self.current_damage() * self.mini_staff_damage_mult()):
                        collided_enemies.append(enemy)

        self.mini_staff_targets = mini_staff_targets
        return collided_enemies

    def find_multiple_targets(self, enemies, start_pos):
        if not enemies: # mainly for the very start as this caused a crash 
            return []

        targets = []
        max_targets = self.get_upgrade_value('targets')
        available_enemies = enemies.copy()
        range_limit = self.get_upgrade_value('range')

        while len(targets) < max_targets and available_enemies:
            nearest = None
            nearest_dist = range_limit

            for enemy in available_enemies:
                dist = math.sqrt((enemy.x - start_pos[0])**2 + (enemy.y - start_pos[1])**2)
                if dist < nearest_dist:
                    nearest = enemy
                    nearest_dist = dist

            if nearest:
                targets.append(nearest)
                available_enemies.remove(nearest)
            else:
                break

        return targets

    def draw_lightning(self, surface, start_pos, target_pos, width_mult=1.0):
        # Create list of points starting with the source position
        points = [start_pos]
        
        # Calculate total distance between start and end points
        dist = math.sqrt((target_pos[0] - start_pos[0]) ** 2 + (target_pos[1] - start_pos[1]) ** 2)
        
        # Divide the line into segments (1 segment per 10 pixels)
        segments = int(dist / 10)

        # Generate jagged lightning effect
        for i in range(segments):
            # Calculate position along the line (t goes from 0 to 1)
            t = (i + 1) / segments
            
            # Get the position on straight line between start and end
            mid_x = start_pos[0] + (target_pos[0] - start_pos[0]) * t
            mid_y = start_pos[1] + (target_pos[1] - start_pos[1]) * t
            
            # Add random offset (-15 to +15 pixels) to create jagged effect
            offset = random.randint(-15, 15)
            points.append((mid_x + offset, mid_y + offset))
        
        # Add the final target position
        points.append(target_pos)

        # Draw 3 layers of lightning:
        # 1. Wide dark blue background glow
        pygame.draw.lines(surface, (0, 50, 255, 128), False, points, 
                         int(self.lightning_width * width_mult + 4))
        
        # 2. Medium bright blue main bolt
        pygame.draw.lines(surface, self.lightning_color, False, points,
                         int(self.lightning_width * width_mult))
        
        # 3. Thin white center for intensity
        pygame.draw.lines(surface, (200, 230, 255), False, points,
                         int(2 * width_mult))

    def draw(self, surface):
        # Draw main staff
        surface.blit(self.image, self.rect)

        # Draw mini-staffs and their lightning
        mini_image = pygame.transform.scale(self.image, (int(self.size * 1.5), int(self.size * 1.5)))
        for mini in self.mini_staffs:
            # Draw mini-staff
            mini_rect = mini_image.get_rect(center=(mini[0], mini[1]))
            surface.blit(mini_image, mini_rect)

            # Draw lightning from mini-staff if it hit targets this frame
            if hasattr(self, 'mini_staff_targets') and tuple(mini) in self.mini_staff_targets:
                mini_targets = self.mini_staff_targets[tuple(mini)]
                for target in mini_targets[:self.current_chain_count()]:
                    self.draw_lightning(surface, (mini[0], mini[1]), (target.x, target.y), 0.7)

        # Draw main staff lightning
        if self.current_targets and self.zap_timer > self.current_cooldown() - 10:
            start_pos = (self.x, self.y)
            for target in self.current_targets:
                self.draw_lightning(surface, start_pos, (target.x, target.y))
