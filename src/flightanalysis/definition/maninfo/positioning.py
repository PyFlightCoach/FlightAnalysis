import numpy as np
from enum import Enum
from dataclasses import dataclass
from typing import Annotated


class Orientation(Enum):
    UPRIGHT = np.pi
    INVERTED = 0


class Heading(Enum):
    RTOL = np.pi
    LTOR = 0
    OUTTOIN = 3 * np.pi / 2
    INTOOUT = np.pi / 2

    @staticmethod
    def values():
        return np.array(list(Heading.__members__.values()))

    @staticmethod
    def infer(bearing: Annotated[float, "in radians from north"]):
        def check(bearing: float, heading: Heading):
            return (np.round(np.abs(4*(bearing - heading.value)) / (2*np.pi)).astype(int) % 4)==0
            
        for head in Heading.__members__.values():
            if check(bearing, head):
                return head
        else:
            raise ValueError(f"Invalid bearing {bearing}")

    def reverse(self):
        return {
            Heading.RTOL: Heading.LTOR,
            Heading.LTOR: Heading.RTOL,
            Heading.OUTTOIN: Heading.INTOOUT,
            Heading.INTOOUT: Heading.OUTTOIN,
        }[self]


class Direction(Enum):
    UPWIND = 1
    DOWNWIND = -1
    CROSS = 0

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
        return dict(
            height=self.height.name,
            direction=self.direction.name if self.direction else "",
            orientation=self.orientation.name if self.orientation else "",
        )

    @staticmethod
    def from_dict(data):
        return BoxLocation(
            Height[data["height"]],
            Direction[data["direction"]] if len(data["direction"]) > 0 else None,
            Orientation[data["orientation"]] if len(data["orientation"]) > 0 else None,
        )
