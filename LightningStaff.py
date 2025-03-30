import pygame
import math
import random

class LightningStaff:
    def __init__(self, x, y, size=40):
        self.x = x
        self.y = y
        self.size = size
        self.damage = 4  
        self.chain_count = 2
        self.chain_range = 150 
        self.active = True
        self.zap_timer = 0
        self.zap_cooldown = 15  # Faster zapping
        self.lightning_color = (0, 191, 255)  # Brighter blue
        self.lightning_width = 4  # Thicker lines
        self.glow_radius = size * 1.5
        self.current_targets = []  # Store current lightning targets
        
        # Create staff visual with glow effect
        self.image = pygame.Surface((self.size * 3, self.size * 3), pygame.SRCALPHA)
        # Outer glow
        pygame.draw.circle(self.image, (0, 100, 255, 50), (self.size * 1.5, self.size * 1.5), self.glow_radius)
        pygame.draw.circle(self.image, (0, 150, 255, 100), (self.size * 1.5, self.size * 1.5), self.glow_radius * 0.7)
        # Core
        pygame.draw.circle(self.image, (100, 200, 255), (self.size * 1.5, self.size * 1.5), size//2)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self, player_x, player_y, enemies):
        self.x = player_x
        self.y = player_y
        self.rect.center = (self.x, self.y)
        
        if self.zap_timer > 0:
            self.zap_timer -= 1
        
        # Auto-attack when enemies are in range
        if self.zap_timer <= 0:
            self.try_attack(enemies)

    def find_chain_targets(self, enemies, start_pos):
        targets = []
        available_enemies = enemies.copy()
        current_pos = start_pos

        for _ in range(self.chain_count):
            nearest = None
            nearest_dist = self.chain_range
            
            for enemy in available_enemies:
                dist = math.sqrt((enemy.x - current_pos[0])**2 + (enemy.y - current_pos[1])**2)
                if dist < nearest_dist:
                    nearest = enemy
                    nearest_dist = dist

            if nearest:
                targets.append(nearest)
                available_enemies.remove(nearest)
                current_pos = (nearest.x, nearest.y)
            else:
                break

        return targets

    def check_collision(self, enemies):
        if self.zap_timer > 0 or not enemies:
            return []

        self.current_targets = self.find_chain_targets(enemies, (self.x, self.y))
        self.zap_timer = self.zap_cooldown
        
        killed_enemies = []
        for target in self.current_targets[:]:
            if target in enemies:
                if target.take_damage(self.damage):  # If enemy dies
                    killed_enemies.append(target)

        return killed_enemies

    def try_attack(self, enemies):
        return self.check_collision(enemies)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        
        # Draw lightning if we have targets
        if self.current_targets and self.zap_timer > self.zap_cooldown - 10:
            start_pos = (self.x, self.y)
            for target in self.current_targets:
                points = [start_pos]
                end_pos = (target.x, target.y)
                dist = math.sqrt((end_pos[0] - start_pos[0])**2 + (end_pos[1] - start_pos[1])**2)
                segments = int(dist / 10)  # More segments for jaggedness
                
                # Main lightning bolt
                for i in range(segments):
                    t = (i + 1) / segments
                    mid_x = start_pos[0] + (end_pos[0] - start_pos[0]) * t
                    mid_y = start_pos[1] + (end_pos[1] - start_pos[1]) * t
                    offset = random.randint(-15, 15)
                    points.append((mid_x + offset, mid_y + offset))
                points.append(end_pos)
                
                # Draw glow effect
                pygame.draw.lines(surface, (0, 50, 255, 128), False, points, self.lightning_width + 4)
                # Draw core lightning
                pygame.draw.lines(surface, self.lightning_color, False, points, self.lightning_width)
                # Draw bright center
                pygame.draw.lines(surface, (200, 230, 255), False, points, 2)
                
                start_pos = end_pos
