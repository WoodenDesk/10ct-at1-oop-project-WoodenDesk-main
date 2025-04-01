# enemy.py
import pygame
import math
import app

class Enemy:
    def __init__(self, x, y, enemy_type, enemy_assets, speed=app.DEFAULT_ENEMY_SPEED, level=1):
        # Core position attributes
        self.x = x  # X position in game world
        self.y = y  # Y position in game world
        self.speed = speed  # Movement speed
        self.facing_left = False  # Direction enemy is facing
        
        # Animation setup
        self.frames = enemy_assets[enemy_type]  # List of sprite frames
        self.frame_index = 0  # Current frame being shown
        self.animation_timer = 0  # Time until next frame
        self.animation_speed = 8  # Frames between animation updates
        self.image = self.frames[self.frame_index]  # Current sprite
        self.rect = self.image.get_rect(center=(self.x, self.y))  # Collision box
        
        # Stats
        self.max_health = int(12 * (1.15 ** (level - 1)))  # Health scales with level
        self.health = self.max_health
        self.level = level
        
        # Knockback system
        self.knockback_dist_remaining = 0  # Distance left to move when hit
        self.knockback_dx = self.knockback_dy = 0  # Knockback direction 

    def update(self, player):
        # Handle movement (knockback or chase player)
        if self.knockback_dist_remaining > 0:
            self.apply_knockback()
        else:
            self.move_toward_player(player)
        self.animate()

    def move_toward_player(self, player):
        # Calculate direction to player
        dx = player.x - self.x  # X distance to player
        dy = player.y - self.y  # Y distance to player
        dist = (dx**2 + dy**2) ** 0.5  # Total distance to player

        # Update position if not at player
        if dist != 0:
            self.x += (dx / dist) * self.speed  
            self.y += (dy / dist) * self.speed 


        # Face the correct direction
        self.facing_left = dx < 0  # Face left if player is to the left

        # Update collision box position
        self.rect.center = (self.x, self.y)

    def apply_knockback(self):
        step = min(app.ENEMY_KNOCKBACK_SPEED, self.knockback_dist_remaining)
        self.knockback_dist_remaining -= step

        self.x += self.knockback_dx * step
        self.y += self.knockback_dy * step

        if self.knockback_dx < 0:
            self.facing_left = True
        else:
            self.facing_left = False

        self.rect.center = (self.x, self.y)

    def animate(self):
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            center = self.rect.center
            self.image = self.frames[self.frame_index]
            self.rect = self.image.get_rect()
            self.rect.center = center

    def draw(self, surface):
        if self.facing_left:
            flipped_image = pygame.transform.flip(self.image, True, False)
            surface.blit(flipped_image, self.rect)
        else:
            surface.blit(self.image, self.rect)

        # Draw health bar
        self.draw_health_bar(surface)

    def draw_health_bar(self, surface):
        bar_width = 40  # Fixed width for health bar
        bar_height = 5
        health_ratio = self.health / self.max_health  # Use max_health instead of recalculating
        health_bar_width = int(bar_width * health_ratio)

        # Background bar (red)
        bar_x = self.rect.centerx - bar_width // 2  # Center the bar
        bar_y = self.rect.y - bar_height - 2
        pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))

        # Foreground bar (green)
        pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, health_bar_width, bar_height))

    def set_knockback(self, px, py, dist):
        dx = self.x - px
        dy = self.y - py
        length = math.sqrt(dx*dx + dy*dy)
        if length != 0:
            self.knockback_dx = dx / length
            self.knockback_dy = dy / length
            self.knockback_dist_remaining = dist

    def take_damage(self, amount):
        """Reduce enemy health by the given amount."""
        self.health = max(0, self.health - amount)  # Prevent negative health
        return self.health <= 0  # Return True if enemy should die
