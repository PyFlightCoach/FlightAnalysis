from __future__ import annotations
import numpy as np
from geometry import Transformation, PY, Time
from flightdata import State
from .element import Element
from .line import Line
from dataclasses import dataclass
from typing import ClassVar


@dataclass
class PitchBreak(Element):
    parameters: ClassVar[list[str]] = Element.parameters + "length,break_angle".split(",")
    length: float
    break_angle: float

    def create_template(self, istate: State, time: Time=None) -> State:
        return Line("pitch_break", self.speed, self.length).create_template(
            istate, 
            time
        ).superimpose_rotation(
            PY(),
            self.break_angle
        ).label(element=self.uid)

    def describe(self):
        return "pitch break"
    
    def match_intention(self, transform: Transformation, flown: State) -> PitchBreak:
        jit = flown.judging_itrans(transform)

        _speed = abs(flown.vel).mean()

        alphas = np.arctan2(flown.vel.z, flown.vel.x)

        return self.set_parms(
            speed = _speed,
            length = max(
                jit.att.inverse().transform_point(flown.pos - jit.pos).x[-1],
                5
            ) ,
            break_angle = alphas[-1]
        )
    
    def copy_direction(self, other: PitchBreak) -> PitchBreak:
        return self.set_parms(break_angle=abs(self.break_angle) * np.sign(other.break_angle))


