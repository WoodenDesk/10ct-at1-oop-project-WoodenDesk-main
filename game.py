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

        self.screen = pygame.display.set_mode((app.WIDTH, app.HEIGHT))
        pygame.display.set_caption("Shooter")
        self.clock = pygame.time.Clock()

        self.assets = app.load_assets()

        font_path = os.path.join("assets", "PressStart2P.ttf")
        self.font_small = pygame.font.Font(font_path, 18)
        self.font_large = pygame.font.Font(font_path, 32)

        self.background = self.create_random_background(
            app.WIDTH, app.HEIGHT, self.assets["floor_tiles"]
        )

        self.running = True
        self.game_over = False

        self.enemy_spawn_time = 0
        self.enemy_spawn_interval = 60
        self.enemies_per_spawn = 1

        self.coins = []

        self.reset_game()

    def reset_game(self):
        self.player = Player(app.WIDTH // 2, app.HEIGHT // 2, self.assets)
        self.enemies = []
        self.coins = []
        self.game_over = False

    def create_random_background(self, width, height, floor_tiles):
        bg = pygame.Surface((width, height))

        tile_w = floor_tiles[0].get_width()
        tile_h = floor_tiles[0].get_height()

        for y in range(0, height, tile_h):
            for x in range(0, width, tile_w):
                tile = random.choice(floor_tiles)
                bg.blit(tile, (x, y))

        return bg

    def run(self):
        while self.running:
            self.clock.tick(app.FPS)
            self.handle_events()

            if not self.game_over:
                self.update()

            self.draw()

        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    nearest_enemy = self.find_nearest_enemy()
                    if nearest_enemy:
                        self.player.shoot_toward_enemy(nearest_enemy)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    self.player.shoot_toward_mouse(event.pos)

    def update(self):
        self.player.handle_input()
        self.player.update()

        self.check_player_enemy_collisions()
        self.check_bullet_enemy_collisions()

        for enemy in self.enemies:
            enemy.update(self.player)

        for coin in self.coins:
            coin.update()

        self.spawn_enemies()

        if self.player.health <= 0:
            self.game_over = True

    def draw(self):
        self.screen.blit(self.background, (0, 0))

        for coin in self.coins:
            coin.draw(self.screen)

        if not self.game_over:
            self.player.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        hp = max(0, min(self.player.health, 5))
        health_img = self.assets["health"][hp]
        self.screen.blit(health_img, (10, 10))

        xp_text = self.font_small.render(f"XP: {self.player.xp}", True, (255, 255, 255))
        self.screen.blit(xp_text, (100, 10))

        if self.game_over:
            self.draw_game_over_screen()

        pygame.display.flip()

    def spawn_enemies(self):
        self.enemy_spawn_time += 1
        if self.enemy_spawn_time >= self.enemy_spawn_interval:
            self.enemy_spawn_time = 0

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
                new_enemy = Enemy(x, y, enemy_type, self.assets["enemies"][enemy_type])
                self.enemies.append(new_enemy)

    def check_bullet_enemy_collisions(self):
        collided = False
        for bullet in self.player.bullets:
            for enemy in self.enemies:
                if enemy.rect.colliderect(bullet.rect):
                    self.enemies.remove(enemy)
                    self.player.bullets.remove(bullet)
                    self.player.add_xp(10)
                    collided = True
                    break
            if collided:
                break

    def check_player_enemy_collisions(self):
        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):
                self.player.take_damage(1)
                self.player.xp -= 5
                self.enemies.remove(enemy)

    def draw_game_over_screen(self):
        game_over_surf = self.font_large.render("GAME OVER", True, (255, 0, 0))
        game_over_rect = game_over_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 2 - 50))
        self.screen.blit(game_over_surf, game_over_rect)

        prompt_surf = self.font_small.render("Press R to Play Again or Esc to Quit", True, (255, 255, 255))
        prompt_rect = prompt_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 2 + 20))
        self.screen.blit(prompt_surf, prompt_rect)

    def find_nearest_enemy(self):
        min_dist = float("inf")
        nearest_enemy = None

        px, py = self.player.x, self.player.y

        for enemy in self.enemies:
            ex, ey = enemy.x, enemy.y
            dist = math.sqrt((ex - px) ** 2 + (ey - py) ** 2)

            if dist < min_dist:
                min_dist = dist
                nearest_enemy = enemy

        return nearest_enemy
    def check_bullet_enemy_collisions(self):
        for bullet in self.player.bullets:
            for enemy in self.enemies:
               if bullet.rect.colliderect(enemy.rect):
                    self.player.bullets.remove(bullet)
                    new_coin = Coin(enemy.x, enemy.y)
                    self.coins.append(new_coin)
                    self.enemies.remove(enemy)

    def check_player_coin_collisions(self):
        coins_collected = []
        for coin in self.coins:
            if coin.rect.colliderect(self.player.rect):
                coins_collected.append(coin)
                self.player.add_xp(1)

        for c in coins_collected:
             if c in self.coins:
                self.coins.remove(c)