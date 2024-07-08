from __future__ import annotations
import numpy as np
import geometry as g
from flightdata import State
from .element import Element
from dataclasses import dataclass
from typing import ClassVar
from flightanalysis.scoring.measurement import Measurement

@dataclass
class StallTurn(Element):
    parameters: ClassVar[list[str]] = Element.parameters + ["yaw_rate"]
    yaw_rate: float

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