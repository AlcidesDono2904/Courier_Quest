import pygame
import random
from src.logic.animated_sprite import AnimatedSprite

class AnimatedCloud(AnimatedSprite):
    def __init__(self, x, y, size, speed):
        super().__init__(x, y)
        self.size = size
        self.speed = speed
        self.alpha = random.randint(100, 200)

    def update(self, dt, screen_width):
        self.x += self.speed * dt
        if self.x > screen_width + 100:
            self.x = -100
            self.y = random.randint(50, 200)

    def draw(self, screen):
        cloud_surface = pygame.Surface((self.size * 2, self.size), pygame.SRCALPHA)

        pygame.draw.circle(cloud_surface, (255, 255, 255, self.alpha), (self.size//2, self.size//2), self.size//3)
        pygame.draw.circle(cloud_surface, (255, 255, 255, self.alpha), (self.size//2 + 15, self.size//2), self.size//4)
        pygame.draw.circle(cloud_surface, (255, 255, 255, self.alpha), (self.size//2 - 15, self.size//2), self.size//4)
        pygame.draw.circle(cloud_surface, (255, 255, 255, self.alpha), (self.size//2, self.size//2 - 10), self.size//5)

        screen.blit(cloud_surface, (self.x, self.y))