import numpy as np
from enum import Enum
from dataclasses import dataclass
from typing import Annotated


class Orientation(Enum):
    UPRIGHT = np.pi
    INVERTED = 0


class Heading(Enum):
    LEFT = np.pi
    RIGHT = 0
    IN = np.pi / 2
    OUT = 3 * np.pi / 2

    @staticmethod
    def parse(s: str):
        match s[0].lower():
            case "l":
                return Heading.LEFT
            case "r":
                return Heading.RIGHT
            case "i":
                return Heading.IN
            case "o":
                return Heading.OUT
            case _:
                raise ValueError(f"Invalid direction {s}")

    @staticmethod
    def infer(bearing: Annotated[float, "in radians from north"]):
        
        def check(bearing: float, heading: Heading):
           return np.abs((bearing - heading.value)) % (2*np.pi) < np.pi/4 

        for head in Heading.__members__.values():
            if check(bearing, head):
                return head
        else:
            raise ValueError(f"Invalid bearing {bearing}")


    def reverse(self):
        return {
            Heading.LEFT: Heading.RIGHT,
            Heading.RIGHT: Heading.LEFT,
            Heading.IN: Heading.OUT,
            Heading.OUT: Heading.IN,
        }[self]


class Direction(Enum):
    UPWIND = 1
    DOWNWIND = -1
    CROSS = 3

    def wind_swap_heading(self, d_or_w: Heading) -> int:
        match self:
            case Direction.UPWIND:
                return d_or_w
            case Direction.DOWNWIND:
                return d_or_w.reverse()
            case Direction.CROSS:
                return d_or_w

    
    @staticmethod
    def parse(s: str):
        match s[0].lower():
            case "u":
                return Direction.UPWIND
            case "d":
                return Direction.DOWNWIND
            case "c":
                return Direction.CROSS
            case _:
                raise ValueError(f"Invalid wind {s}")


class Height(Enum):
    BTM = 0.2
    MID = 0.6
    TOP = 1.0


class Position(Enum):
    CENTRE = 0
    END = 1


@dataclass
class BoxLocation:
    height: Height
    direction: Direction = None
    orientation: Orientation = None

    def to_dict(self):
        return dict(h=self.height.name, d=self.direction.name, o=self.orientation.name)

    @staticmethod
    def from_dict(data):
        return BoxLocation(
            Height[data["h"]], Direction[data["d"]], Orientation[data["o"]]
        )
    
