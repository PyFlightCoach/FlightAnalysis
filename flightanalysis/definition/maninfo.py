"""This file contains some Enums and classes that could be used to set up a manoeuvre, for 
example containing the line before and scaling the ManParms so that it fills the box.

WIP, very vague ideas at the moment.

"""
import numpy as np
from geometry import Point, Transformation, Euler, P0, PY
from enum import Enum
from dataclasses import dataclass, field
from typing import Tuple


class Orientation(Enum):
    DRIVEN=0
    UPRIGHT=1
    INVERTED=-1

    def roll_angle(self):
        return {
            Orientation.UPRIGHT: np.pi,
            Orientation.INVERTED: 0
        }[self]


class Direction(Enum):
    DRIVEN=0
    UPWIND=1
    DOWNWIND=2
    CROSS=3

    def get_wind(self, direction: int=1) -> int:
        return {
            Direction.UPWIND: -direction,
            Direction.DOWNWIND: direction
        }[self]

    def get_direction(self, wind: int=1) -> int:
        """return 1 for heading in +ve x direction, -1 for negative"""
        return {
            Direction.UPWIND: -wind,
            Direction.DOWNWIND: wind
        }[self]

class CrossDirection(Enum):
    IN=0
    OUT=1
    

class Height(Enum):
    BTM=1
    MID=2
    TOP=3

    def calculate(self, depth):
        top = np.tan(np.radians(60))* depth
        btm = np.tan(np.radians(15))* depth
    
        return {
            Height.BTM: btm ,
            Height.MID: 0.5 * (btm + top),
            Height.TOP: top
        }[self]
        
class Position(Enum):
    CENTRE=0
    END=1


class BoxLocation():
    def __init__(
        self, 
        h: Height, 
        d: Direction=Direction.DRIVEN, 
        o: Orientation=Orientation.DRIVEN
    ):
        self.h = h
        self.d = d
        self.o = o
    
    def initial_rotation(self, wind: int | CrossDirection):
        if self.d == Direction.CROSS:
            return Euler(
                self.o.roll_angle(),
                0.0,
                np.pi/2 if wind == CrossDirection.OUT else 3*np.pi/2
            )
        else:
            return Euler(
                self.o.roll_angle(),
                0.0,
                np.pi*(-self.d.get_direction(wind) + 1) / 2 
            )

    def to_dict(self):
        return dict(
            h = self.h.name,
            d = self.d.name,
            o = self.o.name
        )
    
    @staticmethod
    def from_dict(data):
        return BoxLocation(
            Height[data["h"]],
            Direction[data["d"]],
            Orientation[data["o"]]
        )
    

@dataclass
class ManInfo:
    name:str
    short_name:str
    k:float
    position: Position
    start: BoxLocation
    end: BoxLocation
    centre_points: list[int] = field(default_factory=lambda: []) # points that should be centered, ids correspond to the previous element
    centred_els: list[Tuple[int, float]] = field(default_factory=lambda: [])  # element ids that should be centered

    def initial_position(self, depth: float, wind: int) -> Transformation: 
        return Point(
            {
                Position.CENTRE: wind * {
                    Direction.UPWIND: depth * np.tan(np.radians(60)),
                    Direction.DOWNWIND: -depth * np.tan(np.radians(60))
                }[self.start.d],
                Position.END: 0.0
            }[self.position],
            depth,
            self.start.h.calculate(depth)
        )

    def initial_transform(self, depth: float, wind: int, cross: CrossDirection=CrossDirection.OUT) -> Transformation:
        """The default initial position. For a centre manoeuvre this is the box edge, for an end manoeuvre it is the centre

        Args:
            depth (float): _description_
            wind (int): 1 for wind in +ve x direction, -1 for -ve x direction

        Returns:
            Transformation: _description_
        """
        if self.start.d == Direction.CROSS:
            return Transformation(
                P0() if cross==CrossDirection.OUT else PY(depth*2), 
                self.start.initial_rotation(cross)
            ) 
        else:
            return Transformation(self.initial_position(depth, wind), self.start.initial_rotation(wind))


    def to_dict(self):
        return dict(
            name=self.name,
            short_name = self.short_name,
            k=self.k,
            position = self.position.name,
            start = self.start.to_dict(),
            end = self.end.to_dict(),
            centre_points = self.centre_points,
            centred_els = self.centred_els
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
            inp["centred_els"]
        )
        