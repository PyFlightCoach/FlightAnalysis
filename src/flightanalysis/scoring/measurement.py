from __future__ import annotations

from dataclasses import dataclass


import geometry as g
import numpy as np
import numpy.typing as npt
from flightdata import State

from flightanalysis.elements import Elements


@dataclass
class Measurement:
    value: npt.NDArray
    unit: str
    keys: npt.NDArray = None
    
    def __len__(self):
        return len(self.value)

    def __getitem__(self, sli):
        return Measurement(
            self.value[sli],
            self.unit,
        )

    def to_dict(self):
        return dict(
            value=list(self.value),
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
    unit: str = ""
    visor: str = ""
    
    @staticmethod
    def get_axial_direction(tp: State):
        """Proj is a vector in the axial direction for the template ref_frame (tp[0].transform)*"""
        return g.point.cross(g.PX(), tp[0].arc_centre()).unit()
    
    def __call__(self, els: Elements, fl: State, tp: State, **kwargs) -> Measurement:
        info: dict = {}
        meas = self.measure(els, fl, tp, info, **kwargs)
        return Measurement(meas, self.unit, info=info)
    
    def to_dict(self):
        return dict(
            unit=self.unit,
            measure=str(self.measure),
            visor=str(self.visor),
        )