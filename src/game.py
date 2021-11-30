import random
from itertools import chain
from typing import Tuple, Union
import logging

from . import constants
from .bot import IBot
from .geometry import DOWN, LEFT, RIGHT, UP, Coordinate, Direction
from .snake import Snake, SnakeRunner


class GameOver(Exception):
    """
    Exception for stopping the game
    """

    def __init__(self, snakeWinner: int, reason: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.snakeWinner = snakeWinner
        self.reason = reason

    def __str__(self):
        if self.snakeWinner in [1, 2]:
            return f"Snake #{self.snakeWinner} won. Reason: {self.reason}"
        else:
            return f"Draw. Reason: {self.reason}"


class Game:
    """
    Represents one game between two snakes
    """

    def __init__(
            self, head1: Coordinate, tailDir1: Coordinate,
            head2: Coordinate, tailDir2: Coordinate,
            size: int, mazeSize: Coordinate = None,
            bots: Tuple[IBot, IBot] = None,
            executors: Tuple[SnakeRunner, SnakeRunner] = None):

        self.gameId = random.randint(2**31, 2**32)

        self.mazeSize = mazeSize
        self.snake1 = Snake(self.mazeSize, initialHead=head1,
                            tailDireciton=tailDir1, size=size)
        self.snake2 = Snake(self.mazeSize, initialHead=head2,
                            tailDireciton=tailDir2, size=size)
        self.snake1_prev = None
        self.snake2_prev = None

        self.iterationNumber = 0
        self.score1 = 0
        self.score2 = 0
        self.appleCoordinate = self.randomNonOccupiedCell

        # creating runners
        try:
            self.bot1_runner = SnakeRunner(
                self.snake1, self.snake2, self.mazeSize, self.appleCoordinate,
                bot=bots[0] if bots else None, executor=executors[0] if executors else None)

            self.bot2_runner = SnakeRunner(
                self.snake2, self.snake1, self.mazeSize, self.appleCoordinate,
                bot=bots[1] if bots else None, executor=executors[1] if executors else None)
        except IndexError:
            raise TypeError(f"executors or bots should be tuple of size 2")

        self.moves = []

        self.end = False
        self.snakeWinner = -1
        self.result = (-1, -1)
        self.result_description = "None"

    @staticmethod
    def default_game(bots=None, executors=None):
        """
        Prepare and return default local game
        """

        mazeSize = Coordinate(*constants.GAME_SIZE)

        head1 = Coordinate(*constants.SNAKE1_INITIAL_HEAD)
        tailDir1 = Direction(*constants.SNAKE1_INITIAL_DIRECTION)

        head2 = Coordinate(*constants.SNAKE2_INITIAL_HEAD)
        tailDir2 = Direction(*constants.SNAKE2_INITIAL_DIRECTION)

        snakeSize = constants.SNAKES_INITIAL_SIZE

        game = Game(head1, tailDir1, head2, tailDir2,
                    snakeSize, mazeSize, bots=bots, executors=executors)
        return game

    @property
    def randomNonOccupiedCell(self) -> Union[Coordinate, None]:
        """
        Return any free cell in maze. 
        If there are none, return None
        """
        randomCell = Coordinate(
            random.randint(0, self.mazeSize.x - 1),
            random.randint(0, self.mazeSize.y - 1),
        )
        # TODO: fix method. it can go out of mazeSize
        for dy in range(self.mazeSize.y):
            for dx in range(self.mazeSize.x):
                delta = Coordinate(dx, dy) % self.mazeSize
                newCell = (randomCell + delta) % self.mazeSize

                if not self.cell_is_occupied(newCell):
                    return newCell

        return None

    def cell_is_occupied(self, cell: Coordinate) -> bool:
        """
        Return true if cell is occipied
        """
        return cell in self.snake1.elements or cell in self.snake2.elements

    def check_for_end_game(self, snake1_dead, snake2_dead):
        """
        Check if need to end the game with given conditions
        """
        snake1_name = self.bot1_runner.name
        snake2_name = self.bot2_runner.name
        # if exactly 1 snake is died
        if snake1_dead ^ snake2_dead:
            if snake1_dead:
                self.end_game(2, f"snake of '{snake1_name}' is dead")

            if snake2_dead:
                self.end_game(1, f"snake of '{snake2_name}' is dead")

        # if both snakes are died
        elif snake1_dead and snake2_dead:
            iterationsExceeded = self.iterationNumber > constants.MAX_GAME_ITERATIONS
            prefix = 'Snakes exceeded the maximum number of iterations' if iterationsExceeded else 'Both snakes are died'

            if self.score1 > self.score2:
                self.end_game(1, prefix + f", but '{snake1_name}' earned more points")
            elif self.score2 > self.score1:
                self.end_game(2, prefix + f", but '{snake2_name}' earned more points")
            else:
                self.end_game(
                    0, prefix + ' and they had the same amount of points')

    def run_one_step(self, timeout=1, requestTimeout=2):
        directions = [UP, DOWN, LEFT, RIGHT]
        """
        Run one step of the game. 
        If any of snakes died, then finish the game
        """
        # check if game is already over
        if self.end:
            self.end_game()

        if self.iterationNumber > constants.MAX_GAME_ITERATIONS:
            self.check_for_end_game(snake1_dead=True, snake2_dead=True)

        self.bot1_runner.apple = self.appleCoordinate
        self.bot2_runner.apple = self.appleCoordinate

        try:
            d1 = self.bot1_runner.run(
                timeout=timeout, requestTimeout=requestTimeout)
        except TimeoutError:
            self.end_game(2, 'took too long to make a decision for 1st')
        except Exception as e:
            self.end_game(2, e.__str__())

        if d1 not in directions:
            self.end_game(2, f"Invalid direction for 1st: {d1}")

        try:
            d2 = self.bot2_runner.run(
                timeout=timeout, requestTimeout=requestTimeout)
        except TimeoutError:
            self.end_game(1, 'took too long to make a decision for 2nd')
        except Exception as e:
            self.end_game(1, e.__str__())

        if d2 not in directions:
            self.end_game(1, f"Invalid direction for 2st: {d2}")

        try:
            grow1 = self.snake1.head.moveTo(d1) == self.appleCoordinate
        except Exception as e:
            self.end_game(2, "Player 1 finished the game for technical reasons")

        try:
            grow2 = self.snake2.head.moveTo(d2) == self.appleCoordinate
        except Exception as e:
            self.end_game(1, "Player 2 finished the game for technical reasons")
        
        # remember prev state. (for criteria evaluation)
        self.snake1_prev = self.snake1.clone()
        self.snake2_prev = self.snake2.clone()
        
        snake1_dead = not self.snake1.moveTo(d1, grow1)
        snake2_dead = not self.snake2.moveTo(d2, grow2)

        snake1_dead |= self.snake1.headCollidesWith(self.snake2)
        snake2_dead |= self.snake2.headCollidesWith(self.snake1)

        # check for end game. if game is over, it will throw an exception
        self.check_for_end_game(snake1_dead, snake2_dead)

        # if no one is died,
        self.iterationNumber += 1
        self.score1 += grow1
        self.score2 += grow2
        if grow1 or grow2:
            self.appleCoordinate = self.randomNonOccupiedCell

    def end_game(self, snakeWinner: int = None, result_description: str = None):
        """
        Ends game and raises GameOver exception
        """
        self.end = True
        self.snakeWinner = snakeWinner if snakeWinner != None else self.snakeWinner
        self.result = (int(self.snakeWinner == 1), int(self.snakeWinner == 2))
        self.result_description = result_description if result_description != None else self.result_description
        logging.info(
            f"End game between {self.bot1_runner.name} and {self.bot2_runner.name}. Description: ({self.result_description})")
        raise GameOver(self.snakeWinner, self.result_description)

    def __str__(self):
        """
        Game state in string view
        """

        class Map:
            def __init__(self, mazeSize, emptyField='.'):
                self._map = [[emptyField for _ in range(mazeSize.y)] for _ in range(mazeSize.x)]
            
            def set_value(self, coord: Coordinate, value):
                try:
                    self._map[coord.y][coord.x] = value
                except IndexError:
                    return False
                return True
            def __str__(self):
                return '\n'.join(map(lambda x: ''.join(x), self._map[::-1])) + '\n'

        _map = Map(self.mazeSize)

        for element in self.snake1.elements:
            if element.inBounds(self.mazeSize):
                _map.set_value(element, 'b')
        for element in self.snake2.elements:
            if element.inBounds(self.mazeSize):
                _map.set_value(element, 'B')

        _map.set_value(self.appleCoordinate, 'X')

        # collision
        if self.snake1.head == self.snake2.head:
            _map.set_value(self.snake1.head, '!')
        else:
            _map.set_value(self.snake1.head, 'h')
            _map.set_value(self.snake2.head, 'H')

        return str(_map)

    def get_state(self) -> dict:
        """
        Return dict with current game state
        """
        info = {}

        info['apple'] = self.appleCoordinate.__str__()
        info['score1'] = self.score1
        info['score2'] = self.score2
        info['snake1'] = list(map(str, self.snake1.body))
        info['snake2'] = list(map(str, self.snake2.body))

        return info

    def __iter__(self):
        return GameIter(self)


class GameIter:
    def __init__(self, game: Game, timeout=1, requestTimeout=2):
        self.game = game
        self.timeout = timeout
        self.requestTimeout = requestTimeout
        self.states = {}
        self.states['metadata'] = {}
        self.states['metadata']['team1'] = {}
        self.states['metadata']['team2'] = {}
        self.stop = False

    def __iter__(self):
        return self

    def __next__(self):
        """
        Make a game iteration
        Return instance of game
        """
        if self.stop:
            raise StopIteration
        try:
            self.states[str(self.game.iterationNumber)] = self.game.get_state()
            self.game.run_one_step(timeout=self.timeout,
                                   requestTimeout=self.requestTimeout)
        except GameOver as e:
            metadata = self.states['metadata']
            metadata['winner'] = self.game.snakeWinner
            metadata['description'] = self.game.result_description
            metadata['score'] = self.game.score1, self.game.score2
            metadata['gameId'] = self.game.gameId
            metadata['result'] = self.game.result

            team1 = metadata['team1']
            team2 = metadata['team2']
            team1['name'] = self.game.bot1_runner.name
            team2['name'] = self.game.bot2_runner.name
            team1['id'] = self.game.bot1_runner.id
            team2['id'] = self.game.bot2_runner.id

            self.stop = True

    def getStates(self):
        return self.states
