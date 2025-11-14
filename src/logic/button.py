import pygame
import os

class Button:
    """Clase para crear botones interactivos en la interfaz gráfica."""
    def __init__(self, text, x, y, width, height, base_color, hover_color, text_color, border_color=(255, 255, 255), border_width=2, font_size=36, font_path=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_color = border_color
        self.border_width = border_width

        self.font = pygame.font.Font(font_path, font_size) 

        self.current_color = self.base_color
        self.is_hovered = False

    def draw(self, screen):
       
        pygame.draw.rect(screen, self.border_color, self.rect, self.border_width, border_radius=10)
        
        pygame.draw.rect(screen, self.current_color, self.rect.inflate(-self.border_width*2, -self.border_width*2), border_radius=8)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                if not self.is_hovered:
                    self.current_color = self.hover_color
                    self.is_hovered = True
            else:
                if self.is_hovered:
                    self.current_color = self.base_color
                    self.is_hovered = False
        
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_hovered:
            return True 
        return False