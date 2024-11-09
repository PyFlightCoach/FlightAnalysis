from __future__ import annotations
import numpy as np
from geometry import Transformation, P0, PX
from flightdata import State
from .element import Element
from dataclasses import dataclass
from typing import ClassVar


@dataclass
class Line(Element):
    parameters: ClassVar[list[str]] = Element.parameters + "length,roll,rate".split(",")
    length: float
    roll: float = 0   

    def describe(self):
        d1 = "line" if self.roll==0 else f"{self.roll} roll"
        return f"{d1}, length = {self.length} m"

    @property
    def rate(self):
        return self.roll * self.speed / self.length

    def create_template(self, istate: State, fl: State=None) -> State:
        """construct a State representing the judging frame for this line element

        Args:
            istate (Transformation): initial position and orientation
            speed (float): speed in judging frame X axis
            simple (bool, optional): just create the first and last points of the section. Defaults to False.

        Returns:
            State: [description]
        """
        v = PX(self.speed) if istate.vel == 0 else istate.vel.scale(self.speed)
             
        return self._add_rolls(
            istate.copy(vel=v, rvel=P0()).fill(
                Element.create_time(self.length / self.speed, fl)
            ), 
            self.roll
        )

    def match_intention(self, itrans: Transformation, flown: State) -> Line:
        return self.set_parms(
            length=abs(self.length_vec(itrans, flown))[0],
            roll=np.sign(np.mean(flown.p)) * abs(self.roll),
            speed=abs(flown.vel).mean()
        )


    def copy_direction(self, other) -> Line:
        return self.set_parms(roll=abs(self.roll) * np.sign(other.roll))
