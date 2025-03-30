# game.py
import pygame
import random
import os

import app

from player import Player
from enemy import Enemy
from coin import Coin
import math

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()  # Initialize the mixer for sound
        self.screen = pygame.display.set_mode((app.WIDTH, app.HEIGHT))
        pygame.display.set_caption("Shooter")
        self.clock = pygame.time.Clock()
        self.in_level_up_menu = False
        self.upgrade_options = []

        self.assets = app.load_assets()

        font_path = os.path.join("assets", "PressStart2P.ttf")
        self.font_small = pygame.font.Font(font_path, 18)
        self.font_large = pygame.font.Font(font_path, 32)

        self.background = self.create_random_background(
            app.WIDTH, app.HEIGHT, self.assets["floor_tiles"]
        )

        self.running = True
        self.game_over = False

        self.enemies = []  # List to store enemies
        self.enemy_spawn_timer = 0
        self.enemy_spawn_interval = 30 
        self.enemies_per_spawn = 2

        self.coins = []
        self.weapon_choice = None  # Initialize weapon choice before calling reset_game
        self.reset_game()

        # Load sound effects
        self.sounds = {
            "shoot": pygame.mixer.Sound(os.path.join("assets", "shoot.wav")),
            "enemy_death": pygame.mixer.Sound(os.path.join("assets", "enemy_death.wav")),
            "level_up": pygame.mixer.Sound(os.path.join("assets", "level_up.wav")),
            "game_over": pygame.mixer.Sound(os.path.join("assets", "death.wav")), 
        }
        self.sounds["shoot"].set_volume(0.5)  # Adjust volume (optional)
        self.sounds["enemy_death"].set_volume(0.5)
        self.sounds["level_up"].set_volume(0.7)
        self.sounds["game_over"].set_volume(0.7)  
        self.weapon_choice = None  # Store the player's weapon choice

    def reset_game(self):
        if self.game_over:  # If resetting after death, clear weapon choice
            self.weapon_choice = None
        self.player = Player(app.WIDTH // 2, app.HEIGHT // 2, self.assets, self.weapon_choice)  
        self.enemies = [] 
        self.enemy_spawn_timer = 0
        self.enemies_per_spawn = 1
        self.coins = []
        self.game_over = False

    def create_random_background(self, width, height, floor_tiles): 
        bg = pygame.Surface((width, height))  
        tile_w = floor_tiles[0].get_width()
        tile_h = floor_tiles[0].get_height()  
        tile_w = floor_tiles[0].get_width()
        tile_h = floor_tiles[0].get_height()

        for y in range(0, height, tile_h):
            for x in range(0, width, tile_w):
                tile = random.choice(floor_tiles)
                bg.blit(tile, (x, y))

        return bg

    def run(self):
        while self.running:
            if self.weapon_choice is None:
                self.show_weapon_selection_screen()
            else:
                self.clock.tick(app.FPS)
                self.handle_events()

                if not self.game_over and not self.in_level_up_menu:
                    self.update()

                self.draw()

        pygame.quit()

    def show_weapon_selection_screen(self):
        while self.weapon_choice is None:  # Keep showing screen until weapon is chosen
            self.screen.fill((0, 0, 0))

            # Title
            title_surf = self.font_large.render("Choose Your Weapon!", True, (255, 255, 0))
            title_rect = title_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 3 - 50))
            self.screen.blit(title_surf, title_rect)

            # Options with updated descriptions
            bullet_text = "1. Bullet - Shoot with mouse/spacebar"
            sawblade_text = "2. Sawblade - Control with WASD"
            lightning_text = "3. Lightning Staff - Chain lightning between enemies"
            bullet_surf = self.font_small.render(bullet_text, True, (255, 255, 255))
            sawblade_surf = self.font_small.render(sawblade_text, True, (255, 255, 255))
            lightning_surf = self.font_small.render(lightning_text, True, (255, 255, 255))
            bullet_rect = bullet_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 2 - 40))
            sawblade_rect = sawblade_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 2))
            lightning_rect = lightning_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 2 + 40))
            self.screen.blit(bullet_surf, bullet_rect)
            self.screen.blit(sawblade_surf, sawblade_rect)
            self.screen.blit(lightning_surf, lightning_rect)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.weapon_choice = "bullet"
                    elif event.key == pygame.K_2:
                        self.weapon_choice = "sawblade"
                    elif event.key == pygame.K_3:
                        self.weapon_choice = "lightning"
                        
            self.clock.tick(30)  # Limit FPS for weapon selection screen
            
        self.reset_game()  # Reset game with the chosen weapon

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                elif self.in_level_up_menu:  # only runs in the upgrade menu
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                        index = event.key - pygame.K_1  
                        if 0 <= index < len(self.upgrade_options):
                            upgrade = self.upgrade_options[index]
                            self.apply_upgrade(self.player, upgrade)
                            self.in_level_up_menu = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.weapon_choice == "bullet" and event.button == 1:  # Left mouse button
                    self.player.shoot_toward_mouse(event.pos)  # Shoot bullets
                    self.sounds["shoot"].play()

            
    def spawn_enemies(self):
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer >= self.enemy_spawn_interval:
            self.enemy_spawn_timer = 0

            for _ in range(self.enemies_per_spawn):
                side = random.choice(["top", "bottom", "left", "right"])
                if side == "top":
                    x = random.randint(0, app.WIDTH)
                    y = -app.SPAWN_MARGIN
                elif side == "bottom":
                    x = random.randint(0, app.WIDTH)
                    y = app.HEIGHT + app.SPAWN_MARGIN
                elif side == "left":
                    x = -app.SPAWN_MARGIN
                    y = random.randint(0, app.HEIGHT)
                else:
                    x = app.WIDTH + app.SPAWN_MARGIN
                    y = random.randint(0, app.HEIGHT)

                enemy_type = random.choice(list(self.assets["enemies"].keys()))
                print(f"Enemy type: {enemy_type}")
                enemy = Enemy(x, y, enemy_type, self.assets["enemies"], level=self.player.level)
                self.enemies.append(enemy)
            
    def update(self):
        self.player.enemies = self.enemies
        
        self.player.handle_input()
        self.player.update()

        # Move enemies to a list to be removed to avoid modifying list while iterating
        enemies_to_remove = []
        
        if self.weapon_choice == "sawblade":
            for sawblade in self.player.sawblades:
                collided_enemies = sawblade.check_collision(self.enemies)
                enemies_to_remove.extend(collided_enemies)
        elif self.weapon_choice == "lightning":
            killed_enemies = self.player.lightning_staff.check_collision(self.enemies)
            enemies_to_remove.extend(killed_enemies)
        
        # Remove dead enemies and spawn coins
        for enemy in enemies_to_remove:
            if enemy in self.enemies:  # Check if enemy still exists
                self.enemies.remove(enemy)
                new_coin = Coin(enemy.x, enemy.y)
                self.coins.append(new_coin)
                self.sounds["enemy_death"].play()

        for enemy in self.enemies:
            enemy.update(self.player)

        self.check_player_enemy_collisions()
        self.check_bullet_enemy_collisions()
        self.check_player_coin_collisions()

        if self.player.health <= 0:
            self.game_over = True
            return

        self.spawn_enemies()
        self.check_for_level_up()  # Call the method here

    def draw(self):
        self.screen.blit(self.background, (0, 0))

        for coin in self.coins:
            coin.draw(self.screen)

        if not self.game_over:
            self.player.draw(self.screen)
            if self.weapon_choice == "sawblade" and self.player.sawblade:
                self.player.sawblade.draw(self.screen)  # Draw the sawblade only if selected

        for enemy in self.enemies:
            enemy.draw(self.screen)

        if self.in_level_up_menu:
            self.draw_upgrade_menu()

        hp = max(0, min(self.player.health, 20))
        health_img = self.assets["health"][hp]
        self.screen.blit(health_img, (10, 10))

        xp_text_surf = self.font_small.render(f"XP: {self.player.xp}", True, (255, 255, 255))
        self.screen.blit(xp_text_surf, (10, 70))
        next_level_xp = self.player.level * self.player.level * 5
        xp_to_next = max(0, next_level_xp - self.player.xp)
        xp_next_surf = self.font_small.render(f"Next Lvl XP: {xp_to_next}", True, (255, 255, 255))
        self.screen.blit(xp_next_surf, (10, 100))

        if self.game_over:
            self.draw_game_over_screen()

        pygame.display.flip()

    def check_player_enemy_collisions(self):
        collided = False
        for enemy in self.enemies:
            if enemy.rect.colliderect(self.player.rect):
                collided = True
                break

        if collided:
            self.player.take_damage(1)
            if self.player.health <= 0:
                self.sounds["game_over"].play()  # Play game over sound
            px, py = self.player.x, self.player.y
            for enemy in self.enemies:
                enemy.set_knockback(px, py, app.PUSHBACK_DISTANCE)

    def draw_game_over_screen(self):
        # Dark overlay
        overlay = pygame.Surface((app.WIDTH, app.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Game Over text
        game_over_surf = self.font_large.render("GAME OVER!", True, (255, 0, 0))
        game_over_rect = game_over_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 2 - 50))
        self.screen.blit(game_over_surf, game_over_rect)

        # Updated prompt to include weapon selection
        prompt_surf = self.font_small.render("Press R to Choose New Weapon or ESC to Quit", True, (255, 255, 255))
        prompt_rect = prompt_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 2 + 20))
        self.screen.blit(prompt_surf, prompt_rect)

    def find_nearest_enemy(self):
        if not self.enemies:
            return None
        nearest = None
        min_dist = float('inf')
        px, py = self.player.x, self.player.y
        for enemy in self.enemies:
            dist = math.sqrt((enemy.x - px)**2 + (enemy.y - py)**2)
            if dist < min_dist:
                min_dist = dist
                nearest = enemy
        return nearest

    def check_bullet_enemy_collisions(self):
        for bullet in self.player.bullets[:]:
            for enemy in self.enemies[:]:  # Create a copy to safely modify
                if bullet.rect.colliderect(enemy.rect):
                    if enemy.take_damage(bullet.damage):  # Enemy dies
                        self.enemies.remove(enemy)
                        new_coin = Coin(enemy.x, enemy.y)
                        self.coins.append(new_coin)
                        self.sounds["enemy_death"].play()
                    if bullet in self.player.bullets and not bullet.bounces:
                        self.player.bullets.remove(bullet)
                    break

    def check_player_coin_collisions(self):
        coins_collected = []
        for coin in self.coins:
            if coin.rect.colliderect(self.player.rect):
                coins_collected.append(coin)
                self.player.add_xp(1)

        for c in coins_collected:
            if c in self.coins:
                self.coins.remove(c)

    def pick_random_upgrades(self, num):
        if self.weapon_choice == "bullet":
            possible_upgrades = [
                {"name": "Bigger Bullet", "desc": "Bullet size +5"},
                {"name": "Faster Bullet", "desc": "Bullet speed +2"},
                {"name": "Extra Bullet", "desc": "Fire additional bullet"},
                {"name": "Shorter Cooldown", "desc": "Shoot more frequently"},
                {"name": "Wider Spread", "desc": "Increase bullet spread"},
                {"name": "Tighter Spread", "desc": "Decrease bullet spread"},
                {"name": "Rapid Fire", "desc": "Much faster shooting -40% damage"},
                {"name": "Heavy Bullets", "desc": "Double damage, slower speed"},
                {"name": "Bouncy Bullets", "desc": "Bullets bounce off screen edges"},
                {"name": "Triple Shot", "desc": "Fire three spread shots"},
            ]
        elif self.weapon_choice == "sawblade":
            possible_upgrades = [
                {"name": "Larger Sawblade", "desc": "Increase sawblade size"},
                {"name": "Sharper Sawblade", "desc": "Increase damage +2"},
                {"name": "Orbit Sawblade", "desc": "Add orbiting sawblade"},
                {"name": "Faster Spin", "desc": "Increase rotation speed"},
                {"name": "Quicker Movement", "desc": "Better sawblade control"},
                {"name": "Wider Orbit", "desc": "Increase orbit radius"},
                {"name": "Tighter Orbit", "desc": "Decrease orbit radius"},
                {"name": "Faster Orbit", "desc": "Orbital speed +20%"},
            ]
        elif self.weapon_choice == "lightning":
            possible_upgrades = [
                {"name": "Chain Lightning", "desc": "Lightning jumps to +1 enemy"},
                {"name": "Lightning Range", "desc": "Increase chain distance"},
                {"name": "Lightning Power", "desc": "Increase damage +2"},
                {"name": "Quick Zap", "desc": "Reduce cooldown"},
                {"name": "Wide Arc", "desc": "Increase targeting range"},
                {"name": "Thunder Strike", "desc": "Double damage to first target"},
            ]
        return random.sample(possible_upgrades, k=min(num, len(possible_upgrades)))

    def apply_upgrade(self, player, upgrade):
        name = upgrade["name"]
        if self.weapon_choice == "bullet":
            if name == "Bigger Bullet":
                player.bullet_size += 5
            elif name == "Faster Bullet":
                player.bullet_speed += 2
            elif name == "Extra Bullet":
                player.bullet_count += 1
            elif name == "Shorter Cooldown":
                player.shoot_cooldown = max(1, int(player.shoot_cooldown * 0.8))
            elif name == "Wider Spread":
                player.bullet_spread = min(30, player.bullet_spread + 5)
            elif name == "Tighter Spread":
                player.bullet_spread = max(5, player.bullet_spread - 5)
            elif name == "Rapid Fire":
                player.shoot_cooldown = max(1, int(player.shoot_cooldown * 0.6))
                player.bullet_damage *= 0.6
            elif name == "Heavy Bullets":
                player.bullet_damage *= 2
                player.bullet_speed *= 0.8
            elif name == "Triple Shot":
                player.bullet_count = max(3, player.bullet_count)
                player.bullet_spread = max(20, player.bullet_spread)
        elif self.weapon_choice == "sawblade":
            if name == "Larger Sawblade":
                for blade in player.sawblades:
                    blade.size += 10
                    blade.original_image = pygame.transform.scale(
                        blade.original_image, 
                        (blade.size, blade.size)
                    )
            elif name == "Sharper Sawblade":
                for blade in player.sawblades:
                    blade.damage += 2
            elif name == "Orbit Sawblade":
                player.add_orbiting_sawblade()
            elif name == "Faster Spin":
                for blade in player.sawblades:
                    blade.rotation_speed = min(30, blade.rotation_speed + 5)
            elif name == "Quicker Movement":
                for blade in player.sawblades:
                    blade.acceleration *= 1.2
                    blade.friction = min(0.99, blade.friction + 0.01)
            elif name == "Wider Orbit":
                for blade in player.sawblades:
                    if blade.is_orbiting:
                        blade.orbit_radius *= 1.2
            elif name == "Tighter Orbit":
                for blade in player.sawblades:
                    if blade.is_orbiting:
                        blade.orbit_radius *= 0.8
            elif name == "Faster Orbit":
                for blade in player.sawblades:
                    if blade.is_orbiting:
                        blade.orbit_speed *= 1.2
        elif self.weapon_choice == "lightning":
            if name == "Chain Lightning":
                player.lightning_staff.chain_count += 1
            elif name == "Lightning Range":
                player.lightning_staff.chain_range += 50
            elif name == "Lightning Power":
                player.lightning_staff.damage += 2
            elif name == "Quick Zap":
                player.lightning_staff.zap_cooldown = max(10, player.lightning_staff.zap_cooldown - 5)
            elif name == "Thunder Strike":
                player.lightning_staff.damage *= 2

    def draw_upgrade_menu(self):
        # Dark overlay behind the menu
        overlay = pygame.Surface((app.WIDTH, app.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Title
        title_surf = self.font_large.render("Choose an Upgrade!", True, (255, 255, 0))
        title_rect = title_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 3 - 50))
        self.screen.blit(title_surf, title_rect)

        # Options
        for i, upgrade in enumerate(self.upgrade_options):
            text_str = f"{i+1}. {upgrade['name']} - {upgrade['desc']}"
            option_surf = self.font_small.render(text_str, True, (255, 255, 255))
            line_y = app.HEIGHT // 3 + i * 40
            option_rect = option_surf.get_rect(center=(app.WIDTH // 2, line_y))
            self.screen.blit(option_surf, option_rect)

    def check_for_level_up(self):
        xp_needed = self.player.level * self.player.level * 5
        if self.player.xp >= xp_needed:
            # Leveled up
            self.player.level += 1
            self.in_level_up_menu = True
            self.upgrade_options = self.pick_random_upgrades(3)
            # Increase enemy spawns each time we level up
            self.enemies_per_spawn += 1
            self.sounds["level_up"].play()  # Play level-up sound

