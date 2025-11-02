from src.logic.strategies.strategy import Strategy
from src.logic.player import Player


class EasyStrategy(Strategy):
    """Very simple strategy used for testing and examples."""

    def __init__(self, game, player: Player):
        super().__init__(game, player)

    def _find_path(self, start: tuple[int, int], end: tuple[int, int]) -> list[tuple[int, int]]:
        pass
    
    def next_move(self) -> tuple[int, int]:
        """Return the next move as (dx, dy).

        This example simply moves down one tile.
        """
        return 1, 0