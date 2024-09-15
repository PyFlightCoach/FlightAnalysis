"""This file contains some Enums and classes that could be used to set up a manoeuvre, for
example containing the line before and scaling the ManParms so that it fills the box.

WIP, very vague ideas at the moment.

"""

import numpy as np
from geometry import Point, Transformation, Euler
from enum import Enum
from dataclasses import dataclass, field
from typing import Tuple, Annotated


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
    def infer(heading: Annotated[float, "in radians from north"]):
        if (heading > 2 * np.pi) | (heading < 0):
            raise ValueError(f"Invalid heading {heading}")
        if (heading < np.pi / 4) | (heading > 7 * np.pi / 4):
            return Heading.IN
        elif (heading < 3 * np.pi / 4) & (heading > np.pi / 4):
            return Heading.RIGHT
        elif (heading < 5 * np.pi / 4) | (heading > 3 * np.pi / 4):
            return Heading.OUT
        else:
            return Heading.LEFT

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

    def get_wind(self, direction: int = 1) -> int:
        return {Direction.UPWIND: -direction, Direction.DOWNWIND: direction}[self]

    def get_direction(self, wind: int = 1) -> int:
        """return 1 for heading in +ve x direction, -1 for negative"""
        return {Direction.UPWIND: -wind, Direction.DOWNWIND: wind}[self]

    def infer(self, direction: int):
        return self.get_direction(self.get_wind(direction))

    @staticmethod
    def parse(s: str):
        match s[0].lower():
            case "u":
                return Direction.UPWIND
            case "d":
                return Direction.DOWNWIND
            case "a":
                return Direction.ANY
            case "c":
                return Direction.CROSS
            case _:
                raise ValueError(f"Invalid wind {s}")


class Height(Enum):
    BTM = 1
    MID = 2
    TOP = 3

    def calculate(self, depth):
        top = np.tan(np.radians(60)) * depth
        btm = np.tan(np.radians(15)) * depth

        return {Height.BTM: btm, Height.MID: 0.5 * (btm + top), Height.TOP: top}[self]


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

    def guess(self, depth: float, wind: Heading) -> Transformation:
        assert wind in [
            Heading.RIGHT,
            Heading.LEFT,
        ], "Wind must be either Heading.RIGHT or Heading.LEFT"

        heading = wind.reverse()
        return Point(
            x={
                Position.CENTRE: {
                    Heading.IN: 0.0,
                    Heading.OUT: 0.0,
                    Heading.LEFT: np.tan(np.radians(60)) * depth,
                    Heading.RIGHT: -np.tan(np.radians(60)) * depth,
                }[heading],
                Position.END: 0.0,
            }[self.position],
            y={
                Heading.IN: 2 * depth,
                Heading.OUT: 0,
                Heading.LEFT: depth,
                Heading.RIGHT: depth,
            }[heading],
            z=self.start.height.calculate(depth),
        )


@dataclass
class ManInfo:
    name: str
    short_name: str
    k: float
    position: Position
    start: BoxLocation
    end: BoxLocation
    centre_points: list[int] = field(
        default_factory=lambda: []
    )  # points that should be centered, ids correspond to the previous element
    centred_els: list[Tuple[int, float]] = field(
        default_factory=lambda: []
    )  # element ids that should be centered

    def initial_transform(self, depth: float, heading: Heading) -> Transformation:
        """The default initial transformation.
        For a centre manoeuvre this is the box edge, for an end manoeuvre it is the centre

        Args:
            depth (float): y distance from pilot
            heading (Heading): direction of flight

        Returns:
            Transformation: _description_
        """
        return Transformation(
            self.initial_position(depth, heading),
            Euler(self.start.orientation.value, 0, self.start.direction.value),
        )

    def to_dict(self):
        return dict(
            name=self.name,
            short_name=self.short_name,
            k=self.k,
            position=self.position.name,
            start=self.start.to_dict(),
            end=self.end.to_dict(),
            centre_points=self.centre_points,
            centred_els=self.centred_els,
        )

    @staticmethod
    def from_dict(inp: dict):
        return ManInfo(
            inp["name"],
            inp["short_name"],
            inp["k"],
            Position[inp["position"]],
            BoxLocation.from_dict(inp["start"]),
            BoxLocation.from_dict(inp["end"]),
            inp["centre_points"],
            inp["centred_els"],
        )
