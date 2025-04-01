# bullet.py
import app

class Bullet:
    def __init__(self, x, y, vx, vy, size, damage=6):
        # Position and movement
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        
        # Properties
        self.size = size
        self.damage = damage

        # Visual setup
        self.image = app.pygame.Surface((size, size), app.pygame.SRCALPHA)
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        # Move bullet
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x, self.y)
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)