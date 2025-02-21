# game.py
import pygame
import random
import os

import app

class Game:
    def __init__(self):
        pygame.init()  # Initialize Pygame
        self.screen = pygame.display.set_mode((app.WIDTH, app.HEIGHT)) # intialize  the screen size / window
        pygame.display.set_caption("Shooter") #name the window
        self.clock = pygame.time.Clock() # make the clock

        self.assets = app.load_assets() # load the assets 

        font_path = os.path.join("assets", "PressStart2P.ttf") # load the font file
        self.font_small = pygame.font.Font(font_path, 18) # select the font from a list of font
        self.font_large = pygame.font.Font(font_path, 32)# select the font from a list of fonts but for a larger font 

        self.background = self.create_random_background( # create the background of the game from assets
        app.WIDTH, app.HEIGHT, self.assets["floor_tiles"] # the asset is floor_tiles
        ) 

        self.running = True  # set the game state to running
        self.game_over = False # set the game over state to be false
        

        self.reset_game() # resets the game 
        
    def reset_game(self): # defines the reset fame variable
        self.game_over = False # set game over to false so it is not game over 

    def create_random_background(self, width, height, floor_tiles): 
        bg = pygame.Surface((width, height)) # setting the background / surface
        tile_w = floor_tiles[0].get_width() # set the width of the tiles
        tile_h = floor_tiles[0].get_height() # set the height of the tiles

        for y in range(0, height, tile_h):
            for x in range(0, width, tile_w):
                tile = random.choice(floor_tiles)
                bg.blit(tile, (x, y))  # blit puts an asset on the screen

        return bg

    def run(self):
        while self.running:
            self.clock.tick(60)    # Control the game speed: at most FPS frames per second.
            self.handle_events()    # Check for user input or other events.
            self.update() # update the game if it isn't over 
            self.draw()  # display the events on the screen 
        pygame.quit() # close the game when you quit    

    def handle_events(self):
        """Process user input (keyboard, mouse, quitting)."""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        """Update the game state (player, enemies, etc.)."""
        pass

    def draw(self):
        """Render all game elements to the screen."""
        self.screen.blit(self.background, (0, 0))  # Blit the background to the screen

        # TODO: Draw player, enemies, UI elements

        # Refresh the screen
        pygame.display.flip()