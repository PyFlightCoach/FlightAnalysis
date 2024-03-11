from __future__ import annotations
import numpy as np
from geometry import Transformation, P0, PX, Time
from flightdata import State

from .element import Element, ElementError
from flightanalysis.scoring.criteria.f3a_criteria import F3A
from flightanalysis.scoring import Measurement, DownGrade, DownGrades



class Line(Element):
    parameters = Element.parameters + "length,roll,rate".split(",")

    def __init__(self, speed, length, roll=0, uid:str=None):
        super().__init__(uid, speed)
        self.length = length
        self.roll = roll
        if length <= 0:
            raise ElementError(f"Error creating {self.__repr__()}, length must be positive")
    
    @property
    def intra_scoring(self) -> DownGrades:
        _intra_scoring = DownGrades([
            DownGrade(Measurement.speed, F3A.intra.speed),
            DownGrade(Measurement.track_y, F3A.intra.track),
            DownGrade(Measurement.track_z, F3A.intra.track)
        ])

        if not self.roll == 0:
            _intra_scoring.add(DownGrade(Measurement.roll_rate, F3A.intra.roll_rate))
            _intra_scoring.add(DownGrade(Measurement.roll_angle, F3A.single.roll))
        else:
            _intra_scoring.add(DownGrade(Measurement.roll_angle, F3A.intra.roll))
        return _intra_scoring

    def describe(self):
        d1 = "line" if self.roll==0 else f"{self.roll} roll"
        return f"{d1}, length = {self.length} m"

    @property
    def rate(self):
        return self.roll * self.speed / self.length

    def create_template(self, istate: State, time: Time=None) -> State:
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
                Element.create_time(self.length / self.speed, time)
            ), 
            self.roll
        )

    def match_intention(self, itrans: Transformation, flown: State) -> Line:
        return self.set_parms(
            length=abs(self.length_vec(itrans, flown))[0],
            roll=np.sign(np.mean(flown.p)) * abs(self.roll),
            speed=abs(flown.vel).mean()
        )

    @staticmethod
    def from_roll(speed: float, rate: float, angle: float) -> Line:
        return Line(speed, rate * angle * speed, angle )

    def copy_direction(self, other) -> Line:
        return self.set_parms(roll=abs(self.roll) * np.sign(other.roll))
