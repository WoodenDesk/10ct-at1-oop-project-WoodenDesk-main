import pygame
import app  # Contains global settings like WIDTH, HEIGHT, PLAYER_SPEED, etc.

class Player:
    def __init__(self, x, y, assets):
        self.x = x
        self.y = y
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
 

 

    def handle_input(self):
        """Check and respond to keyboard/mouse input."""

        # TODO: 1. Capture Keyboard Input
        keys = pygame.key.get_pressed() #Get the key press event
        # velocity in X, Y direction
        vel_x, vel_y = 0, 0

        # TODO: 2. Adjust player position with keys pressed, updating the player position to vel_x and vel_y
        if keys[pygame.K_LEFT]:
            # Move character left
            vel_x -= self.speed
        if keys[pygame.K_RIGHT]:
            vel_x += self.speed
        if keys[pygame.K_UP]:
            vel_y -= self.speed
        if keys[pygame.K_DOWN]:
            vel_y += self.speed

        # TODO: 3. Clamp player position to screen bounds
        self.x = min(max(self.x + vel_x, 0 ),app.WIDTH) #set the minimum of the players x axis to their current x position + 
        self.y = min(max(self.y + vel_y, 0 ),app.HEIGHT)# set the players minimum y position to their current y position + their velocity 
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


    def update(self):
        self.update_animation()
    def update_animation(self):
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            frames = self.animations[self.state]
            self.frame_index = (self.frame_index + 1) % len(frames)
            self.image = frames[self.frame_index]
            center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = center


    def draw(self, surface):
        """Draw the player on the screen."""
        # TODO: Draw the image to the given surface at self.rect
        # For example: surface.blit(self.image, self.rect)
        pass

    def take_damage(self, amount):
        """Reduce the player's health by a given amount, not going below zero."""
        # TODO: self.health = max(0, self.health - amount)
        pass