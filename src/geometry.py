from typing import Union


class Direction:
    """
    Represents direction in changing current coordinate (vector)
    """
    def __init__(self, dx: int, dy: int, name: str = ""):
        self.dx = dx
        self.dy = dy
        self.name = name
        self.v = Coordinate(dx, dy)
    
    def __str__(self):
        for d in directions:
            if self == d:
                return d.name
        
        return f"{self.dx} {self.dy}"

    def __eq__(self, other):
        if isinstance(other, Direction):
            return self.v == other.v
        else:
            return False


    def __repr__(self):
        return self.__str__()

class Coordinate:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    
    def __add__(self, other_coordinate):
        return Coordinate(self.x + other_coordinate.x, self.y + other_coordinate.y)
    
    def moveTo(self, d: Direction):
        """
        Move coordinate in given direction
        """
        return self + d.v
    
    def getDirection(self, other) -> Union[Direction, None]:
        """
        Returns direction of given vector

        TODO: looks like useless method. Delete?
        """
        vector = Coordinate(other.x - self.x, other.y - self.y)
        for direction in directions:
            if (direction.dx == vector.x and direction.dy == vector.y):
                return direction
        return None
    
    def inBounds(self, mazeSize) -> bool:
        """
        Return true if point in maze
        """
        return self.x >= 0 and self.y >= 0 and self.x < mazeSize.x and self.y < mazeSize.y
    
    def __eq__(self, otherCoordinate) -> bool:
        if isinstance(otherCoordinate, Coordinate):
            return self.x == otherCoordinate.x and self.y == otherCoordinate.y
        else:
            return False
    
    def __mod__(self, otherCoordinate):
        if not isinstance(otherCoordinate, Coordinate):
            raise ValueError(f"Left argument of mod should be Coordinate")
        return Coordinate(self.x % otherCoordinate.x, self.y % otherCoordinate.y)

    def compareTo(self, otherCoordinate) -> int:
        """
        Compares two points in integer value

        TODO: looks like useless method. Delete?
        """
        dx = self.x - otherCoordinate.x
        dy = self.y - otherCoordinate.y
        return dx if dx != 0 else dy
    
    def getDistance(self, otherCoordinate):
        dx = self.x - otherCoordinate.x
        dy = self.y - otherCoordinate.y
        return abs(dx) + abs(dy)

    def getMathDistance(self, otherCoordinate) -> float:
        return ((self.x - otherCoordinate.x) ** 2 + (self.y - otherCoordinate.y)**2)**(1/2)

    def __str__(self):
        return f"{self.x} {self.y}"
    
    def __hash__(self):
        return hash(str(self.x) + str(self.y))
    
    def clone(self):
        return Coordinate(self.x, self.y)

UP = Direction(0, 1, "UP")
DOWN = Direction(0, -1, "DOWN")
RIGHT = Direction(1, 0, "RIGHT")
LEFT = Direction(-1, 0, "LEFT")

directions = [UP, DOWN, RIGHT, LEFT]
