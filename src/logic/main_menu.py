import pygame
from src.logic.button import Button
import os

class MainMenu:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        resources_dir = os.path.join(current_dir, "resources")


        self.font_title = pygame.font.Font(None, 64) 
        self.font_subtitle = pygame.font.Font(None, 24) 
        self.font_footer = pygame.font.Font(None, 16) 

        self.background_image = pygame.image.load(os.path.join(resources_dir, "images", "menu_background.png")).convert()
        self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))
        
        # --- Colores ---
        self.title_color = (0, 255, 100) # Verde neón
        self.subtitle_color = (200, 200, 200) # Gris claro
        self.text_color = (255, 255, 255) # Blanco
        self.button_base_color = (40, 40, 60) # Azul oscuro
        self.button_hover_color = (70, 70, 90) # Azul más claro al pasar el ratón
        self.button_border_color = (0, 255, 100) # Verde neón para el borde
        self.exit_button_color = (150, 0, 0) # Rojo para salir
        self.exit_button_hover_color = (200, 0, 0) # Rojo más brillante

        # --- Creación de Botones ---
        button_width = 300
        button_height = 70
        spacing = 25
        start_y = self.height // 2 - button_height * 2 - spacing 

        self.buttons = {
            "new_game": Button(
                "NUEVA PARTIDA", 
                (self.width - button_width) // 2, start_y, 
                button_width, button_height, 
                self.button_base_color, self.button_hover_color, self.text_color, self.button_border_color,
               
            ),
            "load_game": Button(
                "CARGAR PARTIDA", 
                (self.width - button_width) // 2, start_y + button_height + spacing, 
                button_width, button_height, 
                self.button_base_color, self.button_hover_color, self.text_color, self.button_border_color,
                
            ),
            "high_scores": Button(
                "RÉCORDS", 
                (self.width - button_width) // 2, start_y + (button_height + spacing) * 2, 
                button_width, button_height, 
                self.button_base_color, self.button_hover_color, self.text_color, self.button_border_color,
                
            ),
            "exit": Button(
                "SALIR", 
                (self.width - button_width) // 2, start_y + (button_height + spacing) * 3, 
                button_width, button_height, 
                self.exit_button_color, self.exit_button_hover_color, self.text_color, (255, 255, 255),
                
            )
        }

    def draw(self):
        # Dibujar la imagen de fondo primero
        self.screen.blit(self.background_image, (0, 0))
        
        # Renderizar el título del juego
        title_surface = self.font_title.render("COURIER QUEST", True, self.title_color)
        title_rect = title_surface.get_rect(center=(self.width // 2, self.height // 4))
        self.screen.blit(title_surface, title_rect)

        # Subtítulo (opcional, como en tu imagen)
        subtitle_surface = self.font_subtitle.render("URBAN DELIVERY CHALLENGE", True, self.subtitle_color)
        subtitle_rect = subtitle_surface.get_rect(center=(self.width // 2, self.height // 4 + 70)) 
        self.screen.blit(subtitle_surface, subtitle_rect)
        
        # Dibujar botones
        for button in self.buttons.values():
            button.draw(self.screen)

        # Pie de página (opcional, como en tu imagen)
        footer_text = "EIF-207 Estructuras de Datos • Proyecto 1 • II Ciclo 2025"
        footer_surface = self.font_footer.render(footer_text, True, self.subtitle_color)
        footer_rect = footer_surface.get_rect(midbottom=(self.width // 2, self.height - 20))
        self.screen.blit(footer_surface, footer_rect)

        pygame.display.flip()

    def handle_event(self, event):
        for button_name, button in self.buttons.items():
            if button.handle_event(event):
                if button_name == "new_game":
                    return "start_game"
                elif button_name == "load_game":
                    return "load_game"
                elif button_name == "high_scores":
                    return "high_scores"
                elif button_name == "exit":
                    return "exit"
        return None