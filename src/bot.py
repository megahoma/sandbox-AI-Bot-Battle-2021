import random

from .geometry import Coordinate, Direction, directions
from .utils import get_filename


class IBot:
    def __init__(self, _name='Default name', _id=None):
        self._name = _name
        self._number = -1
        self._id = _id or random.randint(2**31, 2**32)

    def chooseDirection(self, snake, opponent, mazeSize: Coordinate, apple: Coordinate) -> Direction:
        """
        Smart snake bot (brain of your snake) should choose step (direction where to go)
        on each game step until the end of game

        snake    -- Your snake's body with coordinates for each segment
        opponent -- Opponent snake's body with coordinates for each segme
        mazeSize -- Size of the board
        apple    -- Coordinate of an apple
        """
        raise NotImplementedError()
