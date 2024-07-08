from __future__ import annotations
import numpy as np
from geometry import Transformation, PX, PY, Time
from flightdata import State
from .element import Element
from .loop import Loop
from dataclasses import dataclass
from typing import ClassVar


@dataclass
class NoseDrop(Element):
    """A nose drop is used for spin entries. It consists of a loop to a vertical downline, with an integrated
    pitch rotation in the opposite direction to the loops pitch rotation so that the body axis finishes at
    break_angle off the vertical line"""
    parameters: ClassVar[list[str]] = Element.parameters + "radius,break_angle".split(",")
    radius: float
    break_angle: float

    def create_template(self, istate: State, time: Time=None) -> State:
        _inverted = 1 if istate.transform.rotation.is_inverted()[0] else -1
        
        alpha =  np.arctan2(istate.vel.z, istate.vel.x)[0]

        return Loop("nose_drop", self.speed, 0.5*np.pi*_inverted, self.radius, 0, 0).create_template(
            istate, time
        ).superimpose_rotation(
            PY(), 
            -alpha - abs(self.break_angle) * _inverted
        ).label(element=self.uid)
    
    def describe(self):
        return "nose drop"

    def match_intention(self, transform: Transformation, flown: State) -> NoseDrop:
        _inverted = 1 if transform.att.is_inverted()[0] else -1
        _speed = abs(flown.vel).mean()

        loop = Loop("nose_drop",_speed, 0.5*np.pi*_inverted, self.radius, 0, 0).match_intention(
            transform, flown
        )

        return self.set_parms(
            speed = _speed,
            radius = loop.radius,
            break_angle = self.break_angle,#abs(np.arctan2(flown.vel.z, flown.vel.x)[-1])
        )

    def copy_direction(self, other: NoseDrop) -> NoseDrop:
        return self.set_parms(break_angle=abs(self.break_angle) * np.sign(other.break_angle))

