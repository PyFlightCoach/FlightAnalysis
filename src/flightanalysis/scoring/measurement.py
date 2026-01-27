from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Tuple

import geometry as g
import numpy as np
import numpy.typing as npt
from flightdata import State

from flightanalysis.elements import Elements
from flightanalysis.base.ref_funcs import RefFunc


@dataclass
class Measurement:
    value: npt.NDArray
    direction: g.Point
    unit: str
    keys: npt.NDArray = None

    def __len__(self):
        return len(self.value)

    def __getitem__(self, sli):
        return Measurement(
            self.value[sli],
            self.direction[sli],
            self.unit,
        )

    def to_dict(self):
        return dict(
            value=list(self.value),
            direction=self.direction.to_dicts(),
            unit=self.unit,
            keys=list(self.keys) if self.keys is not None else None,
        )

    def __repr__(self):
        if len(self.value) == 1:
            return f"Measurement({self.value}, unit={self.unit})"
        else:
            return f"Measurement(len={len(self)}, unit={self.unit})"

    @staticmethod
    def from_dict(data: dict) -> Measurement:
        return Measurement(
            np.array(data["value"]),
            g.Point.from_dicts(data["direction"]),
            data["unit"],
            np.array(data["keys"])
            if "keys" in data and data["keys"] is not None
            else None,
        )

    @staticmethod
    def ratio(vs, expected):
        avs, aex = np.abs(vs), np.abs(expected)

        nom = np.maximum(avs, aex)
        denom = np.minimum(avs, aex)
        denom = np.maximum(denom, nom / 10)

        with np.errstate(divide="ignore", invalid="ignore"):
            res = ((avs > aex) * 2 - 1) * (nom / denom - 1)

        res[vs * expected < 0] = -10

        return np.nan_to_num(res, 0)


@dataclass
class Measure:
    name: str
    measure: Callable[[Elements, State, State], Tuple[g.Point, npt.NDArray]]
    visor: Callable[[Elements, State, State, g.Point], npt.NDArray]
    unit: str = ""

    @staticmethod
    def get_axial_direction(tp: State):
        """Proj is a vector in the axial direction for the template ref_frame (tp[0].transform)*"""
        return g.point.cross(g.PX(), tp[0].arc_centre()).unit()

    def __call__(self, els: Elements, fl: State, tp: State, **kwargs) -> Measurement:
        return Measurement(*self.measure(els, fl, tp, **kwargs),self.unit)

    @property
    def __name__(self):
        return self.name