# bullet.py
import app

class Bullet:
    def __init__(self, x, y, vx, vy, size, bounces=False, damage=6):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.bounces = bounces
        self.damage = damage

        self.image = app.pygame.Surface((self.size, self.size), app.pygame.SRCALPHA)
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self):
        self.x += self.vx
        self.y += self.vy
        
        if self.bounces:
            if self.x < 0 or self.x > app.WIDTH:
                self.vx *= -1
            if self.y < 0 or self.y > app.HEIGHT:
                self.vy *= -1
            self.x = max(0, min(self.x, app.WIDTH))
            self.y = max(0, min(self.y, app.HEIGHT))
            
        self.rect.center = (self.x, self.y)
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)