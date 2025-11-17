import pygame
import random
import math


class UIManager:
    """Maneja la interfaz gráfica del juego."""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Fuentes
        self.font_small = pygame.font.Font(None, 20)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_large = pygame.font.Font(None, 36)
        
        # Colores
        self.colors = {
            'bg': (20, 20, 30),
            'text': (255, 255, 255),
            'text_dim': (150, 150, 150),
            'panel': (40, 40, 50),
            'success': (50, 255, 100),
            'warning': (255, 200, 50),
            'danger': (255, 50, 50),
            'road': (80, 80, 90),
            'building': (100, 100, 120),
            'park': (50, 150, 80),
            'player': (100, 200, 255),
            'rival': (255, 100, 100),
        }
        
        # Layout
        self.map_offset_x = 200
        self.map_offset_y = 50
        self.tile_size = 30
        
        # Cámara
        self.camera_x = 0
        self.camera_y = 0
        
        # Partículas de clima
        self.rain_particles = []
        self.wind_particles = []
        
    def update_camera(self, player_x, player_y, map_width, map_height):
        """Centra la cámara en el jugador"""
        view_width = self.screen_width - self.map_offset_x
        view_height = self.screen_height - 100
        
        target_x = player_x * self.tile_size - view_width // 2
        target_y = player_y * self.tile_size - view_height // 2
        
        max_x = map_width * self.tile_size - view_width
        max_y = map_height * self.tile_size - view_height
        
        self.camera_x = max(0, min(target_x, max_x))
        self.camera_y = max(0, min(target_y, max_y))
    
    def update_weather_effects(self, weather, dt):
        """Actualiza partículas de clima"""
        view_width = self.screen_width - self.map_offset_x
        view_height = self.screen_height - 100
        
        if weather in ['rain', 'rain_light', 'storm']:
            intensity = 5 if weather == 'storm' else 3 if weather == 'rain' else 1
            for _ in range(intensity):
                self.rain_particles.append({
                    'x': random.randint(self.map_offset_x, self.screen_width),
                    'y': self.map_offset_y,
                    'speed': random.randint(400, 600)
                })
        
        if weather in ['wind', 'storm']:
            if random.random() < 0.1:
                self.wind_particles.append({
                    'x': self.map_offset_x,
                    'y': random.randint(self.map_offset_y, self.map_offset_y + view_height),
                    'speed': random.randint(200, 400)
                })
        
        # Actualizar lluvia
        for p in self.rain_particles[:]:
            p['y'] += p['speed'] * dt
            if p['y'] > self.map_offset_y + view_height:
                self.rain_particles.remove(p)
        
        # Actualizar viento
        for p in self.wind_particles[:]:
            p['x'] += p['speed'] * dt
            if p['x'] > self.screen_width:
                self.wind_particles.remove(p)
    
    def draw_weather_effects(self, surface, weather):
        """Dibuja efectos visuales del clima"""
        # Overlay de clima
        overlay = pygame.Surface((self.screen_width - self.map_offset_x, 
                                 self.screen_height - 100), pygame.SRCALPHA)
        
        if weather == 'storm':
            overlay.fill((20, 20, 40, 100))
        elif weather in ['rain', 'rain_light']:
            overlay.fill((30, 30, 50, 50))
        elif weather == 'fog':
            overlay.fill((200, 200, 200, 80))
        elif weather == 'heat':
            overlay.fill((255, 200, 100, 30))
        
        surface.blit(overlay, (self.map_offset_x, self.map_offset_y))
        
        # Dibujar lluvia
        for p in self.rain_particles:
            pygame.draw.line(surface, (150, 150, 200), 
                           (p['x'], p['y']), (p['x'] - 2, p['y'] + 10), 1)
        
        # Dibujar viento
        for p in self.wind_particles:
            pygame.draw.line(surface, (200, 200, 200, 100),
                           (p['x'], p['y']), (p['x'] + 30, p['y']), 2)
        
        # Flash de tormenta
        if weather == 'storm' and random.random() < 0.01:
            flash = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            flash.fill((255, 255, 255, 150))
            surface.blit(flash, (0, 0))
        
    def draw_hud(self, surface, player, rival, game_time, weather, elapsed, current_game_time):
        """Dibuja el HUD principal."""
        panel_rect = pygame.Rect(0, 0, 190, self.screen_height)
        pygame.draw.rect(surface, self.colors['panel'], panel_rect)
        
        y = 10
        
        # HORA DEL JUEGO
        time_str = current_game_time.strftime("%H:%M:%S")
        self._draw_text(surface, f"Hora: {time_str}", 10, y, 
                       self.font_medium, self.colors['text'])
        y += 35

        time_left = max(0, int(game_time - elapsed))
        minutes, seconds = divmod(time_left, 60)
        time_left_str = f"{minutes:02d}:{seconds:02d}"
        time_color = self.colors['danger'] if time_left < 60 else self.colors['text']
        self._draw_text(surface, f"Tiempo Restante: {time_left_str}", 10, y, 
                       self.font_small, time_color)
        y += 35
        
        progress = player.total_income / player.income_goal
        income_color = (self.colors['success'] if progress >= 1.0 
                       else self.colors['warning'] if progress >= 0.7
                       else self.colors['text'])
        self._draw_text(surface, "Ingresos:", 10, y, self.font_small, self.colors['text_dim'])
        y += 20
        self._draw_text(surface, f"${player.total_income}", 10, y, self.font_medium, income_color)
        y += 25
        self._draw_progress_bar(surface, 10, y, 170, 15, progress, income_color)
        y += 25
        self._draw_text(surface, f"Meta: ${player.income_goal}", 10, y, 
                       self.font_small, self.colors['text_dim'])
        y += 30
        
        stamina_pct = player.stamina / 100
        stamina_color = (self.colors['danger'] if stamina_pct < 0.3
                        else self.colors['warning'] if stamina_pct < 0.6
                        else self.colors['success'])
        self._draw_text(surface, f"Resistencia: {int(player.stamina)}", 10, y,
                       self.font_small, self.colors['text'])
        y += 20
        self._draw_progress_bar(surface, 10, y, 170, 12, stamina_pct, stamina_color)
        y += 25
        
        rep_pct = player.reputation / 100
        rep_color = (self.colors['danger'] if rep_pct < 0.3
                    else self.colors['warning'] if rep_pct < 0.7
                    else self.colors['success'])
        self._draw_text(surface, f"Reputación: {int(player.reputation)}", 10, y,
                       self.font_small, self.colors['text'])
        y += 20
        self._draw_progress_bar(surface, 10, y, 170, 12, rep_pct, rep_color)
        y += 30
        
        # Mostrar clima con símbolo
        weather_symbols = {
            'clear': '☀️', 'clouds': '☁️', 'rain': '🌧️', 
            'rain_light': '🌦️', 'storm': '⛈️', 'fog': '🌫️',
            'wind': '💨', 'heat': '🔥', 'cold': '❄️'
        }
        symbol = weather_symbols.get(weather, '')
        self._draw_text(surface, f"{symbol} {weather}", 10, y,
                       self.font_small, self.colors['text_dim'])
        y += 25
        
        weight_pct = player.inventory.current_weight / player.inventory.max_weight
        self._draw_text(surface, f"Peso: {player.inventory.current_weight}/{player.inventory.max_weight}", 
                       10, y, self.font_small, self.colors['text_dim'])
        y += 20
        self._draw_progress_bar(surface, 10, y, 170, 10, weight_pct, self.colors['warning'])
        y += 20
        self._draw_text(surface, f"Pedidos: {player.inventory.order_count}", 10, y,
                       self.font_small, self.colors['text_dim'])
        # --- Información del Rival ---
        y += 40
        self._draw_text(surface, "Rival:", 10, y, 
                       self.font_medium, self.colors['rival'])
        y += 30
        
        # Ingresos del Rival
        rival_progress = rival.total_income / rival.income_goal
        self._draw_text(surface, f"Ingresos Rival: ${rival.total_income}", 10, y, 
                       self.font_small, self.colors['text'])
        y += 20
        self._draw_progress_bar(surface, 10, y, 170, 10, rival_progress, self.colors['rival'])
        y += 20

        # Pedidos del Rival
        self._draw_text(surface, f"Pedidos Rival: {rival.inventory.order_count}", 10, y,
                       self.font_small, self.colors['text_dim'])
        
    def draw_map(self, surface, city, player_x, player_y, available_orders, rival):
        """Dibuja el mapa con cámara centrada"""
        self.update_camera(player_x, player_y, city.width, city.height)
        
        for y, row in enumerate(city.tiles):
            for x, tile in enumerate(row):
                screen_x = self.map_offset_x + x * self.tile_size - self.camera_x
                screen_y = self.map_offset_y + y * self.tile_size - self.camera_y
                
                if (screen_x < self.map_offset_x - self.tile_size or 
                    screen_x > self.screen_width or
                    screen_y < self.map_offset_y - self.tile_size or 
                    screen_y > self.screen_height - 100):
                    continue
                
                if tile == 'C':
                    color = self.colors['road']
                elif tile == 'B':
                    color = self.colors['building']
                elif tile == 'P':
                    color = self.colors['park']
                else:
                    color = self.colors['road']
                
                rect = pygame.Rect(screen_x, screen_y, self.tile_size - 2, self.tile_size - 2)
                pygame.draw.rect(surface, color, rect)
        
        # Dibujar marcadores de pedidos disponibles
        for order in available_orders:
            pickup = order['pickup']
            self._draw_map_marker_camera(surface, pickup, (100, 255, 100), "P")
        
        # Dibujar jugador
        px = self.map_offset_x + player_x * self.tile_size - self.camera_x
        py = self.map_offset_y + player_y * self.tile_size - self.camera_y
        player_rect = pygame.Rect(px + 5, py + 5, self.tile_size - 12, self.tile_size - 12)
        pygame.draw.rect(surface, self.colors['player'], player_rect)
        pygame.draw.rect(surface, (255, 255, 255), player_rect, 2)
        
        # Draw rival
        rx = self.map_offset_x + rival.x * self.tile_size - self.camera_x
        ry = self.map_offset_y + rival.y * self.tile_size - self.camera_y
        rival_rect = pygame.Rect(rx + 5, ry + 5, self.tile_size - 12, self.tile_size - 12)
        pygame.draw.rect(surface, '#FF0000' , rival_rect)
        pygame.draw.rect(surface, (255, 255, 255), rival_rect, 2)

    def draw_current_order(self, surface, inventory, city):
        """Dibuja información del pedido actual."""
        if inventory.current_order is None:
            return
        
        order = inventory.current_order.order
        
        panel_y = self.screen_height - 120
        panel_rect = pygame.Rect(self.map_offset_x, panel_y, 
                                 self.screen_width - self.map_offset_x, 120)
        pygame.draw.rect(surface, self.colors['panel'], panel_rect)
        pygame.draw.rect(surface, self.colors['text_dim'], panel_rect, 2)
        
        x = self.map_offset_x + 10
        y = panel_y + 10
        
        priority_text = f"⭐ Prioridad {order.priority}" if order.priority > 0 else ""
        self._draw_text(surface, f"Pedido Actual: {order.id} {priority_text}", 
                       x, y, self.font_medium, self.colors['success'])
        y += 30
        
        self._draw_text(surface, f"Peso: {order.weight}kg | Pago: ${order.payout}", 
                       x, y, self.font_small, self.colors['text'])
        y += 22
        self._draw_text(surface, f"Recogida: {order.pickup} → Entrega: {order.dropoff}", 
                       x, y, self.font_small, self.colors['text'])
        y += 22
        self._draw_text(surface, f"Fecha Límite: {order.deadline.replace('T', ' ')}", 
                       x, y, self.font_small, self.colors['text_dim'])
        
        self._draw_map_marker_camera(surface, order.dropoff, (255, 100, 100), "D")
    
    def draw_available_orders(self, surface, orders, start_y=50):
        """Dibuja panel de pedidos disponibles."""
        if not orders:
            return
        
        panel_x = self.screen_width - 250
        panel_width = 240
        
        panel_rect = pygame.Rect(panel_x, start_y, panel_width, 
                                min(400, len(orders) * 70 + 40))
        pygame.draw.rect(surface, self.colors['panel'], panel_rect)
        pygame.draw.rect(surface, self.colors['text_dim'], panel_rect, 2)
        
        self._draw_text(surface, "Pedidos Disponibles", panel_x + 10, start_y + 10,
                       self.font_medium, self.colors['text'])
        
        y = start_y + 45
        for i, order in enumerate(orders[:5]):
            self._draw_order_item(surface, order, panel_x + 10, y, panel_width - 20)
            y += 70
    
    def _draw_order_item(self, surface, order, x, y, width):
        """Dibuja un item de pedido."""
        color = self.colors['warning'] if order.get('priority', 0) > 0 else self.colors['text']
        self._draw_text(surface, order['id'], x, y, self.font_small, color)
        
        if order.get('priority', 0) > 0:
            self._draw_text(surface, f"⭐{order['priority']}", x + width - 30, y,
                           self.font_small, self.colors['warning'])
        
        y += 18
        self._draw_text(surface, f"${order['payout']} | {order['weight']}kg", 
                       x, y, self.font_small, self.colors['text_dim'])
        y += 16
        deadline_time = order['deadline'].split('T')[1][:5]
        self._draw_text(surface, f"⏰ {deadline_time}", x, y, 
                       self.font_small, self.colors['text_dim'])
    
    def _draw_map_marker_camera(self, surface, pos, color, text):
        """Dibuja marcador considerando la cámara"""
        x, y = pos
        screen_x = self.map_offset_x + x * self.tile_size + self.tile_size // 2 - self.camera_x
        screen_y = self.map_offset_y + y * self.tile_size + self.tile_size // 2 - self.camera_y
        
        if (screen_x < self.map_offset_x or screen_x > self.screen_width or
            screen_y < self.map_offset_y or screen_y > self.screen_height - 120):
            return
        
        pygame.draw.circle(surface, color, (screen_x, screen_y), 8)
        pygame.draw.circle(surface, (255, 255, 255), (screen_x, screen_y), 8, 2)
        
        text_surf = self.font_small.render(text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=(screen_x, screen_y))
        surface.blit(text_surf, text_rect)
    
    def _draw_progress_bar(self, surface, x, y, width, height, progress, color):
        """Dibuja barra de progreso."""
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, (50, 50, 50), bg_rect)
        
        fill_width = int(width * min(1.0, progress))
        fill_rect = pygame.Rect(x, y, fill_width, height)
        pygame.draw.rect(surface, color, fill_rect)
        
        pygame.draw.rect(surface, self.colors['text_dim'], bg_rect, 1)
    
    def _draw_text(self, surface, text, x, y, font, color):
        """Helper para dibujar texto."""
        text_surf = font.render(text, True, color)
        surface.blit(text_surf, (x, y))
    
    def draw_game_over(self, surface, victory, score):
        """Dibuja pantalla de fin de juego."""
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        title = "¡VICTORIA!" if victory else "DERROTA"
        title_color = self.colors['success'] if victory else self.colors['danger']
        
        title_surf = self.font_large.render(title, True, title_color)
        title_rect = title_surf.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
        surface.blit(title_surf, title_rect)
        
        score_text = f"Puntaje Final: {score}"
        score_surf = self.font_medium.render(score_text, True, self.colors['text'])
        score_rect = score_surf.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 20))
        surface.blit(score_surf, score_rect)
        
        instruction = "Presiona ESC para salir"
        instruction_surf = self.font_small.render(instruction, True, self.colors['text_dim'])
        instruction_rect = instruction_surf.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 80))
        surface.blit(instruction_surf, instruction_rect)