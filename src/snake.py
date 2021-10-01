import time
from typing import List, Set

from .bot import IBot
from .geometry import DOWN, LEFT, RIGHT, UP, Coordinate, Direction


class Snake:
    def __init__(self, 
    mazeSize: Coordinate, elements: Set[Coordinate] = None, 
    body: List[Coordinate] = None, initialHead: Coordinate = None,
    tailDireciton: Direction = None, size: int = None):
        self.mazeSize = mazeSize
        self.elements = elements or set()
        self.body = body or []
        
        if initialHead:
            self.elements = set([initialHead])
            self.body = [initialHead]
            if tailDireciton:
                assert size
                p = initialHead.moveTo(tailDireciton)
                for _ in range(size - 1):
                    self.body.append(p)
                    self.elements.add(p)
                    p = p.moveTo(tailDireciton)
            
    @property
    def head(self):
        return self.body[0]

    def moveTo(self, d: Direction, grow: bool = False) -> bool:
        """
        Move current snake in given direction
        Return false if snake is dead, true otherwise
        """
        died = False
        newHead = self.head.moveTo(d)
        
        if not newHead.inBounds(self.mazeSize):
            died = True
        
        if not grow:
            self.elements.remove(self.body.pop())
            
        if newHead in self.elements:
            died = True
        
        self.body.insert(0, newHead)
        self.elements.add(newHead)

        return not died
    
    def __str__(self):
        return f"Snake({', '.join(map(str, self.body))})"
    
    def headCollidesWith(self, otherSnake) -> bool:
        """
        Return true if head of snake collides with given snake
        """
        return self.head in otherSnake.elements
    
    def clone(self):
        """
        Clone the snake
        """
        return Snake(self.mazeSize, elements=self.elements.copy(), body=self.body.copy())
    
class SnakeRunner:
    """
    Class for communication between a bot and a snake
    """
    def __init__(self, snake: Snake, opponent: Snake, mazeSize: Coordinate, apple: Coordinate, bot: IBot = None, executor = None):
        if bot:
            self.bot = bot
            self.name = bot._name
            self.id = bot._id
            self.mode = 'local'
        elif executor:
            self.executor = executor
            self.name = executor.team.name
            self.id = executor.team.number
            self.mode = 'checker'
        else:
            raise TypeError(f"executor or bot should be passed")

        self.snake = snake
        self.opponent = opponent
        self.mazeSize = mazeSize
        self.apple = apple
        self.lastMove: Direction = None
    
    def run(self, timeout=1, requestTimeout=2) -> Direction:
        """
        Execute chooseDirection function of bot
        and check if there was timeout 
        """
        # clone data, to prevent cheating (modifying objects)
        data = (
            self.snake.clone(), self.opponent.clone(), 
            self.mazeSize.clone(), self.apple.clone(),
            )
        if self.mode == 'local':
            startTime = time.time()
            result = self.bot.chooseDirection(*data)
    
            if time.time() - startTime > timeout:
                raise TimeoutError
    
        elif self.mode == 'checker':
            if not self.executor.running:
                raise Exception(f"Container is not running. Status: ({self.executor.status})")
            
            error, result = self.executor.send(_data=data, timeout=requestTimeout)
            if error:
                if 'timeout' in error:
                    raise TimeoutError
                else:
                    raise Exception(error)
        else:
            raise NotImplementedError(f"No such mode {self.mode}")
        
        self.lastMove = result
        return result


if __name__ == "__main__":
    s = Snake(Coordinate(10,10), initialHead=Coordinate(5, 5), tailDireciton=DOWN, size=5)
    print(s)
    s.moveTo(RIGHT)
    print(s)
    s.moveTo(DOWN)
    print(s)
    s.moveTo(LEFT)
    print(s)
