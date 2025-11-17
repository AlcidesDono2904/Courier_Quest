from src.logic.player import Player
from src.logic.strategies.strategy import Strategy

class Rival(Player):
    """Representa al repartidor rival (IA)."""

    def __init__(self, x, y, income_goal, strategy: Strategy):
        super().__init__(x, y, income_goal)
        self.strategy = strategy

    def set_strategy(self, strategy: Strategy):
        """
        Establece la estrategia del rival.
        Args:
            strategy (Strategy): La nueva estrategia a usar.
        """
        self.strategy = strategy
        
    def _move(self, direction: tuple[int, int]):
        """
        Mueve al rival en la dirección dada. (Solo actualiza la posición)
        Args:
            direction (tuple[int, int]): La dirección en la que moverse.
        """
        dx, dy = direction
        self.x += dx
        self.y += dy
    
    def decide_next_move(self, city, current_weather) -> bool:
        """Decide el próximo movimiento basado en la estrategia y lo ejecuta, consumiendo resistencia."""
        
        decision = self.strategy.next_move()
        dx, dy = decision
        new_x = self.x + dx
        new_y = self.y + dy

        if dx == 0 and dy == 0:
            return False

        if self.can_move() and not city.is_blocked(new_x, new_y):
            
            self.consume_stamina(current_weather) 
            
            self._move(decision)
            return True

        return False 