from .strategy import Strategy
from ..player import Player


class EasyStrategy(Strategy):
    """Very simple strategy used for testing and examples."""

    def __init__(self, game, player: Player):
        super().__init__(game, player)

    def next_move(self) -> tuple[int, int]:
        """Return the next move as (dx, dy).

        This example simply moves down one tile.
        """
        return 1, 0