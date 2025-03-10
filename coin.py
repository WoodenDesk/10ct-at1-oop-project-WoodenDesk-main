import pygame

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = pygame.Surface((15, 15), pygame.SRCALPHA)
        self.image.fill((255, 215, 0))  # Gold color
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def draw(self, surface):
        surface.blit(self.image, self.rect)