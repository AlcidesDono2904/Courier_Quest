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
        Mueve al rival en la dirección dada.
        Args:
            direction (tuple[int, int]): La dirección en la que moverse.
        """
        dx, dy = direction
        if self.is_exhausted:
            return
        # Make sure the move is valid.
        if dx not in [-1, 0, 1] or dy not in [-1, 0, 1]:
            raise ValueError("dx and dy must be -1, 0, or 1")

        self.x += dx
        self.y += dy
    
    def decide_next_move(self):
        """Decide el próximo movimiento basado en la estrategia."""
        decision = self.strategy.next_move()
        self._move(decision)
