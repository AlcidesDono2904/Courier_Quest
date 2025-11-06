import math
import random
from ..order import Order
from ..city import City
from .strategy import Strategy

class MediumStrategy(Strategy):
    """
    Estrategia de dificultad Media (Greedy Search):
    Utiliza un enfoque Greedy Best-First Search (GBFS) para elegir pedidos
    basado en una heurística que prioriza la ganancia sobre el costo de distancia/clima.
    """

    DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    ALPHA = 2.0   # Peso de la ganancia (Payout)
    BETA = 1.0    # Peso de la distancia (Manhattan Distance)
    GAMMA = 0.5   # Peso de la penalización por clima

    def __init__(self, game: 'Game', rival: 'Rival'):
        super().__init__(game, rival)
        self.target_order_id: str | None = None
       
        self.re_evaluation_timer = random.uniform(4.0, 10.0)
        # Ruta almacenada (lista de coordenadas)
        self.current_path: list[tuple[int, int]] = [] 

    def _evaluate_order(self, order_data: dict, current_pos: tuple[int, int]) -> float:
        """
        Evalúa un pedido con una función heurística.
        score = α*(payout) - β*(distance) - γ*(weather_penalty)
        """
        px, py = order_data["pickup"]
        
        # 1. Ganancia (Expected Payout)
        payout = order_data.get("payout", 10)
        
        # 2. Distancia (Manhattan distance al punto de recogida)
        distance = abs(px - current_pos[0]) + abs(py - current_pos[1]) 
        
        # 3. Penalización por clima (Mayor si el multiplicador de velocidad es bajo)
        weather_mult = self.game.get_current_weather_multiplier() 
        # La penalización es proporcional a cuánto peor es el clima (1.0 - mult)
        weather_penalty_term = (1.0 - weather_mult) * 20 # Multiplicador de 20 para darle peso

        # Heurística final (MAXIMIZAR ESTE PUNTAJE)
        score = (self.ALPHA * payout) - \
                (self.BETA * distance) - \
                (self.GAMMA * weather_penalty_term)
        
        # Penalización extra si el pedido excede la capacidad de carga 
        if self.rival.get_total_weight() + order_data.get('weight', 0) > self.rival.inventory.max_weight:
            return -math.inf
            
        return score
    
    def _find_path(self, start: tuple[int, int], end: tuple[int, int]) -> list[tuple[int, int]]:
        """
        Implementación simplificada:
        Calcula la dirección directa hacia el destino, esquivando obstáculos
        básicos en línea recta y priorizando el eje más lejano.
        """
        path = []
        city: City = self.game.city
        x, y = start
        ex, ey = end

        for _ in range(30): # Límite de 30 pasos para evitar bucles infinitos en esquinas
            if (x, y) == (ex, ey):
                break
                
            dx = 1 if ex > x else -1 if ex < x else 0
            dy = 1 if ey > y else -1 if ey < y else 0
            
            # Decide el movimiento, priorizando el eje con mayor diferencia (más 'Greedy')
            if abs(ex - x) > abs(ey - y):
                # Prioriza el movimiento en X
                nx, ny = x + dx, y 
                blocked_x = city.is_blocked(nx, ny)
                
                # Si está bloqueado en X, intenta moverse en Y
                if blocked_x and dy != 0:
                    nx, ny = x, y + dy
            else:
                # Prioriza el movimiento en Y
                nx, ny = x, y + dy
                blocked_y = city.is_blocked(nx, ny)

                # Si está bloqueado en Y, intenta moverse en X
                if blocked_y and dx != 0:
                    nx, ny = x + dx, y

            # Verificación final de bloqueo antes de avanzar
            if city.is_blocked(nx, ny):
                break # Bloqueo, abortar el camino por ahora
            
            # Movimiento válido
            path.append((nx, ny))
            x, y = nx, ny
            
        return path
    
    def _search_next_objective(self) -> dict | None:
        """
        Busca el mejor pedido disponible para recoger usando la heurística.
        Solo busca si el inventario está vacío.
        """
        if self.rival.inventory.order_count > 0:
            return None 
            
        current_pos = (self.rival.x, self.rival.y)
        available_orders = self.game.order_manager.get_available()
        
        if not available_orders:
            return None
            
        # Encontrar el pedido con el mejor puntaje heurístico
        best_order_data = max(
            available_orders,
            key=lambda o: self._evaluate_order(o, current_pos)
        )
        
        # Devolver el mejor pedido solo si su puntaje es viable 
        if self._evaluate_order(best_order_data, current_pos) == -math.inf:
             return None 
        
        return best_order_data

    def next_move(self) -> tuple[int, int]:
        """
        Calcula el siguiente movimiento basado en el camino pre-calculado.
        Si no hay camino, devuelve (0, 0) y `decide_job_action` re-evaluará.
        """
        if self.current_path:
            next_step = self.current_path.pop(0)
            dx = next_step[0] - self.rival.x
            dy = next_step[1] - self.rival.y
            
            # Debe ser un movimiento unitario
            return (dx, dy)
            
        return (0, 0)
    
    def decide_job_action(self, dt: float):
        """
        Lógica principal: Selecciona el mejor objetivo y planifica el camino
        hacia el punto de acción (recogida o entrega).
        """
        current_pos = (self.rival.x, self.rival.y)
        
        # 1. Intentar Entregar Pedido Actual 
        if self.rival.inventory.current_order:
            order = self.rival.inventory.current_order.order
            dropoff = tuple(order.dropoff)

            if dropoff == current_pos:
                self.game.complete_delivery_rival(self.rival)
                self.current_path.clear()
                self.target_order_id = None
                return True
            
            if not self.current_path:
                self.current_path = self._find_path(current_pos, dropoff)

        # 2. Reevaluar y Recoger Pedido (SI EL INVENTARIO ESTÁ VACÍO)
        elif self.rival.inventory.order_count == 0:
            self.re_evaluation_timer -= dt
            
            if self.re_evaluation_timer <= 0 or not self.target_order_id:
                best_order = self._search_next_objective()
                
                if best_order:
                    
                    pickup_pos = tuple(best_order["pickup"])
                    self.target_order_id = best_order["id"]
                    self.current_path = self._find_path(current_pos, pickup_pos)
                else:
                    self.target_order_id = None
                    self.current_path.clear() # Si no hay objetivo, se queda quieto
                    
                self.re_evaluation_timer = random.uniform(4.0, 10.0) # Reset del timer

            # 3. Intentar Recoger si el objetivo está en la posición
            if self.target_order_id:
                available_orders = self.game.order_manager.get_available()
                for order_data in available_orders:
                    if order_data["id"] == self.target_order_id and tuple(order_data["pickup"]) == current_pos:
                        if self.game.accept_order_at_location_rival(self.rival, order_data):
                            self.current_path.clear()
                            return True
        
        return False