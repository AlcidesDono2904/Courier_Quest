import random
from .strategy import Strategy
from ..order import Order
from ..city import City
from ..game import Game

class EasyStrategy(Strategy):
    """
    Estrategia de dificultad Fácil:
    Implementa Random Walk y Random Choice como su lógica principal.
    """

    # Movimientos posibles: Arriba, Abajo, Izquierda, Derecha
    DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def __init__(self, game: Game, rival):
        super().__init__(game, rival)
        self.target_order_id: str | None = None
        self.re_evaluation_timer = random.uniform(5.0, 15.0)
        self.last_move: tuple[int, int] | None = None  # Evita devolverse inmediatamente

    def _find_path(self, start: tuple[int, int], end: tuple[int, int]) -> list[tuple[int, int]]:
        """
        El nivel fácil no utiliza pathfinding.
        Retorna None o una lista vacía.
        """
        return []

    def next_move(self) -> tuple[int, int]:
        """
        Lógica del Random Walk:
        Elige una dirección adyacente válida al azar (evitando obstáculos y movimientos inútiles).
        """
        current_x, current_y = self.rival.x, self.rival.y
        valid_moves = []
        city: City = self.game.city

        # 1. Generar y filtrar movimientos potenciales
        for dx, dy in self.DIRECTIONS:
            new_x = current_x + dx
            new_y = current_y + dy

            # Verifica si el tile es caminable
            if not city.is_blocked(new_x, new_y):
                valid_moves.append((dx, dy))

        # 2. Evita devolverse al paso anterior (si hay alternativas)
        if self.last_move and (-self.last_move[0], -self.last_move[1]) in valid_moves and len(valid_moves) > 1:
            valid_moves.remove((-self.last_move[0], -self.last_move[1]))

        # 3. Elegir un movimiento al azar válido
        if valid_moves:
            move = random.choice(valid_moves)
            self.last_move = move
            return move
        else:
            # Si no hay movimientos válidos, quedarse quieto
            return (0, 0)

    def decide_job_action(self, dt: float):
        """
        Lógica de Random Choice para elegir pedidos y actuar en ellos.
        Se ejecuta periódicamente (cada tick de actualización).
        """
        city: City = self.game.city
        current_pos = [self.rival.x, self.rival.y]

        # 1. Si no tiene pedidos en el inventario, elige uno al azar cada cierto tiempo
        if self.rival.inventory.order_count == 0:
            self.re_evaluation_timer -= dt
            if self.re_evaluation_timer <= 0:
                available_orders = self.game.order_manager.get_available()
                if available_orders:
                    # Selección ponderada: más probabilidad de elegir pedidos cercanos
                    def order_weight(order_data):
                        px, py = order_data['pickup']
                        dist = abs(px - current_pos[0]) + abs(py - current_pos[1])
                        return 1 / (dist + 1)  # Evita división por cero

                    chosen_data = random.choices(
                        available_orders,
                        weights=[order_weight(o) for o in available_orders],
                        k=1
                    )[0]

                    self.target_order_id = chosen_data['id']

                # Reinicia el temporizador de reevaluación
                self.re_evaluation_timer = random.uniform(5.0, 15.0)

        # 2. Intentar recoger un pedido si está en el punto de recogida
        if self.rival.inventory.order_count == 0 and self.target_order_id:
            available_orders = self.game.order_manager.get_available()
            for order_data in available_orders:
                if order_data['id'] == self.target_order_id and order_data['pickup'] == current_pos:
                    if self.game.accept_order_at_location_rival(self.rival, order_data):
                        self.target_order_id = None  # Limpia el objetivo, ahora debe entregar
                        return True

        # 3. Intentar entregar si lleva un pedido activo
        if self.rival.inventory.current_order:
            dropoff = self.rival.inventory.current_order.order.dropoff
            if dropoff == current_pos:
                self.game.complete_delivery_rival(self.rival)
                return True

        return False
