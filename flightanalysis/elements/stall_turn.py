from __future__ import annotations
import numpy as np
import geometry as g
from flightdata import State
from .element import Element
from flightanalysis.scoring.criteria.f3a_criteria import F3A
from flightanalysis.scoring import Measurement, DownGrade, DownGrades


class StallTurn(Element):
    parameters = Element.parameters + ["yaw_rate"]
    def __init__(self, speed:float, yaw_rate:float=3.0, uid: str=None):
        super().__init__(uid, speed)
        self.yaw_rate = yaw_rate

    @property
    def intra_scoring(self) -> DownGrades:
        def width(fl, tp):
            return Measurement.length(fl, tp, g.PY())
        def speed(fl, tp):
            return Measurement.speed(fl, tp, g.PZ(), 'world')
        def roll_angle(fl, tp):
            return Measurement.roll_angle_z(fl, tp)
        return DownGrades([
            DownGrade(roll_angle, F3A.intra.roll),
            DownGrade(width, F3A.intra.stallturn_width),
            DownGrade(speed, F3A.intra.stallturn_speed),
        ])

    def describe(self):
        return f"stallturn, yaw rate = {self.yaw_rate}"

    def create_template(self, istate: State, time: g.Time=None) -> State:
        return self._add_rolls(
            istate.copy(rvel=g.P0() ,vel=g.P0()).fill( 
                Element.create_time(np.pi / abs(self.yaw_rate), time)
            ).superimpose_rotation(
                g.PZ(), 
                np.sign(self.yaw_rate) * np.pi
            ), 
            0.0
        )

    def match_axis_rate(self, yaw_rate: float) -> StallTurn:
        return self.set_parms(yaw_rate=yaw_rate)

    def match_intention(self, transform: g.Transformation, flown: State) -> StallTurn:
        return self.set_parms(
            yaw_rate=flown.data.r[flown.data.r.abs().idxmax()]
        )

    def copy_direction(self, other) -> StallTurn:
        return self.set_parms(
            yaw_rate=abs(self.yaw_rate) * np.sign(other.yaw_rate)
        )
    
    def yaw_rate_visibility(self, st: State):
        return Measurement._vector_vis(
            st.att.transform_point(g.PZ(1)).mean(), 
            st.pos.mean()
        )