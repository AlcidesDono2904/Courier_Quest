from abc import ABC, abstractmethod
from src.logic.game import Game

class Strategy(ABC):
    """Abstract base class for different strategies."""
    def __init__(self, game: Game):
        self.game = game

    @abstractmethod
    def _findPath(self, start: tuple[int, int], end: tuple[int, int]) -> list[tuple[int, int]]:
        """
        Finds a path from start to end coordinates.
        Args:
            start (tuple[int, int]): Starting coordinates.
            end (tuple[int, int]): Ending coordinates.
        """
        pass

    @abstractmethod
    def nextMove(self) -> tuple[int, int]:
        """
        Find next move
        Returns:
            tuple[int, int]: the next move as (x, y) coordinates.
        """
        # Main method to be implemented by subclasses.
        # Should select and find a path to an order if there
        # is not one already.
        pass
    
    
    