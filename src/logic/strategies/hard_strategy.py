import heapq
import math
import random
from .strategy import Strategy
from ..city import City
from ..order import Order

class HardStrategy(Strategy):
    """
    Estrategia de dificultad Difícil:
    Implementa el algoritmo A* (A estrella) para planificar rutas óptimas
    entre puntos de recogida y entrega, considerando el costo del terreno y el clima.
    """

    def __init__(self, game: 'Game', rival: 'Rival'):
        super().__init__(game, rival)
        self.target_order_id: str | None = None
        self.current_path: list[tuple[int, int]] = []
        self.re_evaluation_timer = random.uniform(5.0, 10.0)
        self.last_weather_multiplier = game.get_current_weather_multiplier()
        self.max_recalc_interval = 5.0  # segundos entre recalculaciones por clima
        self.recalc_timer = 0.0

    def _heuristic(self, a: tuple[int, int], b: tuple[int, int]) -> float:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _find_path(self, start: tuple[int, int], goal: tuple[int, int]) -> list[tuple[int, int]]:
        """
        Implementación clásica del algoritmo A* en una cuadrícula.
        Considera bloqueos y penalizaciones por clima.
        """
        city: City = self.game.city
        weather_mult = self.game.get_current_weather_multiplier()
        width, height = city.width, city.height

        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self._heuristic(start, goal)}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                # Reconstruir el camino
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (current[0] + dx, current[1] + dy)
                x, y = neighbor
                if not (0 <= x < width and 0 <= y < height):
                    continue  # fuera del mapa
                if city.is_blocked(x, y):
                    continue  # edificio o muro

                # Costo del movimiento (afectado por clima)
                terrain_cost = 1.0 / weather_mult
                tentative_g = g_score[current] + terrain_cost

                if tentative_g < g_score.get(neighbor, math.inf):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self._heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        # Si no hay camino, retornar vacío
        return []

    def next_move(self) -> tuple[int, int]:
        """
        Retorna el siguiente paso de la ruta planificada.
        """
        if self.current_path:
            next_step = self.current_path.pop(0)
            dx = next_step[0] - self.rival.x
            dy = next_step[1] - self.rival.y
            return (dx, dy)
        else:
            self.decide_job_action(0)
        return (0, 0)

    def _evaluate_order(self, order_data: dict, current_pos: tuple[int, int]) -> float:
        """Evalúa un pedido con base en la recompensa y distancia estimada."""
    
        pickup = tuple(order_data["pickup"])
        dropoff = tuple(order_data["dropoff"])
        payout = order_data.get("payout", 10)

        distance = abs(pickup[0] - current_pos[0]) + abs(pickup[1] - current_pos[1])
        delivery_distance = abs(dropoff[0] - pickup[0]) + abs(dropoff[1] - pickup[1])
        weather_mult = self.game.get_current_weather_multiplier()

        cost = (distance + delivery_distance) / weather_mult
        return payout - 0.5 * cost

    def decide_job_action(self, dt: float):
        """
        Control principal de decisiones del nivel difícil.
        - Replanifica rutas con A*.
        - Reevaluación dinámica según clima o resistencia.
        """
        current_pos = (self.rival.x, self.rival.y)
        city: City = self.game.city

        # 1. Entregar pedido actual (prioridad alta)
        if self.rival.inventory.current_order:
            dropoff = tuple(self.rival.inventory.current_order.order.dropoff)

            if current_pos == dropoff:
                self.game.complete_delivery_rival(self.rival)
                self.current_path.clear()
                self.target_order_id = None
                return True

            # Replanificación por clima o fin de ruta
            self.recalc_timer += dt
            current_weather = self.game.get_current_weather_multiplier()
            if not self.current_path or self.recalc_timer >= self.max_recalc_interval \
               or current_weather != self.last_weather_multiplier:
                self.current_path = self._find_path(current_pos, dropoff)
                self.last_weather_multiplier = current_weather
                self.recalc_timer = 0.0

        # 2. Buscar nuevo pedido si no tiene
        elif self.rival.inventory.order_count == 0:
            self.re_evaluation_timer -= dt
            if self.re_evaluation_timer <= 0 or not self.target_order_id:
                available_orders = self.game.order_manager.get_available()
                if available_orders:
                    best_order = max(
                        available_orders,
                        key=lambda o: self._evaluate_order(o, current_pos)
                    )
                    self.target_order_id = best_order["id"]
                    pickup = tuple(best_order["pickup"])
                    self.current_path = self._find_path(current_pos, pickup)
                self.re_evaluation_timer = random.uniform(5.0, 10.0)

            # Intentar recoger si ya está en el punto de pickup
            if self.target_order_id:
                available_orders = self.game.order_manager.get_available()
                for order_data in available_orders:
                    if order_data["id"] == self.target_order_id and tuple(order_data["pickup"]) == current_pos:
                        if self.game.accept_order_at_location_rival(self.rival, order_data):
                            self.current_path.clear()
                            return True

        return False
