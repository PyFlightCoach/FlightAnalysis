from __future__ import annotations
import numpy as np
import geometry as g
from flightdata import State
from .element import Element
from dataclasses import dataclass
from typing import ClassVar, Literal


@dataclass
class Line(Element):
    parameters: ClassVar[list[str]] = Element.parameters + "length,roll,rate".split(",")
    length: float
    roll: float = 0

    def describe(self):
        d1 = "Line" if self.roll == 0 else f"{np.degrees(self.roll):0.0f} Roll"
        return f"{d1}, Length = {self.length:0.0f} m"

    @property
    def rate(self):
        return self.roll * self.speed / self.length

    def create_template(self, istate: State, fl: State = None, freq=25, npoints: int | Literal["min"]=3) -> State:
        """construct a State representing the judging frame for this line element

        Args:
            istate (Transformation): initial position and orientation
            speed (float): speed in judging frame X axis
            simple (bool, optional): just create the first and last points of the section. Defaults to False.

        Returns:
            State: [description]
        """
        npoints = 2 if npoints=="min" else npoints
        v = g.PX(self.speed) if istate.vel == 0 else istate.vel.scale(self.speed)
        return (
            istate.copy(vel=v, rvel=g.P0())
            .fill(Element.create_time(self.length / self.speed, fl.time if fl else None, freq, npoints))
            .superimpose_rotation(g.PX(), self.roll)
        )

    def match_intention(self, itrans: g.Transformation, flown: State) -> Line:
        return self.set_parms(
            length=abs(self.length_vec(itrans, flown))[0],
            roll=np.sign(np.mean(flown.p)) * abs(self.roll),
            speed=abs(flown.vel).mean(),
        )

    def copy_direction(self, other) -> Line:
        return self.set_parms(roll=other.roll)
