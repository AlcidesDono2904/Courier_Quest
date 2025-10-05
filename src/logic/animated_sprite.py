import pygame

class AnimatedSprite:
    """Clase base para objetos animados en el menú."""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def update(self, dt):
        """Actualiza la lógica del sprite. Debe ser implementado por las subclases."""
        pass

    def draw(self, screen):
        """Dibuja el sprite en la pantalla. Debe ser implementado por las subclases."""
        pass