import pygame
import app  # Contains global settings like WIDTH, HEIGHT, PLAYER_SPEED, etc.

class Player:
    def __init__(self, x, y, assets):
        """Initialize the player with position and image assets."""
        # TODO: 1. Store the player's position
        # e.g. self.x = x, self.y = y

        # TODO: 2. Load the player's image from assets
        # For example: self.image = assets["player_idle"][0]
        # (or some default image key in assets)

        self.speed = app.PLAYER_SPEED
        self.animations = assets["player"]
        self.state = "idle"
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 8

        # TODO: 3. Create a collision rectangle (self.rect) 
        # For example: 
        # self.rect = self.image.get_rect(center=(self.x, self.y))

        # TODO: 4. Add player health 

    def handle_input(self):
        """Check and respond to keyboard/mouse input."""

        # TODO: 1. Capture Keyboard Input

        # velocity in X, Y direction
        vel_x, vel_y = 0, 0

        # TODO: 2. Adjust player position with keys pressed, updating the player position to vel_x and vel_y

        # TODO: 3. Clamp player position to screen bounds

        # animation state
        if vel_x != 0 or vel_y != 0:
            self.state = "run"
        else:
            self.state = "idle"

        # direction
        if vel_x < 0:
            self.facing_left = True
        elif vel_x > 0:
            self.facing_left = False
        pass

    def update(self):
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            frames = self.animations[self.state]
            self.frame_index = (self.frame_index + 1) % len(frames)
            self.image = frames[self.frame_index]
            center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = center
        pass

    def draw(self, surface):
        """Draw the player on the screen."""
        # TODO: Draw the image to the given surface at self.rect
        # For example: surface.blit(self.image, self.rect)
        pass

    def take_damage(self, amount):
        """Reduce the player's health by a given amount, not going below zero."""
        # TODO: self.health = max(0, self.health - amount)
        pass