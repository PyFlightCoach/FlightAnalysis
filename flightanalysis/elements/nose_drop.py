from __future__ import annotations
import numpy as np
from geometry import Transformation, PX, PY, PZ, Time, Point
from flightdata import State
from .element import Element
from .loop import Loop
from flightanalysis.scoring.criteria.f3a_criteria import F3A
from flightanalysis.scoring import Measurement, DownGrade, DownGrades


class NoseDrop(Element):
    """A nose drop is used for spin entries. It consists of a loop to a vertical downline, with an integrated
    pitch rotation in the opposite direction to the loops pitch rotation so that the body axis finishes at
    break_angle off the vertical line"""
    parameters = Element.parameters + "radius,break_angle".split(",")
    def __init__(self, speed: float, radius: float, break_angle: float, uid: str=None):
        super().__init__(uid, speed)
        self.radius=radius
        self.break_angle = break_angle

    @property
    def intra_scoring(self) -> DownGrades:
        '''TODO check alpha is increasing'''
        def length(fl, tp):
            return Measurement.length(fl, tp, PX())
        def roll_angle(fl, tp):
            return Measurement.roll_angle_proj(fl, tp, PY())
        
        return DownGrades([
            DownGrade(length, F3A.intra.spin_entry_length),
            DownGrade(roll_angle, F3A.intra.roll)
        ])

    def create_template(self, istate: State, time: Time=None) -> State:
        _inverted = 1 if istate.transform.rotation.is_inverted()[0] else -1
        
        alpha =  np.arctan2(istate.vel.z, istate.vel.x)[0]

        return Loop(self.speed, self.radius, 0.5*np.pi*_inverted).create_template(
            istate, time
        ).superimpose_rotation(
            PY(), 
            -alpha - abs(self.break_angle) * _inverted
        ).label(element=self.uid)
    
    def describe(self):
        return "nose drop"

    def match_intention(self, transform: Transformation, flown: State) -> NoseDrop:
        _inverted = 1 if transform.rotation.is_inverted()[0] else -1
        _speed = abs(flown.vel).mean()

        loop = Loop(_speed, self.radius, 0.5*np.pi*_inverted).match_intention(
            transform, flown
        )

        return self.set_parms(
            speed = _speed,
            radius = loop.radius,
            break_angle = self.break_angle,#abs(np.arctan2(flown.vel.z, flown.vel.x)[-1])
        )

    

    def copy_direction(self, other: NoseDrop) -> NoseDrop:
        return self.set_parms(break_angle=abs(self.break_angle) * np.sign(other.break_angle))


    @property
    def exit_scoring(self) -> DownGrades:
        return DownGrades()
