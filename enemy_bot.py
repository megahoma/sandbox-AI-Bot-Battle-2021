"""
Bot that will die in `MOVES_BEFORE_DIE` moves
"""
from src.bot import IBot
from src.geometry import Direction, Coordinate, RIGHT
from src.snake import Snake

MOVES_BEFORE_DIE = 3

class Bot(IBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.i = 0
        

    def chooseDirection(self, snake: Snake, opponent: Snake, mazeSize: Coordinate, apple: Coordinate) -> Direction:
        self.i += 1

        if self.i > MOVES_BEFORE_DIE:
            head = snake.body[0]
            firstBodyElement = snake.body[1]
            directionToDeath = head.getDirection(firstBodyElement)

            return directionToDeath
        else:
            return RIGHT