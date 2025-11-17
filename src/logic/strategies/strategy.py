from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.logic.game import Game
    from src.logic.rival import Rival

class Strategy(ABC):
    """Abstract base class for different strategies."""

    def __init__(self, game: 'Game', rival: 'Rival'):
        self.game = game
        self.rival = rival

    @abstractmethod
    def _find_path(self, start: tuple[int, int], end: tuple[int, int]) -> list[tuple[int, int]]:
        """
        Finds a path from start to end coordinates. Will use algorithm like A*.
        Args:
            start (tuple[int, int]): Starting coordinates.
            end (tuple[int, int]): Ending coordinates.
        Returns:
            list[tuple[int, int]]: List of coordinates representing the path.
        """
        pass

    @abstractmethod
    def next_move(self) -> tuple[int, int]:
        """
        Find next move
        Returns:
            coords (tuple[int, int]): The next move as (x, y) coordinates.
        """
        # Main method to be implemented by subclasses.
        # Should select and find a path to an order if there
        # is not one already.
        pass
    
    
    