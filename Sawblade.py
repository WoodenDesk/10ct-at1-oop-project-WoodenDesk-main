import pygame
import os
import app
import math 
import random

class Sawblade:
    def __init__(self, x, y, size=60, speed=5, is_orbiting=False, orbit_offset=0, orbit_radius=None):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.angle = 0  # Initial angle of rotation
        self.active = True  
        self.damage = 2  

        self.vx = 0  # Velocity X
        self.vy = 0  # Velocity Y
        self.friction = 0.95  
        self.acceleration = 0.3  

        self.is_orbiting = is_orbiting
        self.orbit_offset = orbit_offset  # Offset from base orbit angle
        self.orbit_radius = orbit_radius if orbit_radius is not None else size
        self.orbit_speed = 0.05  
        if is_orbiting:
            # Random speed modifier for orbiting blades cause otherwise they move in sync 
            self.orbit_speed *= random.uniform(0.9, 1.1)
        self.base_orbit_angle = 0  # Base angle for all orbiting sawblades
        self.parent_x = x
        self.parent_y = y


        sawblade_path = os.path.join("assets", "sawblade.png")  
        self.original_image = pygame.image.load(sawblade_path).convert_alpha()  # Use convert_alpha for transparency
        self.original_image = pygame.transform.scale(self.original_image, (self.size, self.size))  # Scale to new size
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(self.x, self.y))

        self.rotation_speed = 25  

    def apply_movement(self, dx, dy):
        # Add to velocity based on input
        self.vx += dx * self.acceleration
        self.vy += dy * self.acceleration

    def update(self):
        if self.is_orbiting:
            # Update orbit position based on main sawblade position and offset
            self.base_orbit_angle += self.orbit_speed
            actual_angle = self.base_orbit_angle + self.orbit_offset
            self.x = self.parent_x + math.cos(actual_angle) * self.orbit_radius
            self.y = self.parent_y + math.sin(actual_angle) * self.orbit_radius
            
        else:
            # Main sawblade physics
            self.x += self.vx
            self.y += self.vy
            self.vx *= self.friction
            self.vy *= self.friction
            self.x = max(0, min(app.WIDTH, self.x))
            self.y = max(0, min(app.HEIGHT, self.y))

        # Update rect position first
        self.rect.center = (self.x, self.y)
        
        # Then update rotation (changed from hardcoded 17)
        self.angle = (self.angle + self.rotation_speed) % 360
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        # Keep the same center when updating rect with rotated image
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def check_collision(self, enemies):
        if not self.active:
            return []
            
        collided_enemies = []
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                if enemy.take_damage(self.damage): 
                    collided_enemies.append(enemy)
        return collided_enemies

    def set_parent_position(self, x, y):
        self.parent_x = x
        self.parent_y = y
