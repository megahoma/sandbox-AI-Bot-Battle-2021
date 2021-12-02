Snake bot for tournament [AI Bot Battles](http://aicup.mf.grsu.by)
====

# Local testing 

## 1. Configuration

+ Config file is `src/constants.py`

## 2. Test game between 2 bots
```console
$ python playGame.py --show <delay in seconds> --output <path to json output file> <path to bot1> <path to bot2> 
```
+ Example 
```console
$ python playGame.py --show 0.1 aibb2021_snake_bot.py enemy_bot.py
```

# Getting started with Snake-bot

In order to start programming your bot, first, you need to import `IBot` class from the `src.bot` module.

```python
from src.bot import IBot
```

Then you need to create your own class `Bot` inherited from `IBot` and create a constructor in the following way to initialize your bot properly.

```python
class Bot(IBot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
```

The constructor may be extended with additional functionality. E.g. you can initialize there some initial state of your bot.

It is assumed that your class will implement the following method:

```python
def chooseDirection(self, snake, opponent, mazeSize, apple)
```

It will be called on every game iteration by the checker. The method must plan the next step of the snake based on the following information about the game field:

  * `snake` is an object of the class `Snake` from `src.snake` module
  * `opponent` is an object of the class `Snake` from `src.snake` module
  * `mazeSize` is a tuple (an object of the class `src.geometry.Coordinate`) which contains the height and width of the game field (for IOAI tournament the field size will 14 by 14).
  * `apple` is a tuple (`src.geometry.Coordinate`) with coordinates of the apple: `apple.x` and `apple.y`.

The method must return the direction the snake must move in on the next step. The direction must be one of the following objects: `src.geometry.DOWN`, `src.geometry.UP`, `src.geometry.LEFT`, `src.geometry.RIGHT`.

The checker assumes that your method does not take more than 1 second to perform the next . If the execution time of the method exceeds 1 second, the bot loses the game. So, if your bot is doing heavy calculations you need to write a code that manage the execution time to return from the method in a proper moment.

Here is an example of a bot that makes only 3 steps and finish the game.

```python
from src.bot import IBot
from src.geometry import Direction, Coordinate, RIGHT
from src.snake import Snake

STEPS_TO_MOVE = 3

class Bot(IBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.i = 0

    def chooseDirection(self, snake: Snake, opponent: Snake, mazeSize: Coordinate, apple: Coordinate) -> Direction:
        self.i += 1

        if self.i > STEPS_TO_MOVE:
            head = snake.body[0]
            firstBodyElement = snake.body[1]
            directionToDeath = head.getDirection(firstBodyElement)

            return directionToDeath
        else:
            return RIGHT
```

## Conditions for the end of the game

In the beginning, all two snakes are alive.

The game ends when **at least one** snake is dead

A snake considered **dead** if at least one of the following conditions is true:

1. The number game iterations (moves) exceeded 500
2. Evaluation of `chooseDirection` of a snake exceeded 1 second
3. During execution of `chooseDirection` of a snake, an exception was raised.
4. Method `chooseDirection` of a snake returned neither UP, DOWN, LEFT, nor RIGHT (variables from `src.geometry`)
5. A snake went out of the field (head of snake not in 14x14 box)
6. The head of a snake is in the same cell as the **body** of **this** snake
7. The head of a snake is in the same cell as the **body** of **opponent** snake
8. The head of a snake is in the same cell as the **head** of **opponent** snake

If at the end:
+ there is live snake, then this snake is the winner
+ both snakes are dead, then if they have different lentgh (they ate diffent amount of apples) then the snake that is longer is the winner

Otherwise, we call it **draw**

## Documentation

---
class **Direction**

Represents direction in changing current coordinate.

```python
from src.geometry import Direction
```

+ there are **predefined directions**: `UP`, `DOWN`, `RIGHT` and `LEFT`
+ there are list of all predefined directions: `directions`

```python
>>> from src.geometry import UP, LEFT, DOWN, RIGHT, directions
>>> directions == [UP, DOWN, RIGHT, LEFT]
True
```

You should return exactly one of the **predefined directions** in your `chooseDirection` method

---
class **Coordinate**

2D point with integer values

```python
from src.geometry import Coordinate
coord = Coordinate(3, 14)
```

Method:
    
* `moveTo(direction)` - returns new coordinate, that has moved in this direction
```python 
>>> coord = Coordinate(3, 14)
>>> coord = coord.moveTo(UP)
>>> coord == Coordinate(3, 15)
True
```

* `getDirection(otherCoordinate)` - returns predefined direction of vector between two points. if there is no such predefined direction, returns None
```python 
>>> Coordinate(3,14).getDirection(Coordinate(3,15))
UP
>>> Coordinate(3,14).getDirection(Coordinate(4,14))
RIGHT
>>> Coordinate(3,14).getDirection(Coordinate(4,15))
>>> 
```

* `inBounds(mazeSize)` - returns true if point in maze, false otherwise

```python 
>>> coord = Coordinate(4,4)
>>> coord.inBounds(Coordinate(4,5))
False
>>> coord.inBounds(Coordinate(5,5))
True
```

* `getDistance(otherCoordinate)` - returns [Manhattan distance](https://computervision.fandom.com/wiki/Manhattan_distance) between two coordinate
```python 
>>> Coordinate(1,1).getDistance(Coordinate(5,4))
7
```
* `getMathDistance(otherCoordinate)` - returns [Euclidean distance](https://en.wikipedia.org/wiki/Euclidean_distance) between two points (coordinate)
```python
>>> Coordinate(1,1).getMathDistance(Coordinate(10,10))
5
```
* `clone() - creates and returns clone of current Coordinate`
---
class **Snake**

```python
from src.snake import Snake
```

    
Attributes:

* `body` - list of `src.geometry.Coordinate` objects that represents body of the snake
* `elements` - is the same as body, but it is a set not list
* `head` - first element of body

Methods:

* `clone()` - returns clone of current snake, `src.snake.Snake` object
* `moveTo(direction, grow)` - moves the snake to the direction, changes body and elements. Returns true if snake is alive after this move, false otherwise
    * paraments:
        * direction (`src.geometry.Direction`) - move in this direction
        * grow (bool) - if true than increase length by one after move
* `headCollidesWith(otherSnake)` - returns true if the head of the current snake is in the body of otherSnake 
    * paraments:
        * otherSnake (`src.snake.Snake`) - snake for collision check

When forming the language pack, the code used in the competitions of the Olympiad in AI at Innopolis University (2021) was used
