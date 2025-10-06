import pygame
import random
from src.logic.animated_sprite import AnimatedSprite

class AnimatedWindow(AnimatedSprite):
    """Se encarga de la lógica y el dibujo de las ventanas animadas en el menú principal."""
    def __init__(self, x, y, width, height):
        super().__init__(x, y)
        self.width = width
        self.height = height
        self.brightness = random.uniform(0.5, 1.0)
        self.pulse_speed = random.uniform(0.01, 0.03)
        self.color_type = random.choice(['warm', 'cool'])

    def update(self, dt):
        self.brightness += self.pulse_speed
        if self.brightness > 1.0 or self.brightness < 0.4:
            self.pulse_speed *= -1

    def draw(self, screen):
        if self.color_type == 'warm':
            color = (min(255, max(0, int(255 * self.brightness))),
                     min(255, max(0, int(220 * self.brightness))),
                     min(255, max(0, int(120 * self.brightness))))
        else:
            color = (min(255, max(0, int(120 * self.brightness))),
                     min(255, max(0, int(180 * self.brightness))),
                     min(255, max(0, int(255 * self.brightness))))

        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))

        glow_rect = pygame.Rect(self.x - 1, self.y - 1, self.width + 2, self.height + 2)
        pygame.draw.rect(screen, color, glow_rect, 1)