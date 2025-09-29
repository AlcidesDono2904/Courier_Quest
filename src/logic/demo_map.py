import pygame
import sys
import json
import os
sys.path.append('src')

from logic.map import Map
from logic.proxy import get_proxy


class MapDemo:
    def __init__(self):
        pygame.init()
        
        # Configuración de ventana
        self.screen_width = 1024
        self.screen_height = 768
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Courier Quest - Map Demo")
        self.game_map = None
        
        # Configuración de cámara
        self.camera_x = 0
        self.camera_y = 0
        self.camera_speed = 5
        
        # Cargar mapa
        self.load_map()
        
        # Configuración de jugador (temporal)
        self.player_x = 0
        self.player_y = 0
        if self.game_map:
            spawn_x, spawn_y = self.game_map.find_spawn_position()
            self.player_x, self.player_y = self.game_map.grid_to_world(spawn_x, spawn_y)
        
        # Colores y fuentes
        self.background_color = (50, 50, 50)
        self.player_color = (255, 255, 0)  # Amarillo
        self.text_color = (255, 255, 255)
        self.font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 36)
        
        # Estados del demo
        self.show_info = True
        self.show_grid = True
        
        # Clock para FPS
        self.clock = pygame.time.Clock()
        self.fps = 120
        
    def load_map(self):
        """Carga el mapa usando el proxy y luego lo pre-renderiza."""
        try:
            # 1. Intentamos obtener el mapa desde el Proxy
            print("Cargando mapa desde el proxy...")
            proxy = get_proxy()
            self.game_map = proxy.get_map()
            
            # 2. Verificamos si la carga fue exitosa
            if self.game_map and self.game_map.tiles:
                print(f"Mapa cargado exitosamente: {self.game_map.width}x{self.game_map.height}")
            else:
                # Si el proxy no devuelve un mapa válido, creamos uno de prueba
                print("Proxy no devolvió un mapa válido, creando mapa de prueba.")
                self.create_test_map()
                
        except Exception as e:
            # Si hay cualquier error con el proxy, creamos un mapa de prueba
            print(f"Error al cargar mapa desde el proxy: {e}")
            self.create_test_map()
        
        # 3. MUY IMPORTANTE: Pre-renderizamos el mapa DESPUÉS de que se haya cargado
        if self.game_map:
            self._render_map_surface()

    def _render_map_surface(self):
        """Dibuja el mapa completo en una superficie para optimizar."""
        print("Pre-renderizando la superficie del mapa...")
        map_width_px = self.game_map.width * self.game_map.cell_size
        map_height_px = self.game_map.height * self.game_map.cell_size
        self.map_surface = pygame.Surface((map_width_px, map_height_px))
        
        # Usamos una versión simplificada de tu método draw, pero sobre la nueva superficie
        for y, row in enumerate(self.game_map.tiles):
            for x, tile_type in enumerate(row):
                color = self.game_map.colors.get(tile_type, self.game_map.colors["default"])
                rect = pygame.Rect(x * self.game_map.cell_size, y * self.game_map.cell_size, self.game_map.cell_size, self.game_map.cell_size)
                pygame.draw.rect(self.map_surface, color, rect)
                pygame.draw.rect(self.map_surface, (0, 0, 0), rect, 1) # Borde
    
    def create_test_map(self):
        """Crea un mapa de prueba si falla la carga."""
        test_map_data = {
            "version": "1.0",
            "width": 20,
            "height": 15,
            "tiles": [],
            "legend": {
                "C": {"name": "calle", "surface_weight": 1.00},
                "B": {"name": "edificio", "blocked": True},
                "P": {"name": "parque", "surface_weight": 0.95}
            },
            "goal": 3000
        }
        
        # Generar mapa procedural simple
        import random
        for y in range(15):
            row = []
            for x in range(20):
                # Crear patrones más interesantes
                if random.random() < 0.15:
                    row.append("B")  # Edificio
                elif random.random() < 0.1:
                    row.append("P")  # Parque
                else:
                    row.append("C")  # Calle
            test_map_data["tiles"].append(row)
        
        self.game_map = Map(test_map_data)
        print("Usando mapa de prueba generado")
    
    def handle_events(self):
        """Maneja eventos de pygame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_i:
                    self.show_info = not self.show_info
                elif event.key == pygame.K_g:
                    self.show_grid = not self.show_grid
                elif event.key == pygame.K_r:
                    self.load_map()
                
        
        return True
    
    def update_camera(self):
        """Actualiza la posición de la cámara."""
        keys = pygame.key.get_pressed()
        
        # Movimiento de cámara con WASD o flechas
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.camera_x -= self.camera_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.camera_x += self.camera_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.camera_y -= self.camera_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.camera_y += self.camera_speed
        
        # Limitar cámara a los bordes del mapa
        if self.game_map:
            max_camera_x = max(0, self.game_map.width * self.game_map.cell_size - self.screen_width)
            max_camera_y = max(0, self.game_map.height * self.game_map.cell_size - self.screen_height)
            
            self.camera_x = max(0, min(self.camera_x, max_camera_x))
            self.camera_y = max(0, min(self.camera_y, max_camera_y))
    
    def update_player(self):
        """Actualiza la posición del jugador (demo)."""
        keys = pygame.key.get_pressed()
        
        # Movimiento del jugador con IJKL
        move_speed = 2
        new_x, new_y = self.player_x, self.player_y
        
        if keys[pygame.K_j]:  # Izquierda
            new_x -= move_speed
        if keys[pygame.K_l]:  # Derecha
            new_x += move_speed
        if keys[pygame.K_i]:  # Arriba
            new_y -= move_speed
        if keys[pygame.K_k]:  # Abajo
            new_y += move_speed
        
        # Verificar si la nueva posición es válida
        if self.game_map:
            grid_x, grid_y = self.game_map.world_to_grid(new_x, new_y)
            if self.game_map.is_walkable(grid_x, grid_y):
                self.player_x, self.player_y = new_x, new_y
    
    def draw_map(self):
        """Dibuja el mapa pre-renderizado en pantalla."""
        if hasattr(self, 'map_surface'):
            # Dibuja la única imagen grande, moviéndola según la cámara
            self.screen.blit(self.map_surface, (-self.camera_x, -self.camera_y))
    
    def draw_player(self):
        """Dibuja el jugador en pantalla."""
        player_screen_x = self.player_x - self.camera_x
        player_screen_y = self.player_y - self.camera_y
        
        # Solo dibujar si está visible
        if (-20 <= player_screen_x <= self.screen_width + 20 and 
            -20 <= player_screen_y <= self.screen_height + 20):
            
            # Círculo del jugador
            pygame.draw.circle(self.screen, self.player_color, 
                             (int(player_screen_x + 16), int(player_screen_y + 16)), 12)
            # Borde negro
            pygame.draw.circle(self.screen, (0, 0, 0), 
                             (int(player_screen_x + 16), int(player_screen_y + 16)), 12, 2)
    
    def draw_info_panel(self):
        """Dibuja el panel de información."""
        if not self.show_info:
            return
        
        # Panel semi-transparente
        info_surface = pygame.Surface((300, 250))
        info_surface.set_alpha(200)
        info_surface.fill((30, 30, 30))
        self.screen.blit(info_surface, (10, 10))
        
        y_offset = 20
        line_height = 25
        
        # Título
        title = self.large_font.render("MAP DEMO", True, (255, 255, 0))
        self.screen.blit(title, (20, y_offset))
        y_offset += 40
        
        # Información del mapa
        if self.game_map:
            info_lines = [
                f"Dimensiones: {self.game_map.width}x{self.game_map.height}",
                f"Meta: ${self.game_map.goal}",
                f"Cámara: ({self.camera_x}, {self.camera_y})",
                "",
                "Controles:",
                "WASD/Flechas - Cámara",
                "IJKL - Jugador",
                "G - Toggle grid",
                "I - Toggle info",
                "R - Recargar mapa",
                "ESC - Salir"
            ]
        else:
            info_lines = ["Error: No hay mapa cargado"]
        
        for line in info_lines:
            if line:  # No renderizar líneas vacías
                text = self.font.render(line, True, self.text_color)
                self.screen.blit(text, (20, y_offset))
            y_offset += line_height
    
    def draw_minimap(self):
        """Dibuja un minimapa en la esquina."""
        if not self.game_map or not self.show_info:
            return
        
        # Configuración del minimapa
        minimap_size = 150
        minimap_x = self.screen_width - minimap_size - 10
        minimap_y = 10
        
        # Fondo del minimapa
        minimap_surface = pygame.Surface((minimap_size, minimap_size))
        minimap_surface.fill((20, 20, 20))
        
        # Calcular escala
        scale_x = minimap_size / (self.game_map.width * self.game_map.cell_size)
        scale_y = minimap_size / (self.game_map.height * self.game_map.cell_size)
        scale = min(scale_x, scale_y)
        
        # Dibujar tiles del minimapa
        for y in range(self.game_map.height):
            for x in range(self.game_map.width):
                tile_type = self.game_map.get_tile_type(x, y)
                color = self.game_map.colors.get(tile_type, (100, 100, 100))
                
                mini_x = int(x * self.game_map.cell_size * scale)
                mini_y = int(y * self.game_map.cell_size * scale)
                mini_size = max(1, int(self.game_map.cell_size * scale))
                
                pygame.draw.rect(minimap_surface, color, 
                               (mini_x, mini_y, mini_size, mini_size))
        
        # Dibujar jugador en minimapa
        player_mini_x = int(self.player_x * scale)
        player_mini_y = int(self.player_y * scale)
        pygame.draw.circle(minimap_surface, (255, 255, 0), 
                         (player_mini_x, player_mini_y), 3)
        
        # Dibujar viewport de cámara
        cam_mini_x = int(self.camera_x * scale)
        cam_mini_y = int(self.camera_y * scale)
        cam_mini_w = int(self.screen_width * scale)
        cam_mini_h = int(self.screen_height * scale)
        pygame.draw.rect(minimap_surface, (255, 0, 0), 
                        (cam_mini_x, cam_mini_y, cam_mini_w, cam_mini_h), 1)
        
        # Dibujar borde del minimapa
        pygame.draw.rect(minimap_surface, (255, 255, 255), 
                        (0, 0, minimap_size, minimap_size), 2)
        
        self.screen.blit(minimap_surface, (minimap_x, minimap_y))
    
    def draw_tile_info(self):
        """Dibuja información del tile bajo el mouse."""
        if not self.game_map:
            return
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        world_x = mouse_x + self.camera_x
        world_y = mouse_y + self.camera_y
        grid_x, grid_y = self.game_map.world_to_grid(world_x, world_y)
        
        # Verificar que esté dentro del mapa
        if (0 <= grid_x < self.game_map.width and 
            0 <= grid_y < self.game_map.height):
            
            tile_type = self.game_map.get_tile_type(grid_x, grid_y)
            tile_props = self.game_map.get_tile_properties(tile_type)
            
            # Información del tile
            info_lines = [
                f"Posición: ({grid_x}, {grid_y})",
                f"Tipo: {tile_type}",
                f"Nombre: {tile_props.get('name', 'Unknown')}",
                f"Peso superficie: {tile_props.get('surface_weight', 1.0)}",
                f"Bloqueado: {'Sí' if tile_props.get('blocked', False) else 'No'}"
            ]
            
            # Panel de información del tile
            panel_width = 200
            panel_height = len(info_lines) * 20 + 10
            panel_x = min(mouse_x + 15, self.screen_width - panel_width)
            panel_y = min(mouse_y + 15, self.screen_height - panel_height)
            
            # Fondo del panel
            panel_surface = pygame.Surface((panel_width, panel_height))
            panel_surface.set_alpha(220)
            panel_surface.fill((0, 0, 0))
            self.screen.blit(panel_surface, (panel_x, panel_y))
            
            # Texto
            for i, line in enumerate(info_lines):
                text = self.font.render(line, True, (255, 255, 255))
                self.screen.blit(text, (panel_x + 5, panel_y + 5 + i * 20))
    
    
    
    def run(self):
        """Bucle principal del demo."""
        running = True
        
        print("=== COURIER QUEST MAP DEMO ===")
        print("Controles:")
        print("  WASD/Flechas - Mover cámara")
        print("  IJKL - Mover jugador")
        print("  G - Toggle grid")
        print("  I - Toggle info panel")
        print("  R - Recargar mapa")
        print("  Mouse - Ver info del tile")
        print("  ESC - Salir")
        print()
        
        while running:
            # Eventos
            running = self.handle_events()
            
            # Actualizaciones
            self.update_camera()
            self.update_player()
            
            # Dibujo
            self.screen.fill(self.background_color)
            
            self.draw_map()
            self.draw_player()
            self.draw_info_panel()
            self.draw_minimap()
            self.draw_tile_info()
            
            # FPS
            fps_text = self.font.render(f"FPS: {int(self.clock.get_fps())}", 
                                      True, (255, 255, 255))
            self.screen.blit(fps_text, (self.screen_width - 80, self.screen_height - 25))
            
            pygame.display.flip()
            self.clock.tick(self.fps)
        
        pygame.quit()
        print("Demo terminado")


def main():
    """Función principal."""
    try:
        demo = MapDemo()
        demo.run()
    except Exception as e:
        print(f"Error en el demo: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()