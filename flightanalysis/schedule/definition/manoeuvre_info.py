"""This file contains some Enums and classes that could be used to set up a manoeuvre, for 
example containing the line before and scaling the ManParms so that it fills the box.

WIP, very vague ideas at the moment.

"""
import numpy as np
from geometry import Point, Transformation, Euler
from enum import Enum

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
    
    def initial_rotation(self, wind):
        return Euler(
            self.o.roll_angle(),
            0.0,
            np.pi*(-self.d.get_direction(wind) + 1) / 2 
        )

class ManInfo:
    def __init__(
        self, 
        name:str, 
        short_name:str, 
        k:float, 
        position: Position,
        start: BoxLocation, 
        end: BoxLocation,
    ):

        self.name = name
        self.short_name = short_name
        self.k = k
        self.position=position
        self.start = start
        self.end = end


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

    def initial_transform(self, depth, wind) -> Transformation:
        """The default initial position. For a centre manoeuvre this is the box edge, for an end manoeuvre it is the centre

        Args:
            depth (float): _description_
            wind (int): 1 for wind in +ve x direction, -1 for -ve x direction

        Returns:
            Transformation: _description_
        """
        return Transformation(self.initial_position(depth, wind), self.start.initial_rotation(wind))


    