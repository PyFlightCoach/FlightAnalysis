from __future__ import annotations
import numpy as np
from geometry import Transformation, PY, Time
from flightdata import State
from .element import Element
from .line import Line
from dataclasses import dataclass
from typing import ClassVar

@dataclass
class Recovery(Element):
    parameters: ClassVar[list[str]] = Element.parameters + ["length"]
    length: float

    def create_template(self, istate: State, time: Time=None) -> State:
        return Line("recovery" ,self.speed, self.length, 0).create_template(
            istate, 
            time
        ).superimpose_rotation(
            PY(),
            -np.arctan2(istate.vel.z, istate.vel.x)[-1]
        ).label(element=self.uid)

    def describe(self):
        return "recovery"

    def match_intention(self, transform: Transformation, flown: State) -> Recovery:
        jit = flown.judging_itrans(transform)
        return self.set_parms(
            length=max(jit.att.inverse().transform_point(flown.pos - jit.pos).x[-1], 5),
            speed=abs(flown.vel).mean()
        )
    
    def copy_direction(self, other: Recovery) -> Recovery:
        return self.set_parms()
