import pygame
import math
import random
import os
from src.logic.button import Button
from src.logic.animated_cyclist import AnimatedCyclist
from src.logic.animated_cloud import AnimatedCloud
from src.logic.animated_window import AnimatedWindow
from src.logic.road_line import RoadLine

class MainMenu:
    """Clase que maneja el menú principal del juego, incluyendo la lógica y el dibujo de todos sus elementos."""
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        
        self.load_background()
         
        self.font_title = pygame.font.Font(None, 72)
        self.font_subtitle = pygame.font.Font(None, 28)
        self.font_footer = pygame.font.Font(None, 18)
        
        # Colores
        self.title_color = (0, 255, 136)  # Verde neón
        self.subtitle_color = (100, 181, 246)  # Azul claro
        self.text_color = (255, 255, 255)
        
        # Efectos de título
        self.title_pulse = 0
        
        # Elementos animados
        self.cyclist = AnimatedCyclist(width * 0.25, height - 150)
        self.clouds = [
            AnimatedCloud(-100, 80, 60, 30),
            AnimatedCloud(-200, 120, 80, 25),
            AnimatedCloud(-150, 60, 50, 35)
        ]
        
        self.windows = []
        self.create_windows()
        
        self.road_lines = [
            RoadLine(height - 80),
            RoadLine(height - 80),
            RoadLine(height - 80),
            RoadLine(height - 80)
        ]
       
        for i, line in enumerate(self.road_lines):
            line.x = -60 - (i * 80)
        
        self.create_buttons()
        
        self.weather_conditions = [
            ('☀️', 'Despejado'),
            ('☁️', 'Nublado'),
            ('🌦️', 'Lluvia ligera'),
            ('🌧️', 'Lluvia'),
            ('⛈️', 'Tormenta'),
            ('🌫️', 'Niebla'),
            ('💨', 'Viento')
        ]
        self.current_weather = 0
        self.weather_timer = 0
        
    def load_background(self):
        
        self.use_image_bg = False
        self.create_procedural_background()
    
    def create_procedural_background(self):
        
        self.background_image = pygame.Surface((self.width, self.height))
        
        for y in range(self.height - 120):
           
            ratio = y / (self.height - 120)
            r = int(135 + (152 - 135) * ratio)
            g = int(206 + (228 - 206) * ratio)
            b = int(235 + (255 - 235) * ratio)
            pygame.draw.line(self.background_image, (r, g, b), (0, y), (self.width, y))
        
        pygame.draw.rect(self.background_image, (74, 74, 74), (0, self.height - 500, 200, 500))
        
        pygame.draw.rect(self.background_image, (139, 74, 107), (self.width - 300, self.height - 600, 300, 600))
        
        pygame.draw.rect(self.background_image, (105, 105, 105), (0, self.height - 120, self.width, 120))
        
    def create_windows(self):
    
        for row in range(3):
            for col in range(2):
                x = 30 + col * 60
                y = self.height - 450 + row * 100
                self.windows.append(AnimatedWindow(x, y, 40, 60))
        
        for row in range(4):
            for col in range(3):
                x = self.width - 260 + col * 80
                y = self.height - 550 + row * 100
                self.windows.append(AnimatedWindow(x, y, 50, 70))
    
    def create_buttons(self):
        
        button_width = 280
        button_height = 60
        spacing = 25
        
        total_height = 4 * button_height + 3 * spacing
        start_y = (self.height - total_height) // 2 + 50
        center_x = (self.width - button_width) // 2
        
        base_color = (40, 40, 60)  # Negro azulado
        hover_color = (0, 255, 136)  # Verde neón
        primary_color = (0, 100, 200)  # Azul para botón principal
        primary_hover = (0, 255, 136)  # Verde para hover del principal
        danger_color = (150, 50, 50)  # Rojo para salir
        danger_hover = (200, 80, 80)  # Rojo más claro para hover
        
        self.buttons = {
            "new_game": Button(
                "NUEVA PARTIDA",
                center_x, start_y,
                button_width, button_height,
                primary_color, primary_hover, self.text_color, (0, 255, 136), 2, 24
            ),
            "load_game": Button(
                "CARGAR PARTIDA",
                center_x, start_y + button_height + spacing,
                button_width, button_height,
                base_color, hover_color, self.text_color, (255, 255, 255), 2, 24
            ),
            "high_scores": Button(
                "RECORDS", 
                center_x, start_y + 2 * (button_height + spacing),
                button_width, button_height,
                base_color, hover_color, self.text_color, (255, 255, 255), 2, 24
            ),
            "exit": Button(
                "SALIR",
                center_x, start_y + 3 * (button_height + spacing),
                button_width, button_height,
                danger_color, danger_hover, self.text_color, (255, 100, 100), 2, 24
            )
        }
    
    def update(self, dt):
        
        self.title_pulse += dt * 2
        
        self.cyclist.update(dt)
        
        for cloud in self.clouds:
            cloud.update(dt, self.width)
        
        for window in self.windows:
            window.update(dt)
        
        for road_line in self.road_lines:
            road_line.update(dt, self.width)
        
        self.weather_timer += dt
        if self.weather_timer >= 10.0:
            self.weather_timer = 0
            self.current_weather = (self.current_weather + 1) % len(self.weather_conditions)
    
    def draw_animated_background(self):
        
        self.screen.blit(self.background_image, (0, 0))
        
        for window in self.windows:
            window.draw(self.screen)
        
        for road_line in self.road_lines:
            road_line.draw(self.screen)
        
        for cloud in self.clouds:
            cloud.draw(self.screen)
        
        tree_sway = math.sin(pygame.time.get_ticks() * 0.002) * 2
        
        tree1_x = self.width * 0.35
        tree1_y = self.height - 160
        pygame.draw.rect(self.screen, (139, 69, 19), (tree1_x - 8, tree1_y, 15, 60))  

        tree_center = (int(tree1_x + tree_sway), tree1_y - 20)
        pygame.draw.circle(self.screen, (218, 165, 32), tree_center, 40)
        
        tree2_x = self.width * 0.55
        tree2_y = self.height - 160
        pygame.draw.rect(self.screen, (139, 69, 19), (tree2_x - 8, tree2_y, 15, 60))  
       
        tree_center2 = (int(tree2_x - tree_sway), tree2_y - 20)
        pygame.draw.circle(self.screen, (218, 165, 32), tree_center2, 40)
        
        self.cyclist.draw(self.screen)
        
    def draw_menu_overlay(self):
       
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        title_scale = 1 + math.sin(self.title_pulse) * 0.02
        title_font = pygame.font.Font(None, int(72 * title_scale))
        
        glow_intensity = int(50 + 30 * math.sin(self.title_pulse))
        title_color = (0, min(255, 155 + glow_intensity), min(255, 136 + glow_intensity//2))
        
        title_surface = title_font.render("COURIER QUEST", True, title_color)
        title_rect = title_surface.get_rect(center=(self.width // 2, self.height // 4))
        
        shadow_surface = title_font.render("COURIER QUEST", True, (0, 0, 0))
        shadow_rect = title_rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        self.screen.blit(shadow_surface, shadow_rect)
        
        self.screen.blit(title_surface, title_rect)
        
        subtitle_surface = self.font_subtitle.render("URBAN DELIVERY CHALLENGE", True, self.subtitle_color)
        subtitle_rect = subtitle_surface.get_rect(center=(self.width // 2, self.height // 4 + 60))
        self.screen.blit(subtitle_surface, subtitle_rect)
        
        for button in self.buttons.values():
            button.draw(self.screen)
    
    def draw_ui_elements(self):
    
        weather_icon, weather_text = self.weather_conditions[self.current_weather]
        
        weather_bg = pygame.Surface((180, 80), pygame.SRCALPHA)
        weather_bg.fill((0, 0, 0, 180))
        self.screen.blit(weather_bg, (20, 20))
        
        climate_font = pygame.font.Font(None, 28)
        text_surface = climate_font.render(weather_text, True, (255, 255, 255))
        self.screen.blit(text_surface, (35, 35))
        
        status_bg = pygame.Surface((160, 80), pygame.SRCALPHA)
        status_bg.fill((0, 0, 0, 180))
        self.screen.blit(status_bg, (self.width - 180, 20))
        
        api_color = (76, 175, 80)  # Verde para online
        pygame.draw.circle(self.screen, api_color, (self.width - 165, 35), 5)
        api_text = self.font_footer.render("API Online", True, (255, 255, 255))
        self.screen.blit(api_text, (self.width - 150, 28))
        
        save_color = (76, 175, 80)  # Verde si hay guardado
        pygame.draw.circle(self.screen, save_color, (self.width - 165, 60), 5)
        save_text = self.font_footer.render("Partida guardada", True, (255, 255, 255))
        self.screen.blit(save_text, (self.width - 150, 53))
        
        footer_text = "EIF-207 Estructuras de Datos • Proyecto 1 • II Ciclo 2025"
        footer_surface = self.font_footer.render(footer_text, True, (200, 200, 200))
        footer_rect = footer_surface.get_rect(center=(self.width // 2, self.height - 40))
        self.screen.blit(footer_surface, footer_rect)
        
    
    def draw(self):
        
        self.screen.fill((135, 206, 235)) 
        
        self.draw_animated_background()
        
        self.draw_menu_overlay()
        
        self.draw_ui_elements()
        
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