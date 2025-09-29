import pygame
import sys
import json
import os
import queue
sys.path.append('src')

from logic.map import Map
from logic.proxy import get_proxy
from .player import Player


class GameLoop:
    def __init__(self):
        pygame.init()
        
        # Configuración de ventana
        self.screen_width = 1024
        self.screen_height = 768
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Courier Quest")
        self.game_map = None
        
        # Configuración de cámara
        self.camera_x = 0
        self.camera_y = 0
        self.camera_speed = 5
        
        # Cargar mapa
        self.load_map()
        
        # Configuración de jugador (temporal)
        
        spawn_x, spawn_y = self.game_map.find_spawn_position()
        self.player = Player(
            spawn_x,
            spawn_y,
            income_goal=self.game_map.goal,
        )
        # LIFO stack of last movement directions (dx, dy) in pixels
        self.player_movements = queue.LifoQueue()

        # Smooth movement variables
        self.player_is_moving = False
        self.player_start_pos = (spawn_x, spawn_y)
        self.player_target_pos = (spawn_x, spawn_y)
        self.movement_progress = 0.0
        self.movement_speed = 0.15  # How fast to move (0.1 = slow, 0.5 = fast)
        
        # Movement timing control
        self.last_movement_time = 0
        self.movement_delay = 200  # milliseconds between movements (200ms = 5 moves/second)

        self.start_time = pygame.time.get_ticks()
        # max_time is provided in SECONDS by the map; convert seconds -> milliseconds
        self.max_time_ms = self.game_map.max_time * 1000
        self.game_over = False

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

        proxy = get_proxy()
        self.game_map = proxy.get_map()
        
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
    
    
    def handle_events(self):
        """Maneja eventos de pygame."""
        self.events = pygame.event.get()
        for event in self.events:
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
        """Actualiza la posición de la cámara para seguir al jugador."""
        # Get current player position (interpolated if moving)
        if self.player_is_moving:
            start_x, start_y = self.player_start_pos
            target_x, target_y = self.player_target_pos
            player_x = start_x + (target_x - start_x) * self.movement_progress
            player_y = start_y + (target_y - start_y) * self.movement_progress
        else:
            player_x, player_y = self.player.x, self.player.y
        
        # Center camera on player
        target_camera_x = player_x - self.screen_width // 2
        target_camera_y = player_y - self.screen_height // 2
        
        # Limitar cámara a los bordes del mapa
        if self.game_map:
            max_camera_x = max(0, self.game_map.width * self.game_map.cell_size - self.screen_width)
            max_camera_y = max(0, self.game_map.height * self.game_map.cell_size - self.screen_height)
            
            target_camera_x = max(0, min(target_camera_x, max_camera_x))
            target_camera_y = max(0, min(target_camera_y, max_camera_y))
        
        # Smooth camera movement (optional - remove for instant following)
        camera_lerp_speed = 0.1
        self.camera_x += (target_camera_x - self.camera_x) * camera_lerp_speed
        self.camera_y += (target_camera_y - self.camera_y) * camera_lerp_speed
    
    def update_player(self):
        """Actualiza la posición del jugador con movimiento suave y continuo."""
        current_time = pygame.time.get_ticks()
        
        # Check for continuous key presses (only start new movement if not currently moving and enough time has passed)
        if not self.player_is_moving and (current_time - self.last_movement_time) >= self.movement_delay:
            keys = pygame.key.get_pressed()
            move_speed = 32
            current_x, current_y = self.player.x, self.player.y
            new_x, new_y = current_x, current_y
            dx, dy = 0, 0

            # Check for movement keys being held down
            using_z = False
            if keys[pygame.K_z] and not self.player_movements.empty(): 
                # Revert last movement direction from LIFO stack (peek and invert)
                last_dx, last_dy = self.player_movements.queue[-1]
                dx, dy = -last_dx, -last_dy
                using_z = True
            else:
                if keys[pygame.K_a]:  # Izquierda
                    dx = -move_speed
                elif keys[pygame.K_d]:  # Derecha
                    dx = move_speed
                elif keys[pygame.K_w]:  # Arriba
                    dy = -move_speed
                elif keys[pygame.K_s]:  # Abajo
                    dy = move_speed

            new_x += dx
            new_y += dy
            
            # If movement was requested
            if new_x != current_x or new_y != current_y:
                # Verificar si la nueva posición es válida
                if self.game_map:
                    grid_x, grid_y = self.game_map.world_to_grid(new_x, new_y)
                    if self.game_map.is_walkable(grid_x, grid_y):
                        # Start smooth movement
                        self.player_is_moving = True
                        self.player_start_pos = (current_x, current_y)
                        self.player_target_pos = (new_x, new_y)
                        self.movement_progress = 0.0
                        self.last_movement_time = current_time
                        # If using Z, now that movement is valid, pop the reverted direction from history
                        if using_z:
                            try:
                                self.player_movements.get_nowait()
                            except Exception:
                                pass
                        # Record direction only for manual WASD moves (not for Z repeats)
                        if not using_z and (dx != 0 or dy != 0):
                            self.player_movements.put((dx, dy))
                            # Optional cap to 50 entries
                            try:
                                while self.player_movements.qsize() > 50:
                                    # Drop the oldest bottom entry
                                    if hasattr(self.player_movements, 'queue') and self.player_movements.queue:
                                        # remove first element
                                        self.player_movements.queue.pop(0)
                                    else:
                                        break
                            except Exception:
                                pass
        # Update smooth movement animation
        if self.player_is_moving:
            self.movement_progress += self.movement_speed
            
            if self.movement_progress >= 1.0:
                # Movement complete
                self.movement_progress = 1.0
                self.player_is_moving = False
                # Update actual player position
                target_x, target_y = self.player_target_pos
                self.player.move(target_x, target_y, weather_condition="clear", surface_weight_tile=1.0)
        else:
            self.player.recover_stamina()
    def draw_map(self):
        """Dibuja el mapa pre-renderizado en pantalla."""
        if hasattr(self, 'map_surface'):
            # Dibuja la única imagen grande, moviéndola según la cámara
            self.screen.blit(self.map_surface, (-self.camera_x, -self.camera_y))
    
    def draw_player(self):
        """Dibuja el jugador en pantalla con interpolación suave."""
        # Use interpolated position for smooth movement
        if self.player_is_moving:
            start_x, start_y = self.player_start_pos
            target_x, target_y = self.player_target_pos
            # Linear interpolation between start and target position
            current_x = start_x + (target_x - start_x) * self.movement_progress
            current_y = start_y + (target_y - start_y) * self.movement_progress
        else:
            current_x, current_y = self.player.x, self.player.y
        
        player_screen_x = current_x - self.camera_x
        player_screen_y = current_y - self.camera_y

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
        info_surface = pygame.Surface((300, 270))
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
            # Compute remaining time
            remaining_ms = max(0, self.max_time_ms - (pygame.time.get_ticks() - self.start_time))
            minutes = remaining_ms // 60000
            seconds = (remaining_ms % 60000) // 1000
            time_str = f"Tiempo restante: {minutes:02d}:{seconds:02d}"

            info_lines = [
                f"Dimensiones: {self.game_map.width}x{self.game_map.height}",
                f"Meta: ${self.game_map.goal}",
                time_str,
                f"Cámara: ({int(self.camera_x)}, {int(self.camera_y)})",
                "",
                "Controles:",
                "Flechas - Cámara",
                "WASD - Jugador",
                "Z - Revertir último movimiento",
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
        
        # Dibujar jugador en minimapa (use interpolated position)
        if self.player_is_moving:
            start_x, start_y = self.player_start_pos
            target_x, target_y = self.player_target_pos
            current_x = start_x + (target_x - start_x) * self.movement_progress
            current_y = start_y + (target_y - start_y) * self.movement_progress
        else:
            current_x, current_y = self.player.x, self.player.y
        player_mini_x = int(current_x * scale)
        player_mini_y = int(current_y * scale)
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
        
        # Convert to integers to avoid float index error
        grid_x, grid_y = int(grid_x), int(grid_y)
        
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
        print("  Flechas - Mover cámara")
        print("  WASD - Mover jugador")
        print("  Z - Repetir último movimiento")
        print("  G - Toggle grid")
        print("  I - Toggle info panel")
        print("  R - Recargar mapa")
        print("  Mouse - Ver info del tile")
        print("  ESC - Salir")
        print()
        
        while running:
            # Eventos
            running = self.handle_events()
            # Timer check
            if not self.game_over:
                current_time = pygame.time.get_ticks()
                if (current_time - self.start_time) >= self.max_time_ms:
                    self.game_over = True

            # Actualizaciones (only when game not over)
            if not self.game_over:
                self.update_camera()
                self.update_player()
            
            # Dibujo
            self.screen.fill(self.background_color)         
            
            self.draw_map()
            self.draw_player()
            self.draw_info_panel()
            self.draw_minimap()
            self.draw_tile_info()

            # If game over, draw overlay
            if self.game_over:
                overlay = pygame.Surface((self.screen_width, self.screen_height))
                overlay.set_alpha(200)
                overlay.fill((0, 0, 0))
                self.screen.blit(overlay, (0, 0))
                go_font = pygame.font.Font(None, 72)
                go_text = go_font.render("GAME OVER", True, (255, 0, 0))
                txt_rect = go_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                self.screen.blit(go_text, txt_rect)
            
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
        demo = GameLoop()
        demo.run()
    except Exception as e:
        print(f"Error en el demo: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()