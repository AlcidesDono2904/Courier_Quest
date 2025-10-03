import pygame
import math
from src.logic.animated_sprite import AnimatedSprite

class AnimatedCyclist(AnimatedSprite):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.bounce_offset = 0
        self.wheel_rotation = 0
        self.backpack_swing = 0

    def update(self, dt):
        self.bounce_offset = math.sin(pygame.time.get_ticks() * 0.005) * 3
        self.wheel_rotation += 180 * dt
        if self.wheel_rotation >= 360:
            self.wheel_rotation = 0
        self.backpack_swing = math.sin(pygame.time.get_ticks() * 0.003) * 2

    def draw(self, screen):
        base_y = self.y + self.bounce_offset

        wheel_back_pos = (self.x - 15, base_y + 20)
        wheel_front_pos = (self.x + 15, base_y + 20)

        pygame.draw.circle(screen, (50, 50, 50), wheel_back_pos, 12)
        pygame.draw.circle(screen, (80, 80, 80), wheel_back_pos, 10)
        pygame.draw.circle(screen, (50, 50, 50), wheel_front_pos, 12)
        pygame.draw.circle(screen, (80, 80, 80), wheel_front_pos, 10)

        pygame.draw.line(screen, (255, 107, 53), wheel_back_pos, (self.x, base_y), 3)
        pygame.draw.line(screen, (255, 107, 53), (self.x, base_y), wheel_front_pos, 3)
        pygame.draw.line(screen, (255, 107, 53), (self.x - 8, base_y - 15), (self.x, base_y), 3)

        pygame.draw.ellipse(screen, (50, 50, 50), (self.x - 18, base_y - 18, 15, 6))
        pygame.draw.ellipse(screen, (255, 215, 0), (self.x - 12, base_y - 30, 25, 20))
        pygame.draw.circle(screen, (251, 188, 180), (self.x, base_y - 45), 10)
        pygame.draw.ellipse(screen, (255, 69, 0), (self.x - 11, base_y - 55, 22, 15))

        backpack_x = self.x - 20 + self.backpack_swing
        pygame.draw.rect(screen, (139, 0, 0), (backpack_x, base_y - 35, 15, 20), border_radius=3)