import pygame
import app
import math
import os

from bullet import Bullet
from Sawblade import Sawblade  # Import the Sawblade class
from LightningStaff import LightningStaff

class Player:
    def __init__(self, x, y, assets, weapon_choice):
        self.x = x
        self.y = y
        self.level = 1

        self.speed = app.PLAYER_SPEED
        self.animations = assets["player"]
        self.state = "idle"
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 8

        self.image = self.animations[self.state][self.frame_index]
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.facing_left = False

        self.health = 5
        self.xp = 0

        self.bullet_speed = 10
        self.bullet_size = 10
        self.bullet_count = 1
        self.bullet_spread = 10  # Angle spread between bullets
        self.bullet_damage = 6  # Changed from 1 to 6
        self.shoot_cooldown = 20
        self.shoot_timer = 0
        self.bullets = []

        self.weapon_choice = weapon_choice
        self.sawblades = []
        if self.weapon_choice == "sawblade":
            self.sawblade = Sawblade(self.x, self.y)  # Main sawblade
            self.sawblades = [self.sawblade]  # List to hold all sawblades
        elif self.weapon_choice == "lightning":
            self.lightning_staff = LightningStaff(self.x, self.y)
        else:
            self.sawblade = None

        self.enemies = []  # Add enemies as instance variable

    def handle_input(self):
        keys = pygame.key.get_pressed()

        vel_x, vel_y = 0, 0

        if keys[pygame.K_LEFT]:
            # Move character left
            vel_x -= self.speed
        if keys[pygame.K_RIGHT]:
            vel_x += self.speed
        if keys[pygame.K_UP]:
            vel_y -= self.speed
        if keys[pygame.K_DOWN]:
            vel_y += self.speed

        self.x += vel_x
        self.y += vel_y

        self.x = max(0, min(self.x, app.WIDTH))
        self.y = max(0, min(self.y, app.HEIGHT))
        self.rect.center = (self.x, self.y)

        if vel_x != 0 or vel_y != 0:
            self.state = "run"
        else:
            self.state = "idle"

        if vel_x < 0:
            self.facing_left = True
        elif vel_x > 0:
            self.facing_left = False

        # Auto-aim with spacebar
        if keys[pygame.K_SPACE] and self.weapon_choice == "bullet" and self.shoot_timer == 0:
            nearest_enemy = self.find_nearest_enemy(self.enemies)
            if nearest_enemy:
                self.shoot_toward_enemy(nearest_enemy)
                self.shoot_timer = self.shoot_cooldown  # Reset the timer
                pygame.mixer.Sound(os.path.join("assets", "shoot.wav")).play()  # Play shooting sound
                
        # Control main sawblade with WASD
        if self.weapon_choice == "sawblade":
            dx, dy = 0, 0
            if keys[pygame.K_w]: dy -= 1
            if keys[pygame.K_s]: dy += 1
            if keys[pygame.K_a]: dx -= 1
            if keys[pygame.K_d]: dx += 1
            
            # Apply movement to the main sawblade (first in the list)
            if dx != 0 or dy != 0:
                self.sawblades[0].apply_movement(dx * self.speed * 1.2, dy * self.speed * 1.2)

    def find_nearest_enemy(self, enemies):
        if not enemies:
            return None
        nearest = None
        min_dist = float('inf')
        for enemy in enemies:
            dist = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
            if dist < min_dist:
                min_dist = dist
                nearest = enemy
        return nearest

    def update(self):
        # Decrease shoot timer
        if self.shoot_timer > 0:
            self.shoot_timer -= 1

        if self.weapon_choice == "bullet":
            for bullet in self.bullets:
                bullet.update()

                if bullet.x < 0 or bullet.y > app.HEIGHT or bullet.x < 0 or bullet.x > app.WIDTH:
                    self.bullets.remove(bullet)

        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            frames = self.animations[self.state]
            self.frame_index = (self.frame_index + 1) % len(frames)
            self.image = frames[self.frame_index]
            center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = center

        if self.weapon_choice == "sawblade":
            # Update main sawblade position
            main_blade = self.sawblades[0]
            main_blade.update()
            
            # Update orbiting sawblades
            for blade in self.sawblades[1:]:
                if blade.is_orbiting:
                    blade.set_parent_position(main_blade.x, main_blade.y)
                blade.update()
        elif self.weapon_choice == "lightning":
            self.lightning_staff.update(self.x, self.y, self.enemies)  # Just update position and enemies

    def add_orbiting_sawblade(self):
        if self.weapon_choice == "sawblade":
            num_orbiting = len(self.sawblades) - 1
            # Each new sawblade is offset by 2π/3 (120 degrees) from the previous
            offset = num_orbiting * (2 * math.pi / 3)
            # Orbit radius is number of current sawblades times sawblade size
            orbit_radius = len(self.sawblades) * self.sawblade.size
            new_blade = Sawblade(
                self.x, self.y, 
                size=self.sawblade.size,
                is_orbiting=True, 
                orbit_offset=offset,
                orbit_radius=orbit_radius
            )
            new_blade.damage = self.sawblade.damage
            self.sawblades.append(new_blade)

    def draw(self, surface):
        if self.facing_left:
            flipped_img = pygame.transform.flip(self.image, True, False)
            surface.blit(flipped_img, self.rect)
        else:
            surface.blit(self.image, self.rect)

        if self.weapon_choice == "bullet":
            for bullet in self.bullets:
                bullet.draw(surface)

        if self.weapon_choice == "sawblade":
            for blade in self.sawblades:
                blade.draw(surface)

        elif self.weapon_choice == "lightning":
            self.lightning_staff.draw(surface)

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)

    def shoot_toward_position(self, tx, ty):
        if self.shoot_timer >= self.shoot_cooldown:
            return

        dx = tx - self.x
        dy = ty - self.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist == 0:
            return

        vx = (dx / dist) * self.bullet_speed
        vy = (dy / dist) * self.bullet_speed

        angle_spread = self.bullet_spread  # Use instance variable instead of hardcoded value
        base_angle = math.atan2(vy, vx)
        mid = (self.bullet_count - 1) / 2

        for i in range(self.bullet_count):
            offset = i - mid
            spread_radians = math.radians(angle_spread * offset)
            angle = base_angle + spread_radians

            final_vx = math.cos(angle) * self.bullet_speed
            final_vy = math.sin(angle) * self.bullet_speed

            bullet = Bullet(self.x, self.y, final_vx, final_vy, self.bullet_size, 
                            damage=self.bullet_damage)
            self.bullets.append(bullet)
        self.shoot_timer = 0

    def shoot_toward_mouse(self, pos):
        if self.weapon_choice == "bullet":  # Ensure bullets are only fired when selected
            mx, my = pos  # denotes mouse
            self.shoot_toward_position(mx, my)

    def shoot_toward_enemy(self, enemy):
        self.shoot_toward_position(enemy.x, enemy.y)

    def add_xp(self, amount):
        self.xp += amount

