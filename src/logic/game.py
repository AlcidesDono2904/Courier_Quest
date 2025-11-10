import pygame
import random
from datetime import datetime, timedelta, timezone
from src.logic.proxy import Proxy
from src.logic.city import City, OrderManager
from src.logic.player import Player

from src.logic.strategies.easy_strategy import EasyStrategy
from src.logic.strategies.medium_strategy import MediumStrategy
from src.logic.strategies.hard_strategy import HardStrategy

from src.logic.order import Order
from src.logic.game_state import GameState
from src.logic.ui import UIManager
from src.config.config import WEATHER_MULTIPLIERS

# 1.3 para version final, 0.6 para testing
RIVAL_INTERACTION_RATE = 0.6  # segundos entre interacciones del rival

class Game:
    """Bucle principal del juego."""

    # MODIFICACIÓN: Añadir 'difficulty'
    def __init__(self, player_name, difficulty: str):
        pygame.init()
        self.screen = pygame.display.set_mode((1200, 800))
        pygame.display.set_caption("Courier Quest")
        self.clock = pygame.time.Clock()

        proxy = Proxy()
        map_data = proxy.get_map()
        jobs_data = proxy.get_jobs()
        self.weather = proxy.get_weather()

        self.city = City(map_data)
        self.order_manager = OrderManager(jobs_data)
        self.player = Player(1, 1, self.city.goal)
        self.player_name = player_name
        self.game_state = GameState()
        self.ui = UIManager(1200, 800)

        self.game_duration = 900
        # Usar UTC para evitar problemas con zona horaria local
        self.game_start_datetime = datetime(2025, 9, 1, 12, 0, 0, tzinfo=timezone.utc)

        self.elapsed_time = 0.0
        self.running = True
        self.game_over = False
        self.victory = False

        self.current_weather = self.weather.state
        self.next_weather = self.weather.state
        self.weather_timer = random.uniform(45, 60)
        self.weather_transition_time = 0.0
        self.in_transition = False

        self.message = ""
        self.message_timer = 0.0

        self.player_moved_this_frame = False

        self.exit_reason = "menu"

        self._arrow_was_pressed = False
        self.loaded_slot = None
        self.saving_overlay_active = False
        self.saving_overlay_timer = 0.0
        self.saving_overlay_duration = 0.7 
        self._saving_overlay_message = "Juego guardado. Volviendo al menú..."
        
        # Rival 
        from src.logic.rival import Rival
        self.rival = Rival(0, 0, self.city.goal, None)

        # --- LÓGICA DE DIFICULTAD (NUEVA) ---
        strategy_map = {
            "easy": EasyStrategy,
            "medium": MediumStrategy,
            "hard": HardStrategy
        }
        
        # Asignar estrategia, usando HardStrategy como fallback
        StrategyClass = strategy_map.get(difficulty.lower(), HardStrategy)
        self.rival.set_strategy(StrategyClass(self, self.rival))
        # ------------------------------------

        self.rival_interaction_rate = RIVAL_INTERACTION_RATE
   
    def handle_input(self):
        """Maneja input del jugador (eventos + movimiento por polling)."""
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                self.exit_reason = "exit"
                self.running = False
                return

            if self.game_over:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.exit_reason = "menu"
                    self.running = False
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    self.player.inventory.view_next_order()
                    self.show_message("Siguiente pedido")
                elif event.key == pygame.K_p:
                    self.player.inventory.view_prev_order()
                    self.show_message("Pedido anterior")
                elif event.key == pygame.K_s:
                    self.player.inventory.sort_inventory(lambda o: o.priority)
                    self.show_message("Ordenado por prioridad")
                elif event.key == pygame.K_d:
                    self.player.inventory.sort_inventory(
                        lambda o: self._normalize_datetime(o.deadline)
                    )
                    self.show_message("Ordenado por deadline")

                elif event.key == pygame.K_a:
                    self.accept_order_at_location()

                elif event.key == pygame.K_RETURN:
                    self.complete_delivery()

                elif event.key == pygame.K_c:
                    if self.player.cancel_order():
                        self.show_message("Pedido cancelado (-4 reputación)")

                elif event.key == pygame.K_F5:
                    slot = self.save_game_auto()
                    self.activate_saving_overlay(f"Guardado en Slot {slot}. Volviendo al menú...")

                elif event.key == pygame.K_F9:
                    self.show_message("Para cargar, usa el menú principal")

                elif event.key == pygame.K_u:
                    state = self.game_state.undo(1)
                    if state:
                        self.restore_state(state)
                        self.show_message("Deshacer último movimiento")

        if not self.game_over and not self.saving_overlay_active:
            keys = pygame.key.get_pressed()
            dx = (1 if keys[pygame.K_RIGHT] else 0) - (1 if keys[pygame.K_LEFT] else 0)
            dy = (1 if keys[pygame.K_DOWN] else 0) - (1 if keys[pygame.K_UP] else 0)

            arrow_pressed_now = (dx != 0 or dy != 0)
            if arrow_pressed_now and not self._arrow_was_pressed:
                new_x = self.player.x + dx
                new_y = self.player.y + dy

                if not self.city.is_blocked(new_x, new_y):
                    if self.player.can_move():
                        self.player.consume_stamina(self.current_weather)
                        self.player.x = new_x
                        self.player.y = new_y
                        self.player_moved_this_frame = True

                        self.game_state.save_state(
                            self.player,
                            self.player.inventory,
                            self.elapsed_time,
                            self.current_weather
                        )
                        self.check_delivery_points()
                    else:
                        self.show_message("¡Exhausto! Descansa para recuperarte")
                else:
                    self.show_message("No puedes moverte ahí")

            self._arrow_was_pressed = arrow_pressed_now


    def activate_saving_overlay(self, message):
        """Activa el overlay de guardado y agenda retorno al menú."""
        self.saving_overlay_active = True
        self.saving_overlay_timer = self.saving_overlay_duration
        self._saving_overlay_message = message


    def _normalize_datetime(self, dt_string):
        dt = datetime.fromisoformat(dt_string)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt

    def get_current_game_datetime(self):
        return self.game_start_datetime + timedelta(seconds=self.elapsed_time)

    def show_message(self, text, duration=2.0):
        self.message = text
        self.message_timer = duration

    def accept_order_at_location(self):
        available = self.order_manager.get_available()
        for order_data in available:
            pickup = order_data['pickup']
            if [self.player.x, self.player.y] == pickup:
                order = Order.from_dict(order_data)
                if self.player.accept_order(order):
                    self.order_manager.remove_order(order_data['id'])
                    self.show_message(f"Pedido {order.id} aceptado!")
                    return
                else:
                    self.show_message("Inventario lleno")
                    return
        self.show_message("No hay pedidos en esta ubicación")

    def check_delivery_points(self):
        if self.player.inventory.current_order:
            dropoff = self.player.inventory.current_order.order.dropoff
            if [self.player.x, self.player.y] == dropoff:
                self.show_message("¡Punto de entrega! Presiona ENTER")

    def complete_delivery(self):
        if self.player.inventory.current_order is None:
            self.show_message("No hay pedido para entregar")
            return
        dropoff = self.player.inventory.current_order.order.dropoff
        if [self.player.x, self.player.y] != dropoff:
            self.show_message("Debes estar en el punto de entrega")
            return

        current_game_time = self.get_current_game_datetime()
        result = self.player.complete_delivery(current_game_time)
        if result:
            msg = f"¡Entregado! +${int(result['payout'])} | Rep: {result['rep_change']:+d}"
            self.show_message(msg, 3.0)

    def update_weather(self, dt):
        self.weather_timer -= dt
        if self.in_transition:
            self.weather_transition_time += dt
            if self.weather_transition_time >= 4:
                self.current_weather = self.next_weather
                self.in_transition = False
        if self.weather_timer <= 0 and not self.in_transition:
            self.next_weather = self.weather.next_state()
            self.weather_timer = random.uniform(45, 60)
            self.weather_transition_time = 0
            self.in_transition = True

    def get_current_weather_multiplier(self):
        if not self.in_transition:
            return WEATHER_MULTIPLIERS.get(self.current_weather, 1.0)
        progress = self.weather_transition_time / 4.0
        current_mult = WEATHER_MULTIPLIERS.get(self.current_weather, 1.0)
        next_mult = WEATHER_MULTIPLIERS.get(self.next_weather, 1.0)
        return current_mult + (next_mult - current_mult) * progress

    def update(self, dt):
        
        if self.saving_overlay_active:
            self.saving_overlay_timer -= dt
            if self.saving_overlay_timer <= 0:
                self.saving_overlay_active = False
                self.exit_reason = "menu"
                self.running = False
            return

        if self.game_over:
            return

        if not self.player_moved_this_frame:
            self.player.recover_stamina(dt*0.22)

        self.elapsed_time += dt
        self.update_weather(dt)
        self.ui.update_weather_effects(self.current_weather, dt)
        self.order_manager.update_available(self.elapsed_time)

        current_game_time = self.get_current_game_datetime()
        if self.player.inventory.first:
            node = self.player.inventory.first
            orders_to_expire = []
            while node:
                deadline = self._normalize_datetime(node.order.deadline)
                if current_game_time > deadline:
                    orders_to_expire.append(node.order)
                node = node.next
            for order in orders_to_expire:
                self.player.expire_order(order)
                self.show_message(f"Pedido {order.id} expirado! (-6 Rep)", 3.0)

        if self.message_timer > 0:
            self.message_timer -= dt

        if self.player.is_defeated():
            self.end_game(False)

        if self.elapsed_time >= self.game_duration:
            if self.player.has_won():
                self.end_game(True)
            else:
                self.end_game(False)
                
        # Rival update
        if self.rival_interaction_rate > 0:
            self.rival_interaction_rate -= dt
        else:
            self.rival.decide_next_move()
            self.rival_interaction_rate = RIVAL_INTERACTION_RATE     

    def draw(self):
        self.screen.fill((20, 20, 30))

        available = self.order_manager.get_available()
        self.ui.draw_map(self.screen, self.city, self.player.x, self.player.y, available, self.rival)
        self.ui.draw_weather_effects(self.screen, self.current_weather)

        current_game_time = self.get_current_game_datetime()
        self.ui.draw_hud(
            self.screen, self.player, self.game_duration,
            self.current_weather, self.elapsed_time, current_game_time
        )
        self.ui.draw_current_order(self.screen, self.player.inventory, self.city)
        self.ui.draw_available_orders(self.screen, available)

        if self.message_timer > 0 and not self.saving_overlay_active:
            font = pygame.font.Font(None, 32)
            text = font.render(self.message, True, (255, 255, 100))
            rect = text.get_rect(center=(600, 400))
            bg = pygame.Surface((rect.width + 40, rect.height + 20))
            bg.set_alpha(200)
            bg.fill((0, 0, 0))
            self.screen.blit(bg, bg.get_rect(center=(600, 400)))
            self.screen.blit(text, rect)

        if self.game_over and not self.saving_overlay_active:
            score = self.calculate_score()
            self.ui.draw_game_over(self.screen, self.victory, score)

        if self.saving_overlay_active:
            overlay = pygame.Surface((1200, 800))
            overlay.set_alpha(160)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            box_w, box_h = 560, 160
            box = pygame.Surface((box_w, box_h))
            box.set_alpha(235)
            box.fill((25, 25, 35))
            self.screen.blit(box, box.get_rect(center=(600, 400)))

            title_font = pygame.font.Font(None, 48)
            sub_font = pygame.font.Font(None, 28)
            title = title_font.render("Guardado", True, (0, 255, 136))
            sub = sub_font.render(self._saving_overlay_message, True, (220, 220, 220))
            self.screen.blit(title, title.get_rect(center=(600, 370)))
            self.screen.blit(sub, sub.get_rect(center=(600, 410)))

            progress = 1.0 - max(0.0, self.saving_overlay_timer) / self.saving_overlay_duration
            bar_w, bar_h = 360, 14
            bar_x, bar_y = 600 - bar_w // 2, 440
            pygame.draw.rect(self.screen, (60, 60, 80), (bar_x, bar_y, bar_w, bar_h), border_radius=8)
            pygame.draw.rect(self.screen, (0, 255, 136), (bar_x, bar_y, int(bar_w * progress), bar_h), border_radius=8)

        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.player_moved_this_frame = False
            self.handle_input()
            self.update(dt)
            self.draw()
        return self.exit_reason

    def save_game_auto(self):
        """Guarda usando la política: primer slot libre o más antiguo si lleno. Devuelve slot usado."""
        game_data = {
            'elapsed_time': self.elapsed_time,
            'weather_state': self.current_weather,
            'weather_timer': self.weather_timer,
            'game_start_datetime': self.game_start_datetime.isoformat(),
        }
        slot_used = self.game_state.auto_save(self.player, self.player.inventory, game_data, self.player_name)
        return slot_used

    def load_game(self, data):
        """Carga una partida (desde dict). Se usa desde el MENÚ."""
        if not data:
            return False
        self.player_name = data.get('player_name', self.player_name)
        p = data['player']
        self.player.x = p['x']
        self.player.y = p['y']
        self.player.stamina = p['stamina']
        self.player.reputation = p['reputation']
        self.player.total_income = p['total_income']
        from src.logic.inventory import Inventory
        self.player.inventory = Inventory()
        for order_data in data['inventory']:
            order = Order.from_dict(order_data)
            self.player.inventory.add_order(order)
        gd = data['game_data']
        self.elapsed_time = gd['elapsed_time']
        self.current_weather = gd['weather_state']
        self.weather_timer = gd['weather_timer']
        if 'game_start_datetime' in gd:
            self.game_start_datetime = datetime.fromisoformat(gd['game_start_datetime'])
        return True

    def calculate_score(self):
        bonus = 0
        if self.victory and self.elapsed_time < self.game_duration * 0.8:
            bonus = 500
        score_base = self.player.total_income
        penalties = self.player.total_penalties
        final_score = score_base + bonus - penalties
        return int(max(0, final_score))

    def end_game(self, victory):
        """Finaliza el juego y calcula puntaje."""
        self.game_over = True
        self.victory = victory

        score = self.calculate_score()

        GameState.save_score(
        self.player_name,
        score,
        self.player.total_income,
        self.player.reputation
    ) 
        if getattr(self, "loaded_slot", None):
           self.game_state.delete_slot(self.loaded_slot)
           self.loaded_slot = None