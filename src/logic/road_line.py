import pygame
import math
import random
import os
from src.logic.button import Button

class RoadLine:
    """Se encarga de la lógica y el dibujo de las líneas de la carretera en el menú principal."""
    def __init__(self, y):
        self.x = -60
        self.y = y
        self.width = 60
        self.height = 4
        self.speed = 200  
        
    def update(self, dt, screen_width):
        self.x += self.speed * dt
        if self.x > screen_width:
            self.x = -self.width
    
    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 0), (self.x, self.y, self.width, self.height))