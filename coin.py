import pygame

class Coin:
    def __init__(self, x, y):
        # Setup coin visual and position
        self.x, self.y = x, y
        self.image = pygame.Surface((15, 15), pygame.SRCALPHA)
        self.image.fill((255, 215, 0))  # Gold color
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self, surface):
        surface.blit(self.image, self.rect)