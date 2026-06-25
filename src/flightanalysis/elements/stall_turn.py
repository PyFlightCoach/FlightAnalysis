from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Literal

import geometry as g
import numpy as np
from flightdata import State

from .element import Element


@dataclass
class StallTurn(Element):
    parameters: ClassVar[list[str]] = Element.parameters + ["yaw_rate"]
    yaw_rate: float

    def describe(self):
        return f"stallturn, yaw rate = {self.yaw_rate}"

    def create_template(
        self,
        istate: State,
        fl: State = None,
        freq=25,
        npoints: int | Literal["min"] = 3,
    ) -> State:
        return (
            istate.copy(rvel=g.P0(), vel=g.P0())
            .fill(
                Element.create_time(
                    np.pi / abs(self.yaw_rate),
                    fl.time if fl else None,
                    freq,
                    2 if npoints == "min" else npoints,
                )
            )
            .superimpose_rotation(g.PZ(), np.sign(self.yaw_rate) * np.pi)
        )

    def match_axis_rate(self, yaw_rate: float) -> StallTurn:
        return self.set_parms(yaw_rate=yaw_rate)

    def match_intention(self, transform: g.Transformation, flown: State) -> StallTurn:
        return self.set_parms(yaw_rate=flown.data.r[flown.data.r.abs().idxmax()])

    def copy_direction(self, other) -> StallTurn:
        return self.set_parms(yaw_rate=abs(self.yaw_rate) * np.sign(other.yaw_rate))

    @property
    def axis(self) -> g.Point:
        """return the axis of rotation for this element in world coordinates"""
        return g.PZ()